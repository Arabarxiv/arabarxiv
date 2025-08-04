from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.files.storage import FileSystemStorage
# from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
# gd_storage = GoogleDriveStorage()

COUNTRY_CHOICES = [
        ("AF","أفغانستان "),
        ("US","الولايات المتحدة"),
        ("GP"," جزر جوادلوب"),
        ("IS","آيسلندا"),
        ("ET","أثيوبيا"),
        ("AZ","أذربيجان"),
        ("TF","أراض فرنسية جنوبية"),
        ("AM","أرمينيا"),
        ("AW","أروبا"),
        ("AU","أستراليا"),
        ("AL","ألبانيا"),
        ("DE","ألمانيا"),
        ("AQ","أنتاركتيكا"),
        ("AG","أنتيغوا/بربودا"),
        ("AI","أنجويلا"),
        ("AD","أندورا"),
        ("ID","أندونيسيا"),
        ("AO","أنغولا"),
        ("UY","أورغواي"),
        ("UZ","أوزباكستان"),
        ("UG","أوغندا"),
        ("UA","أوكرانيا"),
        ("IE","أيرلندا"),
        ("ER","إريتريا"),
        ("ES","إسبانيا"),
        ("EC","إكوادور"),
        ("SV","إلسلفادور"),
        ("IR","إيران"),
        ("IT","إيطاليا"),
        ("EE","استونيا"),
        ("AR","الأرجنتين"),
        ("JO","الأردن"),
        ("AE","الإمارات العربية المتحدة"),
        ("BS","الباهاماس"),
        ("BH","البحرين"),
        ("BR","البرازيل"),
        ("PT","البرتغال"),
        ("BA","البوسنة/الهرسك"),
        ("ME","الجبل الأسو"),
        ("DZ","الجزائر"),
        ("VI","الجزر العذراء الأمريكي"),
        ("VG","الجزر العذراء البريطانية"),
        ("CZ","الجمهورية التشيكية"),
        ("DO","الجمهورية الدومينيكية"),
        ("DK","الدانمارك"),
        ("CV","الرأس الأخضر"),
        ("SN","السنغال"),
        ("SD","السودان"),
        ("SE","السويد"),
        ("EH","الصحراء الغربية"),
        ("SO","الصومال"),
        ("CN","الصين"),
        ("IQ","العراق"),
        ("GA","الغابون"),
        ("PH","الفليبين"),
        ("CG","الكونغو"),
        ("KW","الكويت"),
        ("MV","المالديف"),
        ("MA","المغرب"),
        ("MX","المكسيك"),
        ("SA","المملكة العربية السعودية"),
        ("GB","المملكة المتحدة"),
        ("NO","النرويج"),
        ("AT","النمسا"),
        ("NE","النيجر"),
        ("IN","الهند"),
        ("JP","اليابان"),
        ("YE","اليمن"),
        ("GR","اليونان"),
        ("PG","بابوا غينيا الجديدة"),
        ("PY","باراغواي"),
        ("PK","باكستان"),
        ("PW","بالاو"),
        ("BB","بربادوس"),
        ("BN","بروني"),
        ("BE","بلجيكا"),
        ("BG","بلغاريا"),
        ("BD","بنغلاديش"),
        ("PA","بنما"),
        ("BJ","بنين"),
        ("BT","بوتان"),
        ("BW","بوتسوانا"),
        ("PR","بورتوريكو"),
        ("BF","بوركينا فاسو"),
        ("BI","بوروندي"),
        ("PL","بولندا"),
        ("BO","بوليفيا"),
        ("PF","بولينيزيا الفرنسية"),
        ("PN","بيتكيرن"),
        ("PE","بيرو"),
        ("BZ","بيليز"),
        ("TH","تايلندا"),
        ("TW","تايوان"),
        ("TM","تركمانستان"),
        ("TR","تركيا"),
        ("TT","ترينيداد وتوباغو"),
        ("TD","تشاد"),
        ("TZ","تنزانيا"),
        ("TG","توغو"),
        ("TV","توفالو"),
        ("TK","توكلو"),
        ("TN","تونس"),
        ("TO","تونغا"),
        ("TL","تيمور الشرقية"),
        ("GI","جبل طارق"),
        ("GL","جرينلاند"),
        ("AX","جزر أولند"),
        ("AN","جزر الأنتيل الهولندي"),
        ("KM","جزر القمر"),
        ("UM","جزر الولايات المتحدة الصغيرة"),
        ("BM","جزر برمود"),
        ("TC","جزر توركس/كايكوس"),
        ("SB","جزر سليمان"),
        ("FO","جزر فارو"),
        ("FK","جزر فوكلاند(المالديف)"),
        ("KY","جزر كايمان"),
        ("CK","جزر كوك"),
        ("CC","جزر كوكس(كيلينغ)"),
        ("MH","جزر مارشال"),
        ("MP","جزر ماريانا الشمالية"),
        ("BV","جزيرة بوفيه"),
        ("CX","جزيرة كريسماس"),
        ("IM","جزيرة مان"),
        ("NF","جزيرة نورفولك"),
        ("HM","جزيرة هيرد/جزر ماكدونالد"),
        ("JM","جمايكا"),
        ("CF","جمهورية أفريقيا الوسطى"),
        ("ZA","جنوب أفريقيا"),
        ("GU","جوام"),
        ("GS","جورجيا الجنوبية/جزر ساندويتش"),
        ("DJ","جيبوتي"),
        ("JE","جيرزي"),
        ("GE","جيورجيا"),
        ("VA","دولة مدينة الفاتيكان"),
        ("DM","دومينيكا"),
        ("RW","رواندا"),
        ("RU","روسيا"),
        ("BY","روسيا البيضاء"),
        ("RO","رومانيا"),
        ("RE","ريونيون"),
        ("ZM","زامبيا"),
        ("ZW","زمبابوي"),
        ("CI","ساحل العاج"),
        ("WS","ساموا"),
        ("AS","ساموا الأمريكية"),
        ("SM","سان مارينو"),
        ("BL","سانت بارتليمي"),
        ("PM","سانت بيير/ميكلون"),
        ("VC","سانت فنسنت/الجرينادين"),
        ("KN","سانت كيتس/نيفيس"),
        ("LC","سانت لوسيا"),
        ("MF","سانت مارتن"),
        ("SH","سانت هيلانة"),
        ("ST","ساو تومي/برينسيب"),
        ("LK","سريلانكا"),
        ("SJ","سفالبارد/يان ماين"),
        ("SK","سلوفاكيا"),
        ("SI","سلوفينيا"),
        ("SG","سنغافورة"),
        ("SZ","سوازيلند"),
        ("SY","سورية"),
        ("SR","سورينام"),
        ("CH","سويسرا"),
        ("SL","سيراليون"),
        ("SC","سيشيل"),
        ("CL","شيلي"),
        ("RS","صربيا"),
        ("TJ","طاجيكستان"),
        ("OM","عُمان"),
        ("GM","غامبيا"),
        ("GH","غانا"),
        ("GD","غرينادا"),
        ("GT","غواتيمال"),
        ("GF","غويانا الفرنسية"),
        ("GY","غيانا"),
        ("GG","غيرنزي"),
        ("GN","غينيا"),
        ("GQ","غينيا الاستوائي"),
        ("GW","غينيا-بيساو"),
        ("VU","فانواتو"),
        ("FR","فرنسا"),
        ("PS","فلسطين"),
        ("VE","فنزويلا"),
        ("FI","فنلندا"),
        ("VN","فيتنام"),
        ("FJ","فيجي"),
        ("CY","قبرص"),
        ("QA","قطر"),
        ("KG","قيرغيزستان"),
        ("KZ","كازاخستان"),
        ("NC","كاليدونيا الجديدة"),
        ("CM","كاميرون"),
        ("HR","كرواتيا"),
        ("KH","كمبوديا"),
        ("CA","كندا"),
        ("CU","كوبا"),
        ("KR","كوريا الجنوبية"),
        ("KP","كوريا الشمالية"),
        ("CR","كوستاريكا"),
        ("CO","كولومبيا"),
        ("KI","كيريباتي"),
        ("KE","كينيا"),
        ("LV","لاتفيا"),
        ("LA","لاوس"),
        ("LB","لبنان"),
        ("LT","لتوانيا"),
        ("LU","لوكسمبورغ"),
        ("LY","ليبيا"),
        ("LR","ليبيريا"),
        ("LI","ليختنشتين"),
        ("LS","ليسوتو"),
        ("MQ","مارتينيك"),
        ("MO","ماكاو"),
        ("MW","مالاوي"),
        ("MT","مالطا"),
        ("ML","مالي"),
        ("MY","ماليزيا"),
        ("YT","مايوت"),
        ("MG","مدغشقر"),
        ("EG","مصر"),
        ("MK","مقدونيا"),
        ("MN","منغوليا"),
        ("MR","موريتانيا"),
        ("MU","موريشيوس"),
        ("MZ","موزمبيق"),
        ("MD","مولدافيا"),
        ("MC","موناكو"),
        ("MS","مونتسيرات"),
        ("MM","ميانمار"),
        ("FM","ميكرونيسيا"),
        ("NA","ناميبيا"),
        ("NR","ناورو"),
        ("NP","نيبال"),
        ("NG","نيجيريا"),
        ("NI","نيكاراجوا"),
        ("NZ","نيوزيلندا"),
        ("NU","نييوي"),
        ("HT","هايتي"),
        ("HN","هندوراس"),
        ("HU","هنغاريا"),
        ("NL","هولندا"),
        ("HK","هونغ كونغ"),
        ("WF","والس/فوتونا)") ]

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    english_name = models.CharField(max_length=100)
    class Meta:
        verbose_name = 'التصنيف الرئيسي'
        verbose_name_plural = 'التصنيفات الرئيسية'
    def __str__(self):
        return self.name
    
