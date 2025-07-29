#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.contrib.auth.models import Group

def check_and_create_groups():
    """Check existing groups and create missing ones"""
    print("Checking existing groups...")
    
    existing_groups = Group.objects.all()
    print(f"Found {existing_groups.count()} groups:")
    for group in existing_groups:
        print(f"  - {group.name}")
    
    # Check if 'mod' group exists
    mod_group, created = Group.objects.get_or_create(name='mod')
    if created:
        print(f"✅ Created missing 'mod' group")
    else:
        print(f"ℹ️  'mod' group already exists")
    
    # Check if 'default' group exists
    default_group, created = Group.objects.get_or_create(name='default')
    if created:
        print(f"✅ Created missing 'default' group")
    else:
        print(f"ℹ️  'default' group already exists")

if __name__ == '__main__':
    check_and_create_groups() 