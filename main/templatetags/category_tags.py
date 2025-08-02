from django import template
from django.db.models import Count, Q

register = template.Library()

@register.inclusion_tag('main/category_node.html')
def render_category_node(tree_data):
    """Recursively render a category node with its children"""
    return {
        'category': tree_data['category'],
        'level': tree_data['level'],
        'post_count': tree_data['post_count'],
        'total_posts': tree_data['total_posts'],
        'children': tree_data['children']
    } 