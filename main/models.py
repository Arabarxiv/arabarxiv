from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.files.storage import FileSystemStorage
from django_countries.fields import CountryField
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    affiliation = models.TextField(max_length=200, null=True, blank=True)
    country = CountryField(blank=True)
    website = models.TextField(max_length=200, null=True, blank=True)
    career = models.TextField(max_length=200, null=True, blank=True)
    main_category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='user_profile', null=True, blank=True)

    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_posts')
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=400)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    pdf = models.FileField(upload_to='pdfs', storage=gd_storage, null=True, blank=True)

    keywords = models.CharField(max_length=200)  # Keywords for the post
    comments = models.CharField(max_length=200, blank=True)  # Comments related to the post (can be blank)
    external_doi = models.CharField(max_length=100, blank=True)  # External DOI (can be blank)
    

    # Moderation
    # New fields
    status = models.CharField(max_length=20, default='Pending')
    is_approved = models.BooleanField(default=False)
    reviewer_comments = models.TextField(blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_posts')

    is_translation = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title + "\n" + self.description

    def save(self, *args, **kwargs):
        if not self.category:
            category, created = Category.objects.get_or_create(name='الذكاء الاصطناعي')
            self.category = category
        super(Post, self).save(*args, **kwargs)

class KeywordTranslation(models.Model):
    english_keyword = models.CharField(max_length=200)
    arabic_translation = models.CharField(max_length=200)
    category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.english_keyword

