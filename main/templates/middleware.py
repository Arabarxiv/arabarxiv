from django.shortcuts import render
from django.urls import resolve
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)

class AuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass all checks for superusers
        if request.user.is_authenticated and request.user.is_superuser:
            logger.debug(f"Superuser {request.user.username} bypassing all middleware checks")
            return self.get_response(request)
            
        # List of URLs that require email confirmation
        email_confirmation_required_urls = [
            'create_post',
            'create_translation_post',
            'become_reviewer',
        ]
        
        # List of URLs that require login
        login_required_urls = [
            'user_profile',
            'delete_post',
            'edit_post',
        ]
        
        if request.user.is_authenticated:
            # Get current URL name
            try:
                current_url_name = resolve(request.path_info).url_name
            except:
                current_url_name = None
            
            # Check email confirmation for specific URLs
            if current_url_name in email_confirmation_required_urls:
                if not request.user.userprofile.email_confirmed:
                    return render(request, 'main/authorization_error.html', {
                        'error_type': 'email_not_confirmed',
                        'error_title': 'تأكيد البريد الإلكتروني مطلوب',
                        'error_message': 'يجب تأكيد بريدك الإلكتروني قبل الوصول إلى هذه الصفحة.',
                        'action_button_text': 'إعادة إرسال بريد التأكيد',
                        'action_url': f'/resend-confirmation-email/{request.user.id}/',
                        'back_button_text': 'العودة للصفحة الرئيسية',
                        'back_url': '/home'
                    })
        
        else:
            # Check if user is not authenticated for login-required URLs
            try:
                current_url_name = resolve(request.path_info).url_name
            except:
                current_url_name = None
            
            if current_url_name in login_required_urls + email_confirmation_required_urls:
                return render(request, 'main/authorization_error.html', {
                    'error_type': 'login_required',
                    'error_title': 'تسجيل الدخول مطلوب',
                    'error_message': 'يجب تسجيل الدخول للوصول إلى هذه الصفحة.',
                    'action_button_text': 'تسجيل الدخول',
                    'action_url': '/login',
                    'back_button_text': 'العودة للصفحة الرئيسية',
                    'back_url': '/home'
                })
        
        response = self.get_response(request)
        return response
    
    def is_mod_or_staff(self, user):
        """Check if user is moderator, staff, or superuser"""
        return user.is_superuser or user.is_staff or user.groups.filter(name='mod').exists() 