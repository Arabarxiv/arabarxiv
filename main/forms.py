from django import forms 

from django.contrib.auth.forms import UserCreationForm, UsernameField, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget
from django.utils.safestring import mark_safe

from .models import Post, TranslationPost, COUNTRY_CHOICES, Comment, NewsletterSubscriber, Category, MainCategory

from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

class GroupedCategoryWidget(forms.Select):
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        
        css_class = attrs.get("class", "")
        if "form-control" not in css_class:
            css_class = f"form-control {css_class}".strip()
        
       
        main_categories = MainCategory.objects.prefetch_related('categories').all()
        
        
        output = [f'<select name="{name}" id="{attrs.get("id", name)}" class="{css_class}">']   
        output.append('<option value="">---------</option>')
        
        for main_cat in main_categories:
            
            output.append(f'<option disabled style="font-weight: bold; background-color: #f8f9fa; color: #495057;">{main_cat.name}</option>')
            
           
            subcategories = main_cat.categories.all()
            if subcategories.exists():
                for sub_cat in subcategories:
                    selected = 'selected' if str(sub_cat.id) == str(value) else ''
                    output.append(f'<option value="{sub_cat.id}" {selected} style="padding-left: 20px;">{sub_cat.name}</option>')
            else:
                # If no subcategories, add a placeholder
                output.append('<option disabled style="padding-left: 20px; color: #6c757d; font-style: italic;">لا توجد تصنيفات فرعية</option>')
        
        output.append('</select>')
        return mark_safe('\n'.join(output))


class MultipleCategoryWidget(forms.SelectMultiple):
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        css_class = attrs.get("class", "")
        if "form-control" not in css_class:
            css_class = f"form-control {css_class}".strip()
        
        # Convert value to list if it's not already
        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]
        
        # Convert to strings for comparison
        value = [str(v) for v in value]
        
        main_categories = MainCategory.objects.prefetch_related('categories').all()
        
        output = [f'<select name="{name}" id="{attrs.get("id", name)}" class="{css_class}" multiple>']   
        
        for main_cat in main_categories:
            output.append(f'<option disabled style="font-weight: bold; background-color: #f8f9fa; color: #495057;">{main_cat.name}</option>')
            
            subcategories = main_cat.categories.all()
            if subcategories.exists():
                for sub_cat in subcategories:
                    selected = 'selected' if str(sub_cat.id) in value else ''
                    output.append(f'<option value="{sub_cat.id}" {selected} style="padding-left: 20px;">{sub_cat.name}</option>')
            else:
                output.append('<option disabled style="padding-left: 20px; color: #6c757d; font-style: italic;">لا توجد تصنيفات فرعية</option>')
        
        output.append('</select>')
        return mark_safe('\n'.join(output))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='البريد الإلكتروني')

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'اسم المستخدم'
        self.fields['first_name'].label     = 'الإسم'
        self.fields['last_name'].label = 'اللقب'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].label = 'تأكيد كلمة المرور'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("يوجد مستخدم بالفعل بهذا البريد الإلكتروني.")
        return email

class ModifyNameForm(forms.Form):
    first_name = forms.CharField(label='الاسم الأول', max_length=30, required=True)
    last_name = forms.CharField(label='اللقب', max_length=30, required=True)

class ModifyEmailForm(forms.Form):
    email = forms.EmailField(label='البريد الإلكتروني', required=True)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ModifyEmailForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise ValidationError("يوجد مستخدم بالفعل بهذا البريد الإلكتروني.")
        return email

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='البريد الإلكتروني',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

class BibTexForm(forms.Form):
    bibtex_input = forms.CharField(widget=forms.Textarea, label='أدخل مدخل BibTeX الخاص بك هنا')


