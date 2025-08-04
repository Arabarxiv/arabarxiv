from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, PostForm, ModifyNameForm, ModifyEmailForm, CustomPasswordResetForm, KeywordTranslationForm, TranslationPostForm, CommentForm, NewsletterSignupForm, ModifyWhoAmIForm, ModifyAffiliationForm, ModifyCountry, ModifyMainCategoryForm, ModifyCareerForm, ModifyWebsiteForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post, KeywordTranslation, MainCategory, Category, TranslationPost, Comment, PostView, PostPdfView, NewsletterSubscriber
from .forms import CustomLoginForm
from django.contrib import messages
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import Http404
from functools import wraps

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetCompleteView
from django.db.models import Q, Count
import logging

logger = logging.getLogger(__name__)

# Custom authorization decorators
def email_confirmation_required(view_func):
    """Decorator to check if user's email is confirmed"""
    def _wrapped_view_func(request, *args, **kwargs):
        # Superusers bypass all email confirmation requirements
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_authenticated and not request.user.userprofile.email_confirmed:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'email_not_confirmed',
                'error_title': 'تأكيد البريد الإلكتروني مطلوب',
                'error_message': 'يجب تأكيد بريدك الإلكتروني قبل إنشاء منشور جديد.',
                'action_button_text': 'إعادة إرسال بريد التأكيد',
                'action_url': f'/resend-confirmation-email/{request.user.id}/',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def moderator_required(view_func):
    """Decorator to check if user is a moderator or staff"""
    def _wrapped_view_func(request, *args, **kwargs):
        logger.debug(f"Moderator decorator check for {request.user.username} - superuser: {request.user.is_superuser}")
        
        if not request.user.is_authenticated:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'login_required',
                'error_title': 'تسجيل الدخول مطلوب',
                'error_message': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة.',
                'action_button_text': 'تسجيل الدخول',
                'action_url': '/login',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        
        # Superusers bypass all moderator requirements
        if request.user.is_superuser:
            logger.debug(f"Superuser {request.user.username} bypassing moderator decorator")
            return view_func(request, *args, **kwargs)
        
        if not is_mod_or_staff(request.user):
            return render(request, 'main/authorization_error.html', {
                'error_type': 'moderator_required',
                'error_title': 'صلاحيات المراجع مطلوبة',
                'error_message': 'يجب أن تكون مراجعًا للوصول إلى هذه الصفحة.',
                'action_button_text': 'طلب أن تصبح مراجعًا',
                'action_url': '/become_reviewer',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def author_required(view_func):
    """Decorator to check if user is the author of a post"""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'login_required',
                'error_title': 'تسجيل الدخول مطلوب',
                'error_message': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة.',
                'action_button_text': 'تسجيل الدخول',
                'action_url': '/login',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        
        # Superusers bypass all author requirements
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Get post_id from kwargs or request
        post_id = kwargs.get('post_id') or request.POST.get('post_id')
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                if post.author != request.user:
                    return render(request, 'main/authorization_error.html', {
                        'error_type': 'author_required',
                        'error_title': 'صلاحيات المؤلف مطلوبة',
                        'error_message': 'يمكن فقط للمؤلف الأصلي حذف أو تعديل هذا المنشور.',
                        'action_button_text': 'عرض المنشور',
                        'action_url': f'/posts',
                        'back_button_text': 'العودة للصفحة الرئيسية',
                        'back_url': '/home'
                    })
            except Post.DoesNotExist:
                raise Http404("المنشور غير موجود")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def profile_completion_required(view_func):
    """Decorator to check if user profile is completed"""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'login_required',
                'error_title': 'تسجيل الدخول مطلوب',
                'error_message': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة.',
                'action_button_text': 'تسجيل الدخول',
                'action_url': '/login',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        
        # Superusers bypass all profile completion requirements
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if not request.user.userprofile.completed:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'profile_incomplete',
                'error_title': 'ملف الملف الشخصي غير مكتمل',
                'error_message': 'يجب إكمال ملفك الشخصي قبل الوصول إلى هذه الصفحة.',
                'action_button_text': 'إكمال الملف الشخصي',
                'action_url': '/user_profile',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def logout_view(request):
    logout(request)
    return redirect("/home")

def authors(request):
    return render(request, "main/authors.html")

def real_home(request):
    return render(request, 'main/real_home.html')

def get_categories_by_main_category(main_category_name):
    # Retrieve categories where the main category matches the given name
    categories = Category.objects.filter(main_category__name=main_category_name)
    return categories

def palestine_view(request):
    main_category_name = "الثقافة والتاريخ الفلسطيني"  # Replace with the desired main category name
    posts_in_main_category = get_categories_by_main_category(main_category_name)
    
    return render(request, 'main/palestine.html', {"cats": posts_in_main_category})

def profile_view(request):
    return render(request, 'main/user_profile.html')

def public_profile(request, user_id):
    """Public profile view that allows anyone to view a user's profile"""
    try:
        user = User.objects.get(id=user_id)
        
        # Get translation post IDs for comparison
        translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
        
        # Get user's posts and mark which ones are translations
        posts = Post.objects.filter(author=user)
        for post in posts:
            post.is_translation = post.id in translation_post_ids
            # Add translator field for easy access in template
            if post.is_translation:
                try:
                    post.translator = post.translationpost.translator
                except:
                    post.translator = ""
        
        # Get reviewed posts (posts that this user has reviewed)
        reviewed_posts = Post.objects.filter(final_reviewer=user).order_by('-updated_at')
        for reviewed_post in reviewed_posts:
            reviewed_post.is_translation = reviewed_post.id in translation_post_ids
            if reviewed_post.is_translation:
                try:
                    reviewed_post.translator = reviewed_post.translationpost.translator
                except:
                    reviewed_post.translator = ""
        
        context = {
            'profile_user': user,  # The user whose profile is being viewed
            'posts': posts,
            'reviewed_posts': reviewed_posts,
            'is_own_profile': request.user.is_authenticated and request.user.id == user_id
        }
        
        return render(request, 'main/public_profile.html', context)
    except User.DoesNotExist:
        messages.error(request, 'المستخدم غير موجود.')
        return redirect('posts')

def author_guidelines(request):
    return render(request, 'main/author_guidelines.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Basic validation
        try:
            validate_email(email)
            # Send an email
            send_mail(
                subject=f"Message from {name}",
                message=f'This message was sent by {email}: \n {message}',
                from_email=email,
                recipient_list=['arabarxiv@gmail.com'], 
            )
            messages.success(request, 'شكرًا لرسالتك، تم إرسالها بنجاح.')
        except ValidationError:
            messages.error(request, 'البريد الإلكتروني غير صالح، يرجى العودة وتصحيحه.')

        return redirect('contact')
    
    return render(request, 'main/contact.html')

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

def send_confirmation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri('/confirm-email/' + uid + '/' + token + '/')

    message = f"الرجاء الضغط على الرابط التالي لتأكيد تسجيلك: {url}"
    #send_mail('تأكيد تسجيلك', message, None, [user.email])
    send_mail('تأكيد تسجيلك', message, settings.DEFAULT_FROM_EMAIL, [user.email])


def search_posts(request):
    query = request.GET.get('searchKeyword', '')
    results = Post.objects.filter(
        Q(title__icontains=query) | Q(authors__icontains=query), is_approved=True
    )
    
    # Get translation post IDs for comparison
    translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
    
    # Mark which posts are translations and add translator field
    for post in results:
        post.is_translation = post.id in translation_post_ids
        if post.is_translation:
            try:
                post.translator = post.translationpost.translator
            except:
                post.translator = ""
    
    return render(request, 'main/search_results.html', {'results': results})


def send_thank_you_email(user, post):
    subject = 'شكرًا لك على مشاركتك, {}'.format(user.first_name)
    html_content = render_to_string('emails/post_submit_email.html', {
        'user': user,
        'post_title': post.title,
        'post_abstract': post.description,
        'site_url': 'http://www.arabarxiv.org'  # Replace with your website URL
    })
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    email = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_accepted(user, post):
    subject = 'تمت الموافقة على مشاركتك, {}'.format(user.first_name)
    
    # Debug: Print the reviewer comments to see if they're being passed
    print(f"DEBUG: Sending accepted email to {user.email}")
    print(f"DEBUG: Reviewer comments: '{post.reviewer_comments}'")
    
    html_content = render_to_string('emails/post_accepted_email.html', {
        'user': user,
        'post_title': post.title,
        'post_abstract': post.description,
        'reviewer_comments': post.reviewer_comments,
        'site_url': 'http://www.arabarxiv.org'  # Replace with your website URL
    })
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    email = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_rejected(user, post):
    subject = 'تم رفض مشاركتك, {}'.format(user.first_name)
    
    # Debug: Print the reviewer comments to see if they're being passed
    print(f"DEBUG: Sending rejected email to {user.email}")
    print(f"DEBUG: Reviewer comments: '{post.reviewer_comments}'")
    
    html_content = render_to_string('emails/post_rejected_email.html', {
        'user': user,
        'post_title': post.title,
        'post_abstract': post.description,
        'reviewer_comments': post.reviewer_comments,
        'site_url': 'http://www.arabarxiv.org'  # Replace with your website URL
    })
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    email = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()

def home(request):
    # Get filter parameter from request
    filter_type = request.GET.get('filter', 'all')  # Default to 'all' if no filter specified
    sort_by = request.GET.get('sort', 'newest')  # Default to newest
    search_query = request.GET.get('search', '')  # Search query
    

    
    # Get translation post IDs for comparison (same logic used in filters)
    translation_post_ids = set(TranslationPost.objects.values_list('post_ptr_id', flat=True))
    
    # Query posts based on filter
    if filter_type == 'original':
        # Get only original posts (exclude translation posts)
        posts = Post.objects.filter(status="Approved").exclude(
            id__in=translation_post_ids
        )
    elif filter_type == 'translated':
        # Get only translation posts
        posts = Post.objects.filter(
            status="Approved",
            id__in=translation_post_ids
        )
    else:  # 'all' or any other value
        # Get all posts
        posts = Post.objects.filter(status="Approved")
    
    # Apply search filter if provided
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(authors__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'oldest':
        posts = posts.order_by('created_at')
    elif sort_by == 'title':
        posts = posts.order_by('title')
    elif sort_by == 'views':
        # Note: This would require a custom ordering method
        posts = posts.order_by('-created_at')  # Fallback to newest
    elif sort_by == 'comments':
        # Note: This would require a custom ordering method
        posts = posts.order_by('-created_at')  # Fallback to newest
    else:  # 'newest' or default
        posts = posts.order_by('-created_at')
    
    # Set translation attributes AFTER all filtering and sorting
    for post in posts:
        post.is_translation = post.id in translation_post_ids
        
        if post.is_translation:
            try:
                translation_post = TranslationPost.objects.get(post_ptr_id=post.id)
                post.translator = translation_post.translator
            except TranslationPost.DoesNotExist:
                post.translator = ""
        else:
            post.translator = ""
    
    # Add additional post properties for enhanced display
    for post in posts:
        # Calculate engagement score (views + comments)
        post.engagement_score = post.get_view_count() + post.comments.count()
        
        # Add reading time estimate (rough calculation)
        word_count = len(post.description.split()) if post.description else 0
        post.reading_time = max(1, round(word_count / 200))  # Assuming 200 words per minute
        
        # Add excerpt for better display
        if post.description:
            post.excerpt = post.description[:150] + "..." if len(post.description) > 150 else post.description
        else:
            post.excerpt = "لا يوجد وصف متاح"
    
    categories = MainCategory.objects.all()
    
    # Get some statistics for the dashboard
    total_posts = Post.objects.filter(status="Approved").count()
    translation_post_ids = set(TranslationPost.objects.values_list('post_ptr_id', flat=True))
    original_posts = Post.objects.filter(status="Approved").exclude(id__in=translation_post_ids).count()
    translated_posts = Post.objects.filter(status="Approved", id__in=translation_post_ids).count()
    
    # Get recent activity
    recent_posts = Post.objects.filter(status="Approved").order_by('-created_at')[:5]
    
    # Get top categories
    top_categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status="Approved"))
    ).order_by('-post_count')[:5]

    return render(request, 'main/home.html', {
        "posts": posts,
        "categories": categories,
        "current_filter": filter_type,
        "current_sort": sort_by,
        "search_query": search_query,
        "total_posts": total_posts,
        "original_posts": original_posts,
        "translated_posts": translated_posts,
        "recent_posts": recent_posts,
        "top_categories": top_categories,
    })

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to a success page.
            return redirect('/home')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required(login_url="/login")
@email_confirmation_required
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    draft_id = request.GET.get('draft_id')
    draft = None
    
    if draft_id:
        try:
            draft = Post.objects.get(id=draft_id, author=request.user, status='Draft')
        except Post.DoesNotExist:
            pass

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Check if this is a draft saving or new submission
            is_draft_saving = 'save_draft' in request.POST
            
            if is_draft_saving:
                # Save as draft
                post = form.save(commit=False)
                post.author = request.user
                post.status = 'Draft'  # Mark as draft
                
                # Handle custom author selection
                authors_input = request.POST.get('authors', '')
                if authors_input:
                    author_ids = [int(id.strip()) for id in authors_input.split(',') if id.strip()]
                    additional_authors = User.objects.filter(id__in=author_ids, is_superuser=False)
                    
                    # Build the authors string: current user + selected additional authors
                    authors_list = [f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username]
                    
                    # Add selected additional authors
                    for author in additional_authors:
                        author_name = f"{author.first_name} {author.last_name}".strip() or author.username
                        if author_name not in authors_list:
                            authors_list.append(author_name)
                    
                    post.authors = ', '.join(authors_list)
                else:
                    # Only current user as author
                    post.authors = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                
                # Save the post with categories using the form's save method
                post = form.save()
                
                messages.success(request, 'تم حفظ المسودة بنجاح.')
                return redirect("/user_profile")
            else:
                # Create new post
                post = form.save(commit=False)
                post.status = 'Pending'  # Set status to Pending for new submissions
                
                # Handle custom author selection
                authors_input = request.POST.get('authors', '')
                if authors_input:
                    author_ids = [int(id.strip()) for id in authors_input.split(',') if id.strip()]
                    additional_authors = User.objects.filter(id__in=author_ids, is_superuser=False)
                    
                    # Build the authors string: current user + selected additional authors
                    authors_list = [f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username]
                    
                    # Add selected additional authors
                    for author in additional_authors:
                        author_name = f"{author.first_name} {author.last_name}".strip() or author.username
                        if author_name not in authors_list:
                            authors_list.append(author_name)
                    
                    post.authors = ', '.join(authors_list)
                else:
                    # Only current user as author
                    post.authors = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                
                post.author = request.user
                
                # Save the post with categories using the form's save method
                post = form.save()
                
                send_thank_you_email(request.user, post)
                return redirect("/user_profile")
    else:
        if draft:
            # Pre-fill form with draft data
            form = PostForm(instance=draft, user=request.user)
        else:
            form = PostForm(user=request.user)

    return render(request, 'main/create_post.html', {
        "form": form, 
        "draft": draft,
        "active_submission_type": "original_post"
    })

from django.http import JsonResponse
def get_categories(request):
    trigger_value = request.GET.get('trigger_value')
    # Your logic here to determine categories based on trigger_value
    categories = list(Category.objects.values('id', 'name'))
    return JsonResponse({'categories': categories})



def get_users(request):
    # Get all users except superusers and the current user, ordered by first_name, last_name, username
    users = User.objects.filter(is_superuser=False).exclude(id=request.user.id).order_by('first_name', 'last_name', 'username')
    users_data = []
    for user in users:
        # Create a display name that shows first_name last_name (username)
        display_name = f"{user.first_name} {user.last_name} ({user.username})"
        if not user.first_name and not user.last_name:
            display_name = user.username
        users_data.append({
            'id': user.id,
            'name': display_name,
            'username': user.username
        })
    return JsonResponse({'users': users_data})

def get_moderators(request):
    # Get all moderators and staff users, ordered by username
    # Use the same logic as is_mod_or_staff function
    moderators = User.objects.filter(
        Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='mod')
    ).distinct().order_by('username')
    
    # Convert to list of dictionaries
    moderators_list = []
    for moderator in moderators:
        moderators_list.append({
            'id': moderator.id,
            'username': moderator.username
        })
    
    from django.http import JsonResponse
    return JsonResponse({'moderators': moderators_list})




