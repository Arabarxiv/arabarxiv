from django import forms 

from django.contrib.auth.forms import UserCreationForm, UsernameField, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from .models import Post, TranslationPost, COUNTRY_CHOICES, Comment, NewsletterSubscriber

from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

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
    class Meta:
        model = Post
        fields = ['title', 'description', 'keywords', 'category', 'external_doi', 'pdf']
        labels = {
            'title': 'عنوان المقال',
            'description': 'ملخص',
            'keywords': 'الكلمات الدالة',
            'category': 'التصنيف',
            'external_doi': 'DOI',
            'pdf': 'الملف PDF',
        }
        help_texts = {
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            # Set the current user as the author
            instance.author = self.user
        
        if commit:
            instance.save()
        return instance

class TranslationPostForm(forms.ModelForm):
    original_author = forms.CharField(
        label='المؤلف الأصلي',
        max_length=400,
        required=True,
        help_text='أدخل اسم المؤلف الأصلي للمقال'
    )
    
    class Meta:
        model = TranslationPost
        fields = ['title', 'description', 'keywords', 'category', 'external_doi', 'pdf']
        labels = {
            'title': 'عنوان المقال',
            'description': 'ملخص',
            'keywords': 'الكلمات الدالة',
            'category': 'التصنيف',
            'external_doi': 'DOI',
            'pdf': 'الملف PDF',
        }
        help_texts = {
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TranslationPostForm, self).__init__(*args, **kwargs)
    
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
            instance.save()
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
        widget=forms.Select(attrs={'class': 'form-control'})
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
            'category': 'التصنيف',  # Add a label for 'category'
            "english_keyword": "بالإنجليزية", 
            "arabic_translation": "بالعربية", 
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
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("هذا البريد الإلكتروني مشترك بالفعل في النشرة الإخبارية.")
        return email