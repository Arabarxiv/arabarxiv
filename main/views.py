from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post, KeywordTranslation, MainCategory, Category, TranslationPost
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

# Custom authorization decorators
def email_confirmation_required(view_func):
    """Decorator to check if user's email is confirmed"""
    def _wrapped_view_func(request, *args, **kwargs):
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
from django.utils.encoding import force_bytes
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
    Q(title__icontains=query) | Q(authors__icontains=query),is_approved=True
    )
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
    subject = 'شكرًا لك على مشاركتك, {}'.format(user.first_name)
    html_content = render_to_string('emails/post_accepted_email.html', {
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

def send_rejected(user, post):
    subject = 'شكرًا لك على مشاركتك, {}'.format(user.first_name)
    html_content = render_to_string('emails/post_rejected_email.html', {
        'user': user,
        'post_title': post.title,
        'post_comments': post.comments,
        'site_url': 'http://www.arabarxiv.org'  # Replace with your website URL
    })
    text_content = strip_tags(html_content)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    email = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()

def home(request):
    posts = Post.objects.all()
    translation_post_ids = TranslationPost.objects.values_list('post_ptr_id', flat=True)
    for post in posts:
        post.is_translation = post.id in translation_post_ids
    categories = MainCategory.objects.all()

    return render(request, 'main/home.html', {"posts": posts,
                                              "categories":categories})

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

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            send_thank_you_email(request.user, post)
            return redirect("/user_profile")
    else:
        form = PostForm()

    return render(request, 'main/create_post.html', {"form": form})

from django.http import JsonResponse
def get_categories(request):
    trigger_value = request.GET.get('trigger_value')
    # Your logic here to determine categories based on trigger_value
    categories = list(Category.objects.values('id', 'name'))
    return JsonResponse({'categories': categories})




@login_required(login_url="/login")
@email_confirmation_required
@permission_required("main.add_translationpost", login_url="/login", raise_exception=True)  # Update permission
def create_translation_post(request):
    if request.method == 'POST':
        form = TranslationPostForm(request.POST, request.FILES)
        if form.is_valid():
            translation_post = form.save(commit=False)
            translation_post.author = request.user  # Set the author as the current user
            translation_post.save()
            send_thank_you_email(request.user, translation_post)  # Send a thank you email
            return redirect("/user_profile")  # Redirect to a relevant page after saving
    else:
        form = TranslationPostForm()  # Initialize an empty form for GET request

    return render(request, 'main/create_translation_post.html', {"form": form})  # Render the specific template for creating a translation post

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
        messages.success(request, 'تم إعادة إرسال بريد التأكيد.')
    except User.DoesNotExist:
        messages.error(request, 'حدث خطأ. لم يتم إرسال البريد.')
    
    return redirect('/home')  # Redirect to an appropriate view

from .forms import *

@login_required
def modify_profile(request):
    posts = Post.objects.all()
    if request.method == 'POST':
        if 'affiliation' in request.POST:
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

    else:
        affiliation_form = ModifyAffiliationForm(initial={'affiliation': request.user.userprofile.affiliation})
        country_form = ModifyCountry(initial={'country': request.user.userprofile.country})
        main_category_form = ModifyMainCategoryForm(initial={'main_category': request.user.userprofile.main_category})
        career_form = ModifyCareerForm(initial={'career': request.user.userprofile.career})
        website_form = ModifyWebsiteForm(initial={'website': request.user.userprofile.website})

    if request.user.userprofile.affiliation != None and request.user.userprofile.country != None and request.user.userprofile.main_category != None:
        request.user.userprofile.completed = True
        request.user.userprofile.save()

    return render(request, 'main/user_profile.html', {"posts":posts,
                                                      'affiliation_form': affiliation_form,
                                                      'country_form': country_form,
                                                      'main_category_form': main_category_form,
                                                      'career_form': career_form,
                                                      'website_form': website_form, 
                                                      })
                                                    

@login_required
@author_required
def delete_post(request, post_id):
    post = get_object_or_404(Post.objects.select_related('translationpost'), id=post_id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "تم حذف المنشور بنجاح.")
        return redirect("user_profile")

    return redirect("user_profile")
                    
def is_mod_or_staff(user):
    return user.groups.filter(name='mod').exists() or user.is_staff

def term_list(request):
    categories = MainCategory.objects.all()
    selected_category_id = request.GET.get('category')
    print(selected_category_id)
    selected_category = "كل التصنيفات"
    

    if selected_category_id:
        selected_category = MainCategory.objects.get(id=selected_category_id)
        keyword_list = KeywordTranslation.objects.filter(category=selected_category)
    else:
        keyword_list = KeywordTranslation.objects.all()

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
        
        if is_mod_or_staff(request.user):
            # User is in "mod" group or is_staff, add the keyword directly
            form = KeywordTranslationForm(request.POST)
            if form.is_valid():
                form.save()
                # Redirect to the same page or another appropriate page
                return redirect('terms')
        else:
            # User is not in "mod" group or is_staff, send email to admin and notify the user
            form = KeywordTranslationForm(request.POST)
            if form.is_valid():
                keyword = form.save(commit=False)
                send_mail(
                    'اقتراح مصطلح جديد',
                    f'المستخدم {request.user.username} اقترح مصطلحًا جديدًا: {keyword.english_keyword} - {keyword.arabic_translation}',
                    'arabarxiv@gmail.com',  # Replace with your admin's email address
                    ['arabarxiv@gmail.com'],  # Replace with your admin's email address
                    fail_silently=False,
                )
                messages.warning(request, 'تم إرسال اقتراح المصطلح إلى الإدارة. سيتم مراجعته وإضافته إذا كان مناسبًا.')
                # Redirect to the same page or another appropriate page
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

from django.db.models import Q
@login_required
@moderator_required
def review_post(request):
    # Assuming you have a way to identify the current reviewer (e.g., request.user)
    current_reviewer = request.user  # You may need to adjust this based on your user model
    assigned_posts = Post.objects.all()
    mod_group = Group.objects.get(name='mod')
    is_author = Post.objects.filter(author=request.user, status='Approved').exists()

    # Get users in the "mod" group
    mod_users = User.objects.filter(Q(groups=mod_group) | Q(is_staff=True))

    if request.method == 'POST':
        post_id = request.POST.get('post_id')  # Extract post_id from the form post

        # Get the post to be reviewed based on the post_id
        post = get_object_or_404(Post, pk=post_id, reviewer=current_reviewer)

        review_status = request.POST.get('review_status')
        review_comment = request.POST.get('review_comment')

        # Update the post based on the review status and comment
        if review_status == 'approved':
            post.is_approved = True
            post.status = "Approved"
            send_accepted(post.author, post)
        elif review_status == 'rejected':
            post.is_approved = False
            post.status = "Rejected"
            send_rejected(post.author, post)
        post.reviewer_comments = review_comment
        
        post.save()
        redirect("/review")

    context = {
       "posts": assigned_posts, 
       "moderators":mod_users, 
       "is_author": is_author
    }

    return render(request, 'main/review.html', context)

@login_required
@email_confirmation_required
def become_reviewer(request):
    if request.method == 'POST':
        # Check if user already has a pending request
        from .models import ReviewerRequest
        existing_request = ReviewerRequest.objects.filter(user=request.user, status='pending').first()
        
        if existing_request:
            messages.warning(request, 'لديك طلب قيد الانتظار بالفعل.')
            return redirect('/home')
        
        # Check if user is already a moderator
        if is_mod_or_staff(request.user):
            messages.info(request, 'أنت مراجع بالفعل.')
            return redirect('/home')
        
        # Create new reviewer request
        reviewer_request = ReviewerRequest.objects.create(user=request.user)
        
        # Send email to admin
        from django.core.mail import send_mail
        from django.conf import settings
        admin_message = f"""
        طلب جديد لتصبح مراجعًا:
        
        المستخدم: {request.user.username}
        الاسم: {request.user.first_name} {request.user.last_name}
        البريد الإلكتروني: {request.user.email}
        تاريخ الطلب: {reviewer_request.request_date}
        
        للرد على الطلب، يرجى الذهاب إلى لوحة الإدارة.
        """
        
        try:
            send_mail(
                'طلب جديد لتصبح مراجعًا',
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                ['arabarxiv@gmail.com'],  # Admin email
                fail_silently=False,
            )
        except Exception as e:
            # If email fails, still create the request but log the error
            print(f"Failed to send email: {e}")
        
        messages.success(request, 'تم إرسال طلبك لتصبح مراجعًا بنجاح. سيتم مراجعته من قبل الإدارة.')
        return redirect('/home')

    return render(request, 'main/real_home.html')

@login_required
@moderator_required
def assign_mod(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')  # Extract post_id from the form post

        # Get the selected moderator's ID
        moderator_id = request.POST.get(f'moderator_{post_id}')

        # Get the post to be assigned based on the post_id
        post = Post.objects.get(pk=post_id)

        # Get the selected moderator based on the moderator_id
        moderator = User.objects.get(pk=moderator_id)

        # Assign the selected moderator to the post
        post.reviewer = moderator
        post.status = "Pending"
        post.save()

        return redirect("/review")

    # Assuming you have a way to identify the current reviewer (e.g., request.user)
    current_reviewer = request.user  # You may need to adjust this based on your user model
    assigned_posts = Post.objects.all()
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

def test_authorization(request):
    """Test view to demonstrate different authorization scenarios"""
    if not request.user.is_authenticated:
        return render(request, 'main/authorization_error.html', {
            'error_type': 'login_required',
            'error_title': 'تسجيل الدخول مطلوب',
            'error_message': 'هذه صفحة اختبار للصلاحيات. يجب تسجيل الدخول للوصول إليها.',
            'action_button_text': 'تسجيل الدخول',
            'action_url': '/login',
            'back_button_text': 'العودة للصفحة الرئيسية',
            'back_url': '/home'
        })
    
    if not request.user.userprofile.email_confirmed:
        return render(request, 'main/authorization_error.html', {
            'error_type': 'email_not_confirmed',
            'error_title': 'تأكيد البريد الإلكتروني مطلوب',
            'error_message': 'هذه صفحة اختبار للصلاحيات. يجب تأكيد بريدك الإلكتروني.',
            'action_button_text': 'إعادة إرسال بريد التأكيد',
            'action_url': f'/resend-confirmation-email/{request.user.id}/',
            'back_button_text': 'العودة للصفحة الرئيسية',
            'back_url': '/home'
        })
    
    if not is_mod_or_staff(request.user):
        return render(request, 'main/authorization_error.html', {
            'error_type': 'moderator_required',
            'error_title': 'صلاحيات المراجع مطلوبة',
            'error_message': 'هذه صفحة اختبار للصلاحيات. يجب أن تكون مراجعًا.',
            'action_button_text': 'طلب أن تصبح مراجعًا',
            'action_url': '/become_reviewer',
            'back_button_text': 'العودة للصفحة الرئيسية',
            'back_url': '/home'
        })
    
    # If all checks pass, show success message
    return render(request, 'main/authorization_success.html', {
        'message': 'تم اجتياز جميع اختبارات الصلاحيات بنجاح!'
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
        messages.info(request, 'لا توجد طلبات مراجع لك.')
        return redirect('/home')