@login_required(login_url="/login")
@email_confirmation_required
@permission_required("main.add_translationpost", login_url="/login", raise_exception=True)  # Update permission
def create_translation_post(request):
    draft_id = request.GET.get('draft_id')
    draft = None
    
    if draft_id:
        try:
            draft = TranslationPost.objects.get(id=draft_id, author=request.user, status='Draft')
        except TranslationPost.DoesNotExist:
            pass

    if request.method == 'POST':
        form = TranslationPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Check if this is a draft saving or new submission
            is_draft_saving = 'save_draft' in request.POST
            
            if is_draft_saving:
                # Save as draft
                translation_post = form.save(commit=False)
                translation_post.author = request.user
                translation_post.status = 'Draft'  # Mark as draft
                
                # Handle custom translator selection (additional translators)
                translators_input = request.POST.get('translators', '')
                if translators_input:
                    translator_ids = [int(id.strip()) for id in translators_input.split(',') if id.strip()]
                    additional_translators = User.objects.filter(id__in=translator_ids, is_superuser=False)
                    
                    # Build the translators string: current user + selected additional translators
                    translators_list = [f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username]
                    
                    # Add selected additional translators
                    for translator in additional_translators:
                        translator_name = f"{translator.first_name} {translator.last_name}".strip() or translator.username
                        if translator_name not in translators_list:
                            translators_list.append(translator_name)
                    
                    translation_post.translator = ', '.join(translators_list)
                else:
                    # Only current user as translator
                    translation_post.translator = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                
                # Set the original author from the form
                translation_post.authors = form.cleaned_data.get('original_author', '')
                
                # Save the post with categories using the form's save method
                translation_post = form.save()
                
                messages.success(request, 'تم حفظ مسودة الترجمة بنجاح.')
                return redirect("/user_profile")
            else:
                # Create new translation post
                translation_post = form.save(commit=False)
                translation_post.status = 'Pending'  # Set status to Pending for new submissions
            
            # Handle custom translator selection (additional translators)
            translators_input = request.POST.get('translators', '')
            if translators_input:
                translator_ids = [int(id.strip()) for id in translators_input.split(',') if id.strip()]
                additional_translators = User.objects.filter(id__in=translator_ids, is_superuser=False)
                
                # Build the translators string: current user + selected additional translators
                translators_list = [f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username]
                
                # Add selected additional translators
                for translator in additional_translators:
                    translator_name = f"{translator.first_name} {translator.last_name}".strip() or translator.username
                    if translator_name not in translators_list:
                        translators_list.append(translator_name)
                
                translation_post.translator = ', '.join(translators_list)
            else:
                # Only current user as translator
                translation_post.translator = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            
            # Set the original author from the form
            translation_post.authors = form.cleaned_data.get('original_author', '')
            translation_post.author = request.user
            
            # Save the post with categories using the form's save method
            translation_post = form.save()
            
            send_thank_you_email(request.user, translation_post)  # Send a thank you email
            return redirect("/user_profile")  # Redirect to a relevant page after saving
    else:
        if draft:
            # Pre-fill form with draft data
            form = TranslationPostForm(instance=draft, user=request.user)
        else:
            form = TranslationPostForm(user=request.user)  # Initialize an empty form for GET request

    return render(request, 'main/create_translation_post.html', {
        "form": form,
        "draft": draft,
        "active_submission_type": "translation_post"
    })  # Render the specific template for creating a translation post

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name =  form.cleaned_data['first_name']
            user.last_name =  form.cleaned_data['last_name']
            user.email =  form.cleaned_data['email']
            user.save()
            login(request, user)
            send_confirmation_email(user, request)
            
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