class Category(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', help_text='Parent category for hierarchical structure')
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'تصنيف فرعي'
        verbose_name_plural = 'التصنيفات الفرعية'
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    affiliation = models.TextField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    website = models.TextField(max_length=200, null=True, blank=True)
    career = models.TextField(max_length=200, null=True, blank=True)
    main_category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='user_profile', null=True, blank=True)

    completed = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    who_am_i = models.TextField(blank=True, null=True, verbose_name='من أنا', help_text='ملخص مختصر عن الباحث')
    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'
    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_posts')
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=400)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    categories = models.ManyToManyField(Category, related_name='posts', blank=True, verbose_name='التصنيفات')
    pdf = models.FileField(upload_to='pdfs')
    #pdf = models.FileField(upload_to='pdfs', storage=gd_storage, null=True, blank=True)

    keywords = models.CharField(max_length=200)  # Keywords for the post
    external_doi = models.CharField(max_length=100, blank=True)  # External DOI (can be blank)
    
    # Custom meaningful ID
    meaningful_id = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='الرقم المعرفي')
    

    # Moderation
    # New fields
    STATUS_CHOICES = [
        ('Pending', 'قيد الانتظار'),
        ('Approved', 'تمت الموافقة'),
        ('Rejected', 'مرفوض'),
        ('Rejected_For_Reassignment', 'مرفوض لإعادة التعيين'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    is_approved = models.BooleanField(default=False)
    reviewer_comments = models.TextField(blank=True)  # Comments sent to author via email
    admin_comments = models.TextField(blank=True)     # Private comments only visible to admins
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_posts')
    previous_reviewers = models.ManyToManyField(User, blank=True, related_name='previously_reviewed_posts', help_text='Reviewers who have already reviewed this post')
    final_reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='finally_reviewed_posts', help_text='The reviewer who made the final decision (approved/rejected)')
    review_started = models.BooleanField(default=False, help_text='Indicates if the reviewer has started reviewing this post')
    recommended_for_best_article = models.BooleanField(default=False, help_text='Indicates if the reviewer recommended this post for best article of the month')
    is_edited_after_approval = models.BooleanField(default=False, help_text='Indicates if the post was edited after being approved')
    class Meta:
        verbose_name = 'مشاركة'
        verbose_name_plural = 'المشاركات'
    def __str__(self):
        return self.title
    
    def get_view_count(self):
        """Return the number of unique views for this post"""
        return self.views.count()

    def get_comment_count(self):
        """Return the number of comments for this post"""
        return self.comments.count()
    
    def get_pdf_view_count(self):
        """Return the number of unique PDF views for this post"""
        return self.pdf_views.count()
    
    def get_total_view_count(self):
        """Return the total view count including both post views and PDF views"""
        return self.views.count() + self.pdf_views.count()
    
    def add_pdf_view(self, user):
        """Add a PDF view for this post by a user, but only if they haven't viewed the post details"""
        if user.is_authenticated:
            # Check if user has already viewed the post details
            has_viewed_post = self.views.filter(user=user).exists()
            # Check if user has already viewed the PDF
            has_viewed_pdf = self.pdf_views.filter(user=user).exists()
            
            # Only add PDF view if user hasn't viewed the PDF before
            if not has_viewed_pdf:
                PostPdfView.objects.get_or_create(post=self, user=user)
                return True
        return False

    def generate_meaningful_id(self):
        """Generate a meaningful ID based on the primary category"""
        if self.categories.exists():
            # Get the first category (primary category)
            primary_category = self.categories.first()
            main_category = primary_category.main_category
            
            # Count posts in this category to get the sequence number
            category_posts_count = Post.objects.filter(
                categories=primary_category
            ).count()
            
            # Format: main_category_id.sub_category_id.sequence_number
            meaningful_id = f"{main_category.id}.{primary_category.id}.{category_posts_count + 1}"
            return meaningful_id
        return None
    
    def regenerate_meaningful_id(self):
        """Regenerate meaningful ID based on current categories"""
        if self.categories.exists():
            meaningful_id = self.generate_meaningful_id()
            if meaningful_id:
                self.meaningful_id = meaningful_id
                self.save(update_fields=['meaningful_id'])
                return meaningful_id
        else:
            # Clear meaningful ID if no categories
            self.meaningful_id = None
            self.save(update_fields=['meaningful_id'])
        return None
    
    def get_meaningful_id_display(self):
        """Get a human-readable version of the meaningful ID"""
        if self.meaningful_id:
            parts = self.meaningful_id.split('.')
            if len(parts) == 3:
                main_cat_id, sub_cat_id, seq_num = parts
                try:
                    main_category = MainCategory.objects.get(id=main_cat_id)
                    sub_category = Category.objects.get(id=sub_cat_id)
                    return f"{main_category.name} - {sub_category.name} - {seq_num}"
                except (MainCategory.DoesNotExist, Category.DoesNotExist):
                    return self.meaningful_id
        return self.meaningful_id or f"ID-{self.id}"
    
    def save(self, *args, **kwargs):
        # Save the post normally - meaningful ID generation is handled in forms
        super(Post, self).save(*args, **kwargs)

class TranslationPost(Post):
    translator = models.CharField(max_length=400)
    class Meta:
        verbose_name = 'مشاركة مترجمة'
        verbose_name_plural = 'المشاركات المترجمة'

class KeywordTranslation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    
    english_keyword = models.CharField(max_length=200)
    arabic_translation = models.CharField(max_length=200)
    category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved', verbose_name='الحالة')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تم الإرسال بواسطة')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    
    class Meta:
        verbose_name = 'ترجمة مصطلح'
        verbose_name_plural = 'ترجمات المصطلحات'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f'{self.english_keyword} - {self.arabic_translation}'
    
    def save(self, *args, **kwargs):
        # Set default status for existing records
        if not self.pk and not self.status:
            self.status = 'approved'
        super().save(*args, **kwargs)

class ReviewerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewer_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    class Meta:
        verbose_name = 'طلب مراجع'
        verbose_name_plural = 'طلبات المراجعين'
        ordering = ['-request_date']
    def __str__(self):
        return f"طلب مراجع من {self.user.username} - {self.get_status_display()}"
    
    ordering = ['-request_date']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'تعليق من {self.author.username} على {self.post.title}'
    
    def is_edited(self):
        """Check if the comment has been edited"""
        return self.is_modified


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مشاهدة مشاركة'
        verbose_name_plural = 'مشاهدات المشاركات'
        unique_together = ['post', 'user']  # Ensures one view per user per post
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f'مشاهدة من {self.user.username} لـ {self.post.title}'


class PostPdfView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pdf_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_pdf_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مشاهدة PDF مشاركة'
        verbose_name_plural = 'مشاهدات PDF المشاركات'
        unique_together = ['post', 'user']  # Ensures one PDF view per user per post
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f'مشاهدة PDF من {self.user.username} لـ {self.post.title}'

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    name = models.CharField(max_length=100, blank=True, verbose_name='الاسم')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الاشتراك')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False, verbose_name='مؤكد')
    
    class Meta:
        verbose_name = 'مشترك في النشرة الإخبارية'
        verbose_name_plural = 'المشتركون في النشرة الإخبارية'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f'{self.email} ({self.name if self.name else "بدون اسم"})'

