from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Post, TranslationPost, UserProfile, Category, MainCategory, KeywordTranslation, ReviewerRequest, Comment, PostView, AnonymousPostView, NewsletterSubscriber, PostAuthor

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
        approved_count = 0
        
        for reviewer_request in queryset.filter(status='pending'):
            reviewer_request.status = 'approved'
            reviewer_request.processed_date = timezone.now()
            reviewer_request.processed_by = request.user
            reviewer_request.save()
            
            # Add user to mod group
            from django.contrib.auth.models import Group
            mod_group = Group.objects.get(name='mod')
            reviewer_request.user.groups.add(mod_group)
            
            # Send email notification to user (with error handling)
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    'تمت الموافقة على طلبك لتصبح مراجعًا',
                    f'مرحبًا {reviewer_request.user.first_name},\n\nتمت الموافقة على طلبك لتصبح مراجعًا في منصة أرشيف العرب.\nيمكنك الآن الوصول إلى صفحة المراجعة.\n\nشكرًا لك,\nفريق أرشيف العرب',
                    settings.DEFAULT_FROM_EMAIL,
                    [reviewer_request.user.email],
                    fail_silently=True,  # Changed to True to prevent errors
                )
                print(f"Email sent successfully to {reviewer_request.user.email}")
            except Exception as e:
                print(f"Failed to send email to {reviewer_request.user.email}: {e}")
                # Don't let email failure break the approval process
            
            approved_count += 1
        
        self.message_user(request, f'تمت الموافقة على {approved_count} طلب.')
    approve_requests.short_description = "الموافقة على الطلبات المحددة"
    
    def reject_requests(self, request, queryset):
        from django.utils import timezone
        rejected_count = 0
        
        for reviewer_request in queryset.filter(status='pending'):
            reviewer_request.status = 'rejected'
            reviewer_request.processed_date = timezone.now()
            reviewer_request.processed_by = request.user
            reviewer_request.save()
            
            # Send email notification to user (with error handling)
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    'رد على طلبك لتصبح مراجعًا',
                    f'مرحبًا {reviewer_request.user.first_name},\n\nنعتذر، لم يتم قبول طلبك لتصبح مراجعًا في منصة أرشيف العرب.\nيمكنك إعادة تقديم الطلب لاحقًا.\n\nشكرًا لك,\nفريق أرشيف العرب',
                    settings.DEFAULT_FROM_EMAIL,
                    [reviewer_request.user.email],
                    fail_silently=True,  # Changed to True to prevent errors
                )
                print(f"Rejection email sent successfully to {reviewer_request.user.email}")
            except Exception as e:
                print(f"Failed to send rejection email to {reviewer_request.user.email}: {e}")
                # Don't let email failure break the rejection process
            
            rejected_count += 1
        
        self.message_user(request, f'تم رفض {rejected_count} طلب.')
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
    list_display = ['meaningful_id', 'title', 'author', 'status', 'is_approved', 'created_at']
    list_filter = ['status', 'is_approved', 'created_at']
    search_fields = ['title', 'author__username', 'meaningful_id']
    readonly_fields = ['meaningful_id']
    verbose_name = 'مشاركة'
    verbose_name_plural = 'المشاركات'

@admin.register(TranslationPost)
class TranslationPostAdmin(admin.ModelAdmin):
    list_display = ['meaningful_id', 'title', 'author', 'translator', 'status', 'is_approved']
    list_filter = ['status', 'is_approved']
    search_fields = ['title', 'author__username', 'meaningful_id']
    readonly_fields = ['meaningful_id']
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
    list_display = ['english_keyword', 'arabic_translation', 'category', 'status', 'submitted_by', 'submitted_at']
    list_filter = ['category', 'status', 'submitted_at']
    search_fields = ['english_keyword', 'arabic_translation']
    readonly_fields = ['submitted_at']
    actions = ['approve_terms', 'reject_terms']
    verbose_name = 'ترجمة مصطلح'
    verbose_name_plural = 'ترجمات المصطلحات'
    
    def approve_terms(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'تمت الموافقة على {updated} مصطلح.')
    approve_terms.short_description = "الموافقة على المصطلحات المحددة"
    
    def reject_terms(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'تم رفض {updated} مصطلح.')
    reject_terms.short_description = "رفض المصطلحات المحددة"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'content']
    list_filter = ['created_at', 'post']
    search_fields = ['author__username', 'post__title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    verbose_name = 'تعليق'
    verbose_name_plural = 'التعليقات'

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'session_key', 'viewed_at']
    list_filter = ['viewed_at', 'post']
    search_fields = ['post__title', 'user__username', 'session_key']
    readonly_fields = ['viewed_at']
    verbose_name = 'مشاهدة مشاركة'
    verbose_name_plural = 'مشاهدات المشاركات'

@admin.register(AnonymousPostView)
class AnonymousPostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'session_key', 'viewed_at']
    list_filter = ['viewed_at', 'post']
    search_fields = ['post__title', 'session_key']
    readonly_fields = ['viewed_at']
    verbose_name = 'مشاهدة مجهولة'
    verbose_name_plural = 'مشاهدات مجهولة'

class NewsletterSubscriberResource(resources.ModelResource):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email', 'name', 'subscribed_at')
        export_order = ('email', 'name', 'subscribed_at')
        skip_unchanged = True
        report_skipped = False

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ImportExportModelAdmin):
    resource_class = NewsletterSubscriberResource
    list_display = ['email', 'name', 'subscribed_at']
    list_filter = ['subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']
    verbose_name = 'مشترك في النشرة الإخبارية'
    verbose_name_plural = 'المشتركون في النشرة الإخبارية'

@admin.register(PostAuthor)
class PostAuthorAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'order', 'is_creator']
    list_filter = ['is_creator', 'order']
    search_fields = ['post__title', 'user__username', 'user__first_name', 'user__last_name']
    ordering = ['post', 'order']
    verbose_name = 'مؤلف مشاركة'
    verbose_name_plural = 'مؤلفو المشاركات'