def confirm_email(request, uidb64, token):
    try:
        print('Raw uidb64:', uidb64) #added
        print('Raw token:', token)  #added
        uid = force_str(urlsafe_base64_decode(uidb64))
        print('Decoded UID:', uid)  #added
        user = User.objects.get(pk=uid)
        print('User found:', user) #added
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:  # "ad e" is added
        print('Exception during UID decode or user lookup:', e) #added
        user = None

    if user is not None:
        is_token_valid = default_token_generator.check_token(user, token)
        print('Token valid:', is_token_valid) #added
    else:
        is_token_valid = False
        print('User is None, cannot check token.') #added   

    if user is not None and is_token_valid:
        user.userprofile.email_confirmed = True
        user.userprofile.save()
        # Redirect to a success page or render a success template
        return render(request, 'registration/email_confirmed.html')
    else:
        # Email confirmation failed
        return render(request, 'registration/email_confirmation_failed.html', {'user_id': user.id if user else None})

def resend_confirmation_email(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_confirmation_email(user, request)
        messages.success(request, 'تم إرسال بريد التأكيد بنجاح. يرجى التحقق من بريدك الإلكتروني.')
    except User.DoesNotExist:
        messages.error(request, 'حدث خطأ. لم يتم إرسال البريد.')
    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء إرسال البريد: {str(e)}')
    
    # return redirect('/home')  # Redirect to an appropriate view
     # Redirect back to the page that called this function
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('/become_reviewer')

from .forms import *

@login_required
def modify_profile(request):
    # Get translation post IDs for comparison
    translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
    
    # Get all posts and mark which ones are translations
    posts = Post.objects.all()
    for post in posts:
        post.is_translation = post.id in translation_post_ids
        # Add translator field for easy access in template
        if post.is_translation:
            try:
                post.translator = post.translationpost.translator
            except:
                post.translator = ""
    
    # Get drafts (posts with draft status)
    drafts = Post.objects.filter(author=request.user, status='Draft')
    for draft in drafts:
        draft.is_translation = draft.id in translation_post_ids
        if draft.is_translation:
            try:
                draft.translator = draft.translationpost.translator
            except:
                draft.translator = ""
    
    # Get reviewed posts (posts that this user has reviewed)
    reviewed_posts = Post.objects.filter(final_reviewer=request.user).order_by('-updated_at')
    for reviewed_post in reviewed_posts:
        reviewed_post.is_translation = reviewed_post.id in translation_post_ids
        if reviewed_post.is_translation:
            try:
                reviewed_post.translator = reviewed_post.translationpost.translator
            except:
                reviewed_post.translator = ""
    
    # Initialize all forms with current user data
    name_form = ModifyNameForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })
    email_form = ModifyEmailForm(initial={'email': request.user.email}, user=request.user)
    affiliation_form = ModifyAffiliationForm(initial={'affiliation': request.user.userprofile.affiliation})
    country_form = ModifyCountry(initial={'country': request.user.userprofile.country})
    main_category_form = ModifyMainCategoryForm(initial={'main_category': request.user.userprofile.main_category})
    career_form = ModifyCareerForm(initial={'career': request.user.userprofile.career})
    website_form = ModifyWebsiteForm(initial={'website': request.user.userprofile.website})
    who_am_i_form = ModifyWhoAmIForm(initial={'who_am_i': request.user.userprofile.who_am_i})
    
    if request.method == 'POST':
        if 'first_name' in request.POST:
            name_form = ModifyNameForm(request.POST)
            if name_form.is_valid():
                request.user.first_name = name_form.cleaned_data['first_name']
                request.user.last_name = name_form.cleaned_data['last_name']
                request.user.save()
                messages.success(request, 'تم تحديث الاسم بنجاح.')
                return redirect('user_profile')

        elif 'email' in request.POST:
            email_form = ModifyEmailForm(request.POST, user=request.user)
            if email_form.is_valid():
                old_email = request.user.email
                new_email = email_form.cleaned_data['email']
                request.user.email = new_email
                request.user.userprofile.email_confirmed = False
                request.user.save()
                request.user.userprofile.save()
                
                # Send confirmation email to new email
                send_confirmation_email(request.user, request)
                messages.success(request, f'تم تحديث البريد الإلكتروني إلى {new_email}. يرجى تأكيد البريد الإلكتروني الجديد.')
                return redirect('user_profile')

        elif 'affiliation' in request.POST:
            affiliation_form = ModifyAffiliationForm(request.POST)
            if affiliation_form.is_valid():
                request.user.userprofile.affiliation = affiliation_form.cleaned_data['affiliation']
                request.user.userprofile.save()
                return redirect('user_profile')

        elif 'country' in request.POST:
            country_form = ModifyCountry(request.POST)
            if country_form.is_valid():
                request.user.userprofile.country = country_form.cleaned_data['country']
                request.user.userprofile.save()
                return redirect('user_profile')

        elif 'main_category' in request.POST:
            main_category_form = ModifyMainCategoryForm(request.POST)
            if main_category_form.is_valid():
                request.user.userprofile.main_category = main_category_form.cleaned_data['main_category']
                request.user.userprofile.save()
                return redirect('user_profile')

        elif 'career' in request.POST:
            career_form = ModifyCareerForm(request.POST)
            if career_form.is_valid():
                request.user.userprofile.career = career_form.cleaned_data['career']
                request.user.userprofile.save()
                return redirect('user_profile')

        elif 'website' in request.POST:
            website_form = ModifyWebsiteForm(request.POST)
            if website_form.is_valid():
                request.user.userprofile.website = website_form.cleaned_data['website']
                request.user.userprofile.save()
                return redirect('user_profile')

        elif 'who_am_i' in request.POST:
            who_am_i_form = ModifyWhoAmIForm(request.POST)
            if who_am_i_form.is_valid():
                request.user.userprofile.who_am_i = who_am_i_form.cleaned_data['who_am_i']
                request.user.userprofile.save()
                messages.success(request, 'تم تحديث "من أنا" بنجاح.')
                return redirect('user_profile')

    # Superusers automatically have completed profiles, or check if profile is complete
    if request.user.is_superuser or (request.user.userprofile.affiliation != None and request.user.userprofile.country != None and request.user.userprofile.main_category != None):
        request.user.userprofile.completed = True
        request.user.userprofile.save()

    return render(request, 'main/user_profile.html', {"posts":posts,
                                                      "drafts": drafts,
                                                      "reviewed_posts": reviewed_posts,
                                                      'name_form': name_form,
                                                      'email_form': email_form,
                                                      'affiliation_form': affiliation_form,
                                                      'country_form': country_form,
                                                      'main_category_form': main_category_form,
                                                      'career_form': career_form,
                                                      'website_form': website_form,
                                                      'who_am_i_form': who_am_i_form,
                                                      })

