from django.contrib.auth.models import User
from .models import Post  # Replace with your actual Post model

def review_count_processor(request):
    if request.user.is_authenticated:
        # Count the number of posts where the current user is the reviewer
        count = 0 
        if request.user.is_staff:
            count += Post.objects.filter(status="Pending").count()
        else:
            count += Post.objects.filter(reviewer=request.user, status="Pending").count()
        return {'reviews_count': count}
    return {'reviews_count': 0}