class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='اختر التصنيف',
        help_text='التصنيف إجباري',
        widget=GroupedCategoryWidget(),
        required=True
    )
    
    second_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='إضافة تصنيف',
        help_text='تصنيف إضافي (اختياري)',
        widget=GroupedCategoryWidget(),
        required=False
    )
    
    # Hidden field for author ordering
    author_order = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text='JSON string of author IDs in order'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'description', 'keywords', 'external_doi', 'pdf']
        labels = {
            'title': 'عنوان المقال',
            'description': 'ملخص',
            'keywords': 'الكلمات الدالة',
            'external_doi': 'DOI',
            'pdf': 'الملف PDF',
        }
        help_texts = {
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)
        
        # Set initial author order if this is an existing post
        if self.instance and self.instance.pk:
            authors = self.instance.get_ordered_authors()
            if authors.exists():
                author_ids = [str(author.user.id) for author in authors]
                self.fields['author_order'].initial = ','.join(author_ids)
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        second_category = cleaned_data.get('second_category')
        
        if category and second_category and category == second_category:
            raise forms.ValidationError("لا يمكن اختيار نفس التصنيف مرتين.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            # Set the current user as the author
            instance.author = self.user
        
        if commit:
            # Save the instance first to get an ID
            instance.save()
            self.save_m2m()  # This will save the many-to-many relationships
            
            # Now add categories after the instance has been saved
            category = self.cleaned_data.get('category')
            second_category = self.cleaned_data.get('second_category')
            
            # Clear existing categories first
            instance.categories.clear()
            
            if category:
                instance.categories.add(category)
            if second_category and second_category != category:
                instance.categories.add(second_category)
            
            # Handle author ordering
            author_order = self.cleaned_data.get('author_order', '')
            if author_order:
                author_ids = [int(id.strip()) for id in author_order.split(',') if id.strip()]
                
                # Clear existing author relationships
                instance.post_authors.all().delete()
                
                # Add authors in the specified order
                for order, user_id in enumerate(author_ids, 1):
                    try:
                        user = User.objects.get(id=user_id)
                        is_creator = (user == self.user)
                        instance.add_author(user, order=order, is_creator=is_creator)
                    except User.DoesNotExist:
                        pass
            else:
                # Default: add current user as first author
                instance.add_author(self.user, order=1, is_creator=True)
            
            # Update the authors string field for backward compatibility
            instance.authors = instance.get_authors_string()
            instance.save(update_fields=['authors'])
            
            # Generate comprehensive meaningful ID after categories are added
            if not instance.meaningful_id and instance.categories.exists():
                meaningful_id = instance.generate_meaningful_id()
                if meaningful_id:
                    instance.meaningful_id = meaningful_id
                    instance.save(update_fields=['meaningful_id'])
        
        return instance

class TranslationPostForm(forms.ModelForm):
    original_author = forms.CharField(
        label='المؤلف الأصلي',
        max_length=400,
        required=True,
        help_text='أدخل اسم المؤلف الأصلي للمقال'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='اختر التصنيف',
        help_text='التصنيف إجباري',
        widget=GroupedCategoryWidget(),
        required=True
    )
    
    second_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='إضافة تصنيف',
        help_text='تصنيف إضافي (اختياري)',
        widget=GroupedCategoryWidget(),
        required=False
    )
    
    class Meta:
        model = TranslationPost
        fields = ['title', 'description', 'keywords', 'external_doi', 'pdf']
        labels = {
            'title': 'عنوان المقال',
            'description': 'ملخص',
            'keywords': 'الكلمات الدالة',
            'external_doi': 'DOI',
            'pdf': 'الملف PDF',
        }
        help_texts = {
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TranslationPostForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        second_category = cleaned_data.get('second_category')
        
        if category and second_category and category == second_category:
            raise forms.ValidationError("لا يمكن اختيار نفس التصنيف مرتين.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            # Set the current user as the author (translator)
            instance.author = self.user
            # Set the original author in the authors field
            instance.authors = self.cleaned_data.get('original_author', '')
            # Set the current user as the translator
            instance.translator = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        
        if commit:
            # Save the instance first to get an ID
            instance.save()
            self.save_m2m()  # This will save the many-to-many relationships
            
            # Now add categories after the instance has been saved
            category = self.cleaned_data.get('category')
            second_category = self.cleaned_data.get('second_category')
            
            # Clear existing categories first
            instance.categories.clear()
            
            if category:
                instance.categories.add(category)
            if second_category and second_category != category:
                instance.categories.add(second_category)
            
            # Generate comprehensive meaningful ID after categories are added
            if not instance.meaningful_id and instance.categories.exists():
                meaningful_id = instance.generate_meaningful_id()
                if meaningful_id:
                    instance.meaningful_id = meaningful_id
                    instance.save(update_fields=['meaningful_id'])
        
        return instance

class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(CustomLoginForm, self).__init__(request=request, *args, **kwargs)
        self.fields['username'].label = 'اسم المستخدم'
        self.fields['password'].label = 'كلمة المرور'

from .models import UserProfile
class ModifyAffiliationForm(forms.Form):
    affiliation = forms.CharField(label='الانتماء', max_length=255)

# TODO: Add Arabic translations for country names
class ModifyCountry(forms.Form):
    #country_choices = [(code, name) for code, name in list(countries)]
    #country = forms.ChoiceField(
    #    label="الدولة", 
    #    choices=country_choices,  # Specify the translated default choice
    #    widget=forms.Select(attrs={'class': 'form-control'})
    #)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False, label='الدولة')
    
from .models import Category 
class ModifyMainCategoryForm(forms.Form):
    main_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='اختر تصنيفًا رئيسيًا',
        widget=GroupedCategoryWidget(attrs={'class': 'form-control'})
    )
    

class ModifyCareerForm(forms.Form):
    career = forms.CharField(label='المهنة', max_length=255)

class ModifyWebsiteForm(forms.Form):
    website = forms.CharField(label='الموقع الإلكتروني', max_length=255)

class ModifyWhoAmIForm(forms.Form):
    who_am_i = forms.CharField(
        label='من أنا',
        widget=forms.Textarea(attrs={
            'rows': 8, 
            'cols': 60,
            'placeholder': 'اكتب ملخصاً مختصراً عن نفسك كباحث...',
            'style': 'max-width: 100%; resize: vertical;'
        }),
        required=False,
        help_text='اكتب ملخصاً مختصراً عن خلفيتك العلمية ومجالات اهتمامك البحثية'
    )


from .models import KeywordTranslation
class KeywordTranslationForm(forms.ModelForm):
    class Meta:
        model = KeywordTranslation
        fields = ['category', 'english_keyword', 'arabic_translation']

        labels = {
            'category': 'التصنيف',
            "english_keyword": "بالإنجليزية", 
            "arabic_translation": "بالعربية", 
        }
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'اختر التصنيف'
            }),
            'english_keyword': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل المصطلح بالإنجليزية'
            }),
            'arabic_translation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الترجمة بالعربية'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'التعليق',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب تعليقك هنا...'
            })
        }

class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']
        labels = {
            'email': 'البريد الإلكتروني',
            'name': 'الاسم (اختياري)',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل بريدك الإلكتروني'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسمك (اختياري)'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise ValidationError("هذا البريد الإلكتروني مشترك بالفعل في النشرة الإخبارية.")
        return email