def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "إعادة تعيين كلمة المرور"
                    email_template_name = "registration/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'أرشيف العرب',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        messages.error(request, f'حدث خطأ في إرسال البريد الإلكتروني: {e}')
                        return redirect('password_reset')
                    messages.success(request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.')
                    return redirect('login')
            else:
                messages.error(request, 'البريد الإلكتروني غير مسجل في النظام.')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {"form": form})

@login_required
@author_required
def submit_draft(request, post_id):
    """Submit a draft as a regular post"""
    post = get_object_or_404(Post, id=post_id, author=request.user, status='Draft')
    
    if request.method == "POST":
        # Change status from Draft to Pending
        post.status = 'Pending'
        post.save()
        
        # Send thank you email
        send_thank_you_email(request.user, post)
        
        messages.success(request, "تم تقديم المقال بنجاح.")
        return redirect("user_profile")
    
    return redirect("user_profile")

@login_required
@author_required
def submit_translation_draft(request, post_id):
    """Submit a translation draft as a regular translation post"""
    post = get_object_or_404(TranslationPost, id=post_id, author=request.user, status='Draft')
    
    if request.method == "POST":
        # Change status from Draft to Pending
        post.status = 'Pending'
        post.save()
        
        # Send thank you email
        send_thank_you_email(request.user, post)
        
        messages.success(request, "تم تقديم الترجمة بنجاح.")
        return redirect("user_profile")
    
    return redirect("user_profile")

