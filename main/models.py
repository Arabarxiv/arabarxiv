from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.files.storage import FileSystemStorage
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()

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
    def __str__(self):
        return self.name
    
class Category(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    affiliation = models.TextField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    website = models.TextField(max_length=200, null=True, blank=True)
    career = models.TextField(max_length=200, null=True, blank=True)
    main_category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='user_profile', null=True, blank=True)

    completed = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)

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

    def __str__(self):
        return self.title + "\n" + self.description

    def save(self, *args, **kwargs):
        if not self.category:
            category, created = Category.objects.get_or_create(name='الذكاء الاصطناعي')
            self.category = category
        super(Post, self).save(*args, **kwargs)

class TranslationPost(Post):
    translator = models.CharField(max_length=400)

class KeywordTranslation(models.Model):
    english_keyword = models.CharField(max_length=200)
    arabic_translation = models.CharField(max_length=200)
    category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.english_keyword

