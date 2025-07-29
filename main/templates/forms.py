from django import forms 

from django.contrib.auth.forms import UserCreationForm, UsernameField, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from .models import Post, TranslationPost, COUNTRY_CHOICES

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
        fields = ['title',  "authors", 'description',  "keywords",'category', "comments", "external_doi",  "pdf"]  # Add 'category' here
        labels = {
            'title': 'عنوان المقال',
            "authors": "مؤلف المقال",
            'description': 'ملخص',
            "keywords":"الكلمات الدالة",
            'category': 'التصنيف',  # Add a label for 'category'
            "comments": "تعليق", 
            "external_doi": "DOI", 
            "pdf": "الملف PDF", 
        }
        help_texts = {
            'comments': 'إذا لم يكن التصنيف موجود، يرجى ذكره هنا.',
            'authors': '',
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }

class TranslationPostForm(forms.ModelForm):
    class Meta:
        model = TranslationPost
        fields = ['title', "authors", "translator", 'description', "keywords", 'category', "comments", "external_doi", "pdf"]
        labels = {
            'title': 'عنوان المقال',
            "authors": "مؤلف المقال",
            'description': 'ملخص',
            "keywords": "الكلمات الدالة",
            'category': 'التصنيف',
            "comments": "تعليق",
            "external_doi": "DOI",
            "pdf": "الملف PDF",
            'translator': 'مترجم المقال',  # Label for the translator field
        }
        help_texts = {
            'comments': 'إذا لم يكن التصنيف موجود، يرجى ذكره هنا.',
            'pdf': 'يجب رفع ملف PDF للمقال (إجباري)',
        }

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

    