@login_required
@author_required
def request_re_review(request, post_id):
    """Request re-review for a rejected post"""
    post = get_object_or_404(Post, id=post_id, author=request.user, status='Rejected')
    
    if request.method == "POST":
        # Get the current reviewer to exclude them
        current_reviewer = post.reviewer
        
        # Add current reviewer to previous_reviewers if they exist
        if current_reviewer:
            post.previous_reviewers.add(current_reviewer)
        
        # Find available reviewers (excluding all previous reviewers)
        available_reviewers = User.objects.filter(
            groups__name='mod',
            is_active=True
        ).exclude(id__in=post.previous_reviewers.values_list('id', flat=True))
        
        if available_reviewers.exists():
            # Assign a new reviewer randomly
            import random
            new_reviewer = random.choice(available_reviewers)
            
            # Reset the post for re-review
            post.status = 'Pending'
            post.reviewer = new_reviewer
            post.reviewer_comments = ''  # Clear previous review comments
            post.admin_comments = ''     # Clear admin comments
            post.review_started = False  # Reset review started flag
            post.save()
            
            messages.success(request, f"تم طلب إعادة مراجعة المقال. تم تعيين مراجع جديد: {new_reviewer.get_full_name() or new_reviewer.username}")
        else:
            # If no other reviewers available, just reset without assigning
            post.status = 'Pending'
            post.reviewer = None
            post.reviewer_comments = ''
            post.admin_comments = ''
            post.review_started = False  # Reset review started flag
            post.save()
            
            messages.success(request, "تم طلب إعادة مراجعة المقال. سيتم تعيين مراجع جديد قريباً.")
        
        return redirect("user_profile")
    
    return redirect("user_profile")

@login_required
@author_required
def delete_post(request, post_id):
    post = get_object_or_404(Post.objects.select_related('translationpost'), id=post_id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "تم حذف المنشور بنجاح.")
        return redirect("user_profile")

    return redirect("user_profile")

@login_required
@author_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if this is a translation post
    translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
    is_translation = post.id in translation_post_ids
    
    if request.method == "POST":
        if is_translation:
            form = TranslationPostForm(request.POST, request.FILES, instance=post, user=request.user)
        else:
            form = PostForm(request.POST, request.FILES, instance=post)
            
        if form.is_valid():
            # If the post was approved, set it back to pending for re-review
            if post.status == "Approved":
                # Keep the same reviewer for approved posts that are edited
                # Don't add to previous_reviewers since it's the same reviewer
                post.status = "Pending"
                post.reviewer_comments = ""  # Clear previous review comments
                post.review_started = False  # Reset review started flag
                post.is_edited_after_approval = True  # Mark as edited after approval
                messages.success(request, "تم تحديث المنشور بنجاح. سيتم إعادة مراجعته من نفس المراجع.")
            else:
                messages.success(request, "تم تحديث المنشور بنجاح.")
            
            form.save()
            return redirect("user_profile")
    else:
        if is_translation:
            form = TranslationPostForm(instance=post, user=request.user)
        else:
            form = PostForm(instance=post)
    
    return render(request, 'main/edit_post.html', {"form": form, "post": post})
                    
def is_mod_or_staff(user):
    """Check if user is moderator, staff, or superuser"""
    return user.is_superuser or user.is_staff or user.groups.filter(name='mod').exists()

