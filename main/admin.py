from django.contrib import admin
from .models import Post, TranslationPost, UserProfile, Category, MainCategory, KeywordTranslation, ReviewerRequest

# Register your models here.

@admin.register(ReviewerRequest)
class ReviewerRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'request_date', 'status', 'processed_date', 'processed_by']
    list_filter = ['status', 'request_date']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['request_date']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        from django.utils import timezone
        for reviewer_request in queryset.filter(status='pending'):
            reviewer_request.status = 'approved'
            reviewer_request.processed_date = timezone.now()
            reviewer_request.processed_by = request.user
            reviewer_request.save()
            
            # Add user to mod group
            from django.contrib.auth.models import Group
            mod_group = Group.objects.get(name='mod')
            reviewer_request.user.groups.add(mod_group)
            
            # Send email notification to user
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                'تمت الموافقة على طلبك لتصبح مراجعًا',
                f'مرحبًا {reviewer_request.user.first_name},\n\nتمت الموافقة على طلبك لتصبح مراجعًا في منصة أرشيف العرب.\nيمكنك الآن الوصول إلى صفحة المراجعة.\n\nشكرًا لك,\nفريق أرشيف العرب',
                settings.DEFAULT_FROM_EMAIL,
                [reviewer_request.user.email],
                fail_silently=False,
            )
        self.message_user(request, f'تمت الموافقة على {queryset.count()} طلب.')
    approve_requests.short_description = "الموافقة على الطلبات المحددة"
    
    def reject_requests(self, request, queryset):
        from django.utils import timezone
        for reviewer_request in queryset.filter(status='pending'):
            reviewer_request.status = 'rejected'
            reviewer_request.processed_date = timezone.now()
            reviewer_request.processed_by = request.user
            reviewer_request.save()
            
            # Send email notification to user
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                'رد على طلبك لتصبح مراجعًا',
                f'مرحبًا {reviewer_request.user.first_name},\n\nنعتذر، لم يتم قبول طلبك لتصبح مراجعًا في منصة أرشيف العرب.\nيمكنك إعادة تقديم الطلب لاحقًا.\n\nشكرًا لك,\nفريق أرشيف العرب',
                settings.DEFAULT_FROM_EMAIL,
                [reviewer_request.user.email],
                fail_silently=False,
            )
        self.message_user(request, f'تم رفض {queryset.count()} طلب.')
    reject_requests.short_description = "رفض الطلبات المحددة"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'affiliation', 'country', 'completed', 'email_confirmed']
    list_filter = ['completed', 'email_confirmed', 'country']
    search_fields = ['user__username', 'user__email', 'affiliation']
    verbose_name = 'ملف المستخدم'
    verbose_name_plural = 'ملفات المستخدمين'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'is_approved', 'created_at']
    list_filter = ['status', 'is_approved', 'created_at']
    search_fields = ['title', 'author__username']
    verbose_name = 'مشاركة'
    verbose_name_plural = 'المشاركات'

@admin.register(TranslationPost)
class TranslationPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'translator', 'status', 'is_approved']
    list_filter = ['status', 'is_approved']
    verbose_name = 'مشاركة مترجمة'
    verbose_name_plural = 'المشاركات المترجمة'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_category']
    list_filter = ['main_category']
    verbose_name = 'تصنيف فرعي'
    verbose_name_plural = 'التصنيفات الفرعية'

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'english_name']
    verbose_name = 'التصنيف الرئيسي'
    verbose_name_plural = 'التصنيفات الرئيسية'

@admin.register(KeywordTranslation)
class KeywordTranslationAdmin(admin.ModelAdmin):
    list_display = ['english_keyword', 'arabic_translation', 'category']
    list_filter = ['category']
    search_fields = ['english_keyword', 'arabic_translation']
    verbose_name = 'ترجمة مصطلح'
    verbose_name_plural = 'ترجمات المصطلحات'
