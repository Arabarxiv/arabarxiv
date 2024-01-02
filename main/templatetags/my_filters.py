from django import template

register = template.Library()

@register.filter
def count_approved_posts_in_category(posts, category):
    return sum(1 for post in posts if post.status == "Approved" and post.category.main_category.id == category.id)


@register.filter(name='split')
def split_string(value, key):
    return value.split(key)

@register.filter(name='strip')
def strip(value):
    return value.strip()