def term_list(request):
    categories = MainCategory.objects.all()
    selected_category_id = request.GET.get('category')
    print(selected_category_id)
    selected_category = "كل التصنيفات"
    

    if selected_category_id:
        selected_category = MainCategory.objects.get(id=selected_category_id)
        keyword_list = KeywordTranslation.objects.filter(category=selected_category, status='approved')
    else:
        keyword_list = KeywordTranslation.objects.filter(status='approved')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return render(request, 'main/authorization_error.html', {
                'error_type': 'login_required',
                'error_title': 'تسجيل الدخول مطلوب',
                'error_message': 'يجب تسجيل الدخول لإضافة مصطلحات جديدة.',
                'action_button_text': 'تسجيل الدخول',
                'action_url': '/login',
                'back_button_text': 'العودة للصفحة الرئيسية',
                'back_url': '/home'
            })
        
        form = KeywordTranslationForm(request.POST)
        if form.is_valid():
            keyword = form.save(commit=False)
            
            if is_mod_or_staff(request.user):
                # User is in "mod" group or is_staff, add the keyword directly as approved
                keyword.status = 'approved'
                keyword.submitted_by = request.user
                keyword.save()
                messages.success(request, 'تم إضافة المصطلح بنجاح!')
            else:
                # User is not in "mod" group or is_staff, save as pending
                keyword.status = 'pending'
                keyword.submitted_by = request.user
                keyword.save()
                
                # Send email to admin
                try:
                    send_mail(
                        'اقتراح مصطلح جديد',
                        f'المستخدم {request.user.username} اقترح مصطلحًا جديدًا:\n\nالمصطلح بالإنجليزية: {keyword.english_keyword}\nالترجمة بالعربية: {keyword.arabic_translation}\nالتصنيف: {keyword.category.name}\n\nيمكنك مراجعة المصطلح في لوحة الإدارة.',
                        'arabarxiv@gmail.com',
                        ['arabarxiv@gmail.com'],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send email: {e}")
                
                messages.success(request, 'تم إرسال اقتراح المصطلح بنجاح! سيتم مراجعته وإضافته إذا كان مناسبًا.')
            
            return redirect('terms')
    else:
        form = KeywordTranslationForm()
    
    context = {
        'categories': categories,
        'selected_category_id': selected_category_id,
        'selected_category_name': selected_category if selected_category else None,
        'keyword_list': keyword_list,
        "form": form
    }
    
    return render(request, 'main/term_list.html', context)

def category_hierarchy(request):
    """Display the hierarchy of categories with post counts"""
    from django.db.models import Count, Q, Prefetch
    
    # Get all main categories
    main_categories = MainCategory.objects.all()
    
    # Get all categories for each main category
    categories_by_main = {}
    
    for main_cat in main_categories:
        # Get ALL categories under this main category (not just root ones)
        categories = Category.objects.filter(main_category=main_cat).annotate(
            post_count=Count('posts', filter=Q(posts__status="Approved"))
        )
        
        # Convert to simple list format for display
        category_list = []
        for cat in categories:
            category_list.append({
                'category': cat,
                'post_count': cat.post_count,
                'total_posts': cat.post_count,  # For flat view, total = direct count
            })
        
        categories_by_main[main_cat] = category_list
        
        # Calculate total posts for main category
        main_cat.total_posts = sum(cat['post_count'] for cat in category_list)
    
    context = {
        'main_categories': main_categories,
        'categories_by_main': categories_by_main,
    }
    
    return render(request, 'main/category_hierarchy.html', context)

from django.db.models import Q
@login_required
@moderator_required
def review_post(request):
    logger.debug(f"Review post view called by {request.user.username} - superuser: {request.user.is_superuser}")
    
    # Check if user is an author (has approved posts) - for template logic
    is_author = Post.objects.filter(author=request.user, status='Approved').exists()
    
    # Superusers see all pending posts, others see only assigned posts
    if request.user.is_superuser:
        assigned_posts = Post.objects.filter(status__in=['Pending', 'Rejected_For_Reassignment'])
        logger.debug(f"Superuser {request.user.username} seeing {assigned_posts.count()} pending posts")
    else:
        assigned_posts = Post.objects.filter(
            Q(reviewer=request.user) | Q(reviewer__isnull=True),
            status__in=['Pending', 'Rejected_For_Reassignment']
        )
        logger.debug(f"Regular user {request.user.username} seeing {assigned_posts.count()} assigned posts")
    
    # Separate queryset for unassigned posts (المشاركات في انتظار المراجعة)
    unassigned_posts = Post.objects.filter(
        Q(status='Pending', reviewer__isnull=True) | 
        Q(status='Rejected_For_Reassignment')
    )

    if request.method == 'POST':
        post_id = request.POST.get('post_id')  # Extract post_id from the form post

        # Get the post to be reviewed - superusers can review any post
        if request.user.is_superuser:
            post = get_object_or_404(Post, pk=post_id, status='Pending')
        else:
            post = get_object_or_404(Post, pk=post_id, reviewer=request.user, status='Pending')

        review_status = request.POST.get('review_status')
        public_comment = request.POST.get('public_comment')
        admin_comment = request.POST.get('admin_comment', '')

        # Save both types of comments first
        post.reviewer_comments = public_comment  # This will be sent to author via email
        post.admin_comments = admin_comment      # This is private, only for admins
        
        # Update the post based on the review status
        if review_status == 'approved':
            post.is_approved = True
            post.status = "Approved"
            post.is_edited_after_approval = False  # Reset edited flag when approved
            post.final_reviewer = request.user  # Set the final reviewer
            # Add the reviewer to previous_reviewers when they complete a review
            post.previous_reviewers.add(request.user)
        elif review_status == 'rejected':
            post.is_approved = False
            post.status = "Rejected"
            post.is_edited_after_approval = False  # Reset edited flag when rejected
            post.final_reviewer = request.user  # Set the final reviewer
            # Add the reviewer to previous_reviewers when they complete a review
            post.previous_reviewers.add(request.user)
        elif review_status == 'rejected_for_reassignment':
            post.is_approved = False
            post.status = "Rejected_For_Reassignment"
            post.is_edited_after_approval = False  # Reset edited flag when rejected
            # Don't set final_reviewer as this post will be reassigned
            # Add current reviewer to previous_reviewers and clear current reviewer
            post.previous_reviewers.add(request.user)
            post.reviewer = None
            post.review_started = False
        
        # Save the post with all changes
        post.save()
        
        # Send email after saving the comments
        if review_status == 'approved':
            send_accepted(post.author, post)
        elif review_status == 'rejected':
            send_rejected(post.author, post)
        return redirect("/review")

    # Get moderators for the template
    mod_group = Group.objects.get(name='mod')
    moderators = User.objects.filter(Q(groups=mod_group) | Q(is_staff=True) | Q(is_superuser=True))

    context = {
       "posts": assigned_posts,
       "unassigned_posts": unassigned_posts,  # Separate queryset for unassigned posts
       "moderators": moderators,
       "is_author": is_author
    }

    return render(request, 'main/review.html', context)

@login_required
@moderator_required
def start_reviewing(request, post_id):
    """Start reviewing a specific post - moves it to 'in review' state"""
    if request.method == 'POST':
        # Get the post to be reviewed
        if request.user.is_superuser:
            post = get_object_or_404(Post, pk=post_id, status__in=['Pending', 'Rejected_For_Reassignment'])
        else:
            post = get_object_or_404(Post, pk=post_id, reviewer=request.user, status__in=['Pending', 'Rejected_For_Reassignment'])
        
        # Mark the post as being reviewed by this user
        post.reviewer = request.user
        post.review_started = True
        post.save()
        
        messages.success(request, f'تم بدء مراجعة المشاركة: {post.title}')
        return redirect('/review')
    
    return redirect('/review')

@login_required
@moderator_required
def detailed_review(request, post_id):
    """Detailed review page for a specific post"""
    # Get the post to be reviewed
    if request.user.is_superuser:
        post = get_object_or_404(Post, pk=post_id, status__in=['Pending', 'Rejected_For_Reassignment'])
    else:
        post = get_object_or_404(Post, pk=post_id, reviewer=request.user, status__in=['Pending', 'Rejected_For_Reassignment'])
    
    if request.method == 'POST':
        review_status = request.POST.get('review_status')
        public_comment = request.POST.get('public_comment')
        admin_comment = request.POST.get('admin_comment', '')
        best_article_month = request.POST.get('best_article_month') == 'on'  # Checkbox returns 'on' when checked

        # Save both types of comments first
        post.reviewer_comments = public_comment  # This will be sent to author via email
        post.admin_comments = admin_comment      # This is private, only for admins
        
        # Save the best article recommendation
        post.recommended_for_best_article = best_article_month
        
        # Update the post based on the review status
        if review_status == 'approved':
            post.is_approved = True
            post.status = "Approved"
            post.is_edited_after_approval = False  # Reset edited flag when approved
            post.final_reviewer = request.user  # Set the final reviewer
            # Add the reviewer to previous_reviewers when they complete a review
            post.previous_reviewers.add(request.user)
        elif review_status == 'rejected':
            post.is_approved = False
            post.status = "Rejected"
            post.is_edited_after_approval = False  # Reset edited flag when rejected
            post.final_reviewer = request.user  # Set the final reviewer
            # Add the reviewer to previous_reviewers when they complete a review
            post.previous_reviewers.add(request.user)
        elif review_status == 'rejected_for_reassignment':
            post.is_approved = False
            post.status = "Rejected_For_Reassignment"
            post.is_edited_after_approval = False  # Reset edited flag when rejected
            # Don't set final_reviewer as this post will be reassigned
            # Add current reviewer to previous_reviewers and clear current reviewer
            post.previous_reviewers.add(request.user)
            post.reviewer = None
            post.review_started = False
        
        # Save the post with all changes
        post.save()
        
        # Send email after saving the comments
        if review_status == 'approved':
            send_accepted(post.author, post)
        elif review_status == 'rejected':
            send_rejected(post.author, post)
        
        messages.success(request, f'تم إرسال مراجعة المشاركة: {post.title}')
        return redirect("/review")

    context = {
        'post': post
    }
    
    return render(request, 'main/detailed_review.html', context)

@login_required
def become_reviewer(request):
    print(f"become_reviewer called by user: {request.user.username}")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")
    
    if request.method == 'POST':
        print(f"Processing POST request for reviewer application")
        
        # Check if user has confirmed email (superusers bypass this check)
        if not request.user.is_superuser and hasattr(request.user, 'userprofile') and not request.user.userprofile.email_confirmed:
            messages.warning(request, 'يرجى تأكيد بريدك الإلكتروني أولاً قبل طلب أن تصبح مراجعًا.')
            return redirect('/become_reviewer')
        
        # Check if user has at least one approved post (superusers bypass this check)
        if not request.user.is_superuser:
            approved_posts_count = Post.objects.filter(author=request.user, status='Approved').count()
            if approved_posts_count == 0:
                messages.warning(request, 'يجب أن يكون لديك مقال واحد على الأقل مقبول للنشر قبل طلب أن تصبح مراجعًا. يرجى تقديم مقالك الأول أولاً.')
                return redirect('/become_reviewer')
        
        # Check if user already has a pending request
        from .models import ReviewerRequest
        existing_request = ReviewerRequest.objects.filter(user=request.user, status='pending').first()
        
        if existing_request:
            print(f"User {request.user.username} already has pending request")
            messages.warning(request, 'لديك طلب قيد الانتظار بالفعل.')
            return redirect('/review')
        
        # Check if user is already a moderator (but allow superusers to submit requests for testing)
        if is_mod_or_staff(request.user) and not request.user.is_superuser:
            print(f"User {request.user.username} is already a moderator")
            messages.info(request, 'أنت مراجع بالفعل.')
            return redirect('/review')
        
        # Debug: Check superuser status
        if request.user.is_superuser:
            print(f"Superuser {request.user.username} is submitting reviewer request")
        
        # Create new reviewer request
        print(f"Creating new reviewer request for user: {request.user.username}")
        reviewer_request = ReviewerRequest.objects.create(user=request.user)
        print(f"Reviewer request created with ID: {reviewer_request.id}")
        
        # Send email to admin (optional - don't let it break the request)
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            admin_message = f"""
            أحدهم طلب أن يصبح مراجعا:
            
            المستخدم: {request.user.username}
            الاسم: {request.user.first_name} {request.user.last_name}
            البريد الإلكتروني: {request.user.email}
            تاريخ الطلب: {reviewer_request.request_date}
            
            للرد على الطلب، يرجى الذهاب إلى لوحة الإدارة.
            """
            
            send_mail(
                'أحدهم طلب أن يصبح مراجعا',
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                ['arabarxiv@gmail.com'],  # Admin email
                fail_silently=True,  # Changed to True to prevent errors
            )
            print(f"Email sent successfully for reviewer request from {request.user.username}")
        except Exception as e:
            # If email fails, still create the request but log the error
            print(f"Failed to send email for reviewer request: {e}")
            # Don't let email failure break the request creation
        
        messages.success(request, 'تم إرسال طلبك لتصبح مراجعًا بنجاح. سيتم مراجعته من قبل الإدارة.')
        return redirect('/review')

    # Get context for the template
    from .models import ReviewerRequest
    
    # Check if user has a pending request
    has_pending_request = ReviewerRequest.objects.filter(user=request.user, status='pending').exists()
    
    # Check if user is already a moderator
    is_moderator = is_mod_or_staff(request.user)
    
    # Check user's eligibility status
    email_confirmed = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.email_confirmed)
    profile_completed = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.completed)
    has_approved_post = request.user.is_superuser or Post.objects.filter(author=request.user, status='Approved').exists()
    
    context = {
        'has_pending_request': has_pending_request,
        'is_moderator': is_moderator,
        'email_confirmed': email_confirmed,
        'profile_completed': profile_completed,
        'has_approved_post': has_approved_post,
        'approved_posts_count': Post.objects.filter(author=request.user, status='Approved').count(),
    }
    
    return render(request, 'main/become_reviewer.html', context)

