from django import template
from datetime import datetime, timezone
from django.utils import timezone as django_timezone

register = template.Library()
import re

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user belongs to a specific group"""
    return user.groups.filter(name=group_name).exists()

@register.filter
def count_approved_posts_in_category(posts, category):
    return sum(1 for post in posts if post.status == "Approved" and post.category.main_category.id == category.id)

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add CSS class to a form field"""
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='split')
def split_string(value, key):
    delimiters = [',', '،']
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, value)

@register.filter(name='strip')
def strip(value):
    return value.strip()

@register.filter(name='can_manage_comment')
def can_manage_comment(user, comment):
    """Check if user can manage (edit/delete) a comment"""
    from main.views import is_mod_or_staff
    return comment.author == user or user.is_superuser or is_mod_or_staff(user)

@register.filter(name='can_edit_comment')
def can_edit_comment(user, comment):
    """Check if user can edit a comment (only the author can edit)"""
    return comment.author == user

@register.filter(name='find_user_by_name')
def find_user_by_name(author_name):
    """Find a user by their full name or username"""
    from django.contrib.auth.models import User
    
    # Try to find by full name first
    for user in User.objects.all():
        full_name = f"{user.first_name} {user.last_name}".strip()
        if full_name == author_name:
            return user
        elif user.username == author_name:
            return user
    
    return None

@register.filter(name='user_exists')
def user_exists(author_name):
    """Check if a user exists in our platform by name"""
    from django.contrib.auth.models import User
    
    author_name = author_name.strip()
    
    # Try to find by full name first
    for user in User.objects.all():
        full_name = f"{user.first_name} {user.last_name}".strip()
        if full_name == author_name:
            return True
        elif user.username == author_name:
            return True
    
    return False

@register.filter(name='class_name')
def class_name(obj):
    """Get the class name of an object"""
    return obj.__class__.__name__

@register.filter(name='time_elapsed')
def time_elapsed(date):
    """Calculate and return time elapsed since the given date in Arabic"""
    if not date:
        return ""
    
    now = django_timezone.now()
    if date.tzinfo is None:
        date = django_timezone.make_aware(date)
    
    delta = now - date
    
    # Convert to total seconds
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return "الآن"
    elif total_seconds < 3600:  # Less than 1 hour
        minutes = total_seconds // 60
        if minutes == 1:
            return "منذ دقيقة واحدة"
        else:
            return f"منذ {minutes} دقيقة"
    elif total_seconds < 86400:  # Less than 1 day
        hours = total_seconds // 3600
        if hours == 1:
            return "منذ ساعة واحدة"
        else:
            return f"منذ {hours} ساعة"
    elif total_seconds < 2592000:  # Less than 30 days
        days = total_seconds // 86400
        if days == 1:
            return "منذ يوم واحد"
        else:
            return f"منذ {days} يوم"
    elif total_seconds < 31536000:  # Less than 1 year
        months = total_seconds // 2592000
        if months == 1:
            return "منذ شهر واحد"
        else:
            return f"منذ {months} شهر"
    else:  # More than 1 year
        years = total_seconds // 31536000
        if years == 1:
            return "منذ سنة واحدة"
        else:
            return f"منذ {years} سنة"

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)