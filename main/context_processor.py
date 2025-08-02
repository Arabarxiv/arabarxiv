from django.contrib.auth.models import User
from .models import Post, ReviewerRequest  # Replace with your actual Post model

def review_count_processor(request):
    if request.user.is_authenticated:
        # Count the number of posts where the current user is the reviewer
        count = 0 
        if request.user.is_staff:
            count += Post.objects.filter(status="Pending").count()
        else:
            count += Post.objects.filter(reviewer=request.user, status="Pending").count()
        
        # Check for pending reviewer requests
        has_pending_reviewer_request = ReviewerRequest.objects.filter(
            user=request.user, 
            status='pending'
        ).exists()
        
        # Determine active submission type based on current URL
        active_submission_type = None
        if request.path == '/create-post':
            active_submission_type = 'original_post'
        elif request.path == '/create-translation-post':
            active_submission_type = 'translation_post'
        
        return {
            'reviews_count': count,
            'has_pending_reviewer_request': has_pending_reviewer_request,
            'active_submission_type': active_submission_type
        }
    return {
        'reviews_count': 0, 
        'has_pending_reviewer_request': False,
        'active_submission_type': None
    }