@login_required
@moderator_required
def assign_mod(request):
    logger.debug(f"Assign mod view called by {request.user.username} - superuser: {request.user.is_superuser}")
    if request.method == 'POST':
        post_id = request.POST.get('post_id')  # Extract post_id from the form post
        logger.debug(f"POST data: {request.POST}")
        logger.debug(f"post_id: {post_id}")
        
        if not post_id:
            messages.error(request, "لم يتم تحديد المقال.")
            return redirect("/review")

        # Get the selected moderator's ID
        moderator_id = request.POST.get(f'moderator_{post_id}')
        logger.debug(f"moderator_id for post {post_id}: {moderator_id}")
        
        if not moderator_id:
            messages.error(request, "لم يتم تحديد المراجع.")
            return redirect("/review")

        try:
            # Get the post to be assigned based on the post_id
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            messages.error(request, "المقال غير موجود.")
            return redirect("/review")

        try:
            # Get the selected moderator based on the moderator_id
            moderator = User.objects.get(pk=moderator_id)
        except User.DoesNotExist:
            messages.error(request, "المراجع غير موجود.")
            return redirect("/review")

        # Check if this moderator has already reviewed this post
        if post.previous_reviewers.filter(id=moderator.id).exists():
            messages.error(request, f"لا يمكن تعيين {moderator.username} مرة أخرى لأنه قام بمراجعة هذا المقال سابقاً.")
            return redirect("/review")

        # If there was a previous reviewer, add them to previous_reviewers
        if post.reviewer and post.reviewer != moderator:
            post.previous_reviewers.add(post.reviewer)

        # Assign the selected moderator to the post
        post.reviewer = moderator
        post.status = "Pending"  # Reset to Pending when reassigned
        post.review_started = False  # Reset review started flag
        post.save()

        messages.success(request, f"تم تعيين {moderator.username} لمراجعة المقال بنجاح.")
        return redirect("/review")

    # Superusers can assign any post, others only their assigned posts
    if request.user.is_superuser:
        assigned_posts = Post.objects.filter(status__in=['Pending', 'Rejected_For_Reassignment'])
        logger.debug(f"Superuser {request.user.username} seeing {assigned_posts.count()} posts for assignment")
    else:
        assigned_posts = Post.objects.filter(reviewer=request.user, status__in=['Pending', 'Rejected_For_Reassignment'])
        logger.debug(f"Regular user {request.user.username} seeing {assigned_posts.count()} posts for assignment")
        
    mod_group = Group.objects.get(name='mod')
    # Get users in the "mod" group
    mod_users = User.objects.filter(Q(groups=mod_group) | Q(is_staff=True))

    context = {
        "posts": assigned_posts,
        "moderators": mod_users
    }

    return render(request, 'main/review.html', context)


from .forms import BibTexForm
from .utils import format_bibtex_for_arabic  # Assuming you have a utility function for formatting

def bibtex_converter(request):
    formatted_bibtex = ""
    if request.method == 'POST':
        form = BibTexForm(request.POST)
        if form.is_valid():
            bibtex_input = form.cleaned_data['bibtex_input']
            formatted_bibtex = format_bibtex_for_arabic(bibtex_input)
    else:
        form = BibTexForm()

    return render(request, 'main/bibtex_converter.html', {'form': form, 'formatted_bibtex': formatted_bibtex})

def custom_403_error(request, exception=None):
    """Custom 403 Forbidden error handler"""
    if not request.user.is_authenticated:
        return render(request, 'main/authorization_error.html', {
            'error_type': 'login_required',
            'error_title': 'تسجيل الدخول مطلوب',
            'error_message': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة.',
            'action_button_text': 'تسجيل الدخول',
            'action_url': '/login',
            'back_button_text': 'العودة للصفحة الرئيسية',
            'back_url': '/home'
        })
    else:
        return render(request, 'main/authorization_error.html', {
            'error_type': 'permission_denied',
            'error_title': 'صلاحيات غير كافية',
            'error_message': 'ليس لديك الصلاحيات الكافية للوصول إلى هذه الصفحة.',
            'action_button_text': 'العودة للصفحة الرئيسية',
            'action_url': '/home',
            'back_button_text': 'تواصل معنا',
            'back_url': '/contact'
        })



