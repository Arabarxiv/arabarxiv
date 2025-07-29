#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.contrib.auth.models import Group

def create_groups():
    """Create necessary groups for the application"""
    groups_to_create = [
        'default',
        'mod',
        'admin'
    ]
    
    for group_name in groups_to_create:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✅ Created group: {group_name}")
        else:
            print(f"ℹ️  Group already exists: {group_name}")

if __name__ == '__main__':
    create_groups() 