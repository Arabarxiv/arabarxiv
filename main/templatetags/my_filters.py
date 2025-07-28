from django import template

register = template.Library()
import re

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user belongs to a specific group"""
    return user.groups.filter(name=group_name).exists()
@register.filter
def count_approved_posts_in_category(posts, category):
    return sum(1 for post in posts if post.status == "Approved" and post.category.main_category.id == category.id)


@register.filter(name='split')
def split_string(value, key):
    delimiters = [',', '،']
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, value)

@register.filter(name='strip')
def strip(value):
    return value.strip()