def check_reviewer_request_status(request):
    """Check the status of user's reviewer request"""
    if not request.user.is_authenticated:
        return redirect('/login')
    
    from .models import ReviewerRequest
    try:
        reviewer_request = ReviewerRequest.objects.filter(user=request.user).latest('request_date')
        return render(request, 'main/reviewer_request_status.html', {
            'reviewer_request': reviewer_request
        })
    except ReviewerRequest.DoesNotExist:
        return render(request, 'main/reviewer_request_status.html', {
            'reviewer_request': None,
            'no_requests': True
        })

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        messages.success(request, 'تم إعادة تعيين كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة.')
        return redirect('login')

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    
    # Get translation post IDs for comparison
    translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
    
    # Mark if this post is a translation and add translator field
    post.is_translation = post.id in translation_post_ids
    if post.is_translation:
        try:
            post.translator = post.translationpost.translator
        except:
            post.translator = ""
    
    # Record view if user is authenticated
    if request.user.is_authenticated:
        PostView.objects.get_or_create(post=post, user=request.user)
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail_by_meaningful_id', meaningful_id=post.meaningful_id)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'main/post_detail.html', context)

def post_detail_by_meaningful_id(request, meaningful_id):
    """View post by meaningful ID (e.g., '2.9.15')"""
    try:
        # Parse the meaningful ID to extract main_category, sub_category, and sequence
        parts = meaningful_id.split('.')
        if len(parts) != 3:
            raise Http404("Invalid meaningful ID format")
        
        main_category_id, sub_category_id, sequence = parts
        
        # Find the post by matching the meaningful ID
        post = get_object_or_404(Post, meaningful_id=meaningful_id)
        
        comments = post.comments.all()
        
        # Get translation post IDs for comparison
        translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
        
        # Mark if this post is a translation and add translator field
        post.is_translation = post.id in translation_post_ids
        if post.is_translation:
            try:
                post.translator = post.translationpost.translator
            except:
                post.translator = ""
        
        # Record view if user is authenticated
        if request.user.is_authenticated:
            PostView.objects.get_or_create(post=post, user=request.user)
        
        if request.method == 'POST' and request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('post_detail_by_meaningful_id', meaningful_id=meaningful_id)
        else:
            comment_form = CommentForm()
        
        context = {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        }
        return render(request, 'main/post_detail.html', context)
        
    except (ValueError, IndexError):
        raise Http404("Invalid meaningful ID format")

@login_required
def edit_comment(request, comment_id):
    """Edit a comment - only the author can edit their own comments"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user is the author of the comment
    if comment.author != request.user:
        messages.error(request, 'لا يمكنك تعديل تعليق شخص آخر.')
        return redirect('post_detail_by_meaningful_id', meaningful_id=comment.post.meaningful_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_modified = True
            comment.save()
            messages.success(request, 'تم تعديل التعليق بنجاح.')
            return redirect('post_detail_by_meaningful_id', meaningful_id=comment.post.meaningful_id)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'main/edit_comment.html', context)

@login_required
def delete_comment(request, comment_id):
    """Delete a comment - author can delete their own comments, superusers and mods can delete any comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user can delete this comment
    can_delete = (
        comment.author == request.user or  # Author can delete their own comment
        request.user.is_superuser or       # Superuser can delete any comment
        is_mod_or_staff(request.user)      # Moderators can delete any comment
    )
    
    if not can_delete:
        messages.error(request, 'لا يمكنك حذف هذا التعليق.')
        return redirect('post_detail_by_meaningful_id', meaningful_id=comment.post.meaningful_id)
    
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'تم حذف التعليق بنجاح.')
        return redirect('post_detail_by_meaningful_id', meaningful_id=comment.post.meaningful_id)
    
    context = {
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'main/delete_comment.html', context)

def find_user_by_name(request, author_name):
    """Find a user by their display name and redirect to their profile"""
    # Clean the author name
    author_name = author_name.strip()
    
    # Try to find user by first_name + last_name
    try:
        # Split the name into parts
        name_parts = author_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
            
            # Try to find user by first_name and last_name
            user = User.objects.get(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                is_superuser=False
            )
            return redirect('public_profile', user_id=user.id)
        else:
            # Try to find by username if it's a single word
            user = User.objects.get(username__iexact=author_name, is_superuser=False)
            return redirect('public_profile', user_id=user.id)
    except User.DoesNotExist:
        # If no user found, redirect to search results with the author name
        return redirect(f'/search_results?searchKeyword={author_name}')
    except User.MultipleObjectsReturned:
        # If multiple users found, redirect to search results
        return redirect(f'/search_results?searchKeyword={author_name}')

def newsletter_signup(request):
    """Handle newsletter signup"""
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            # Generate confirmation token
            import secrets
            token = secrets.token_urlsafe(32)
            
            # Create subscriber with confirmation token
            subscriber = form.save(commit=False)
            subscriber.confirmation_token = token
            subscriber.save()
            
            # Send confirmation email
            subject = "تأكيد الاشتراك في النشرة الإخبارية - أراب أركسيف"
            email_template_name = "main/newsletter_confirmation_email.html"
            context = {
                "subscriber": subscriber,
                "token": token,
                'domain': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
            }
            email = render_to_string(email_template_name, context)
            
            try:
                send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [subscriber.email], fail_silently=False)
                messages.success(request, 'تم إرسال رابط التأكيد إلى بريدك الإلكتروني. يرجى التحقق من بريدك وتأكيد الاشتراك.')
            except Exception as e:
                messages.error(request, f'حدث خطأ في إرسال بريد التأكيد: {e}')
            
            return redirect('real_home')
    else:
        form = NewsletterSignupForm()
    
    return render(request, 'main/newsletter_signup.html', {'form': form})

def confirm_newsletter_signup(request, token):
    """Confirm newsletter signup"""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token, is_confirmed=False)
        subscriber.is_confirmed = True
        subscriber.confirmation_token = ''  # Clear the token
        subscriber.save()
        
        messages.success(request, 'تم تأكيد اشتراكك في النشرة الإخبارية بنجاح!')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'رابط التأكيد غير صحيح أو منتهي الصلاحية.')
    
    return redirect('real_home')

def unsubscribe_newsletter(request, token):
    """Unsubscribe from newsletter"""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token, is_active=True)
        subscriber.is_active = False
        subscriber.save()
        
        messages.success(request, 'تم إلغاء اشتراكك في النشرة الإخبارية بنجاح.')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'رابط إلغاء الاشتراك غير صحيح أو منتهي الصلاحية.')
    
    return redirect('real_home')

def newsletter_test(request):
    """Test page for newsletter signup"""
    return render(request, 'main/newsletter_test.html')


def download_pdf(request, post_id):
    """Handle PDF downloads and increment view counter"""
    post = get_object_or_404(Post, id=post_id)
    
    # Increment PDF view counter
    if request.user.is_authenticated:
        post.add_pdf_view(request.user)
    
    # Redirect to the actual PDF file
    if post.pdf:
        return redirect(post.pdf.url)
    else:
        raise Http404("PDF not found")
