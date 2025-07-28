#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User, Group
from main.models import ReviewerRequest
from main.views import is_mod_or_staff

print("=== Debug Superuser Status ===")

# Get the test superuser
superuser = User.objects.get(username='testsuperuser')
print(f"Superuser: {superuser.username}")
print(f"Is superuser: {superuser.is_superuser}")
print(f"Is staff: {superuser.is_staff}")
print(f"Is active: {superuser.is_active}")

# Check groups
print(f"Groups: {list(superuser.groups.all())}")

# Check is_mod_or_staff function
print(f"Is mod or staff: {is_mod_or_staff(superuser)}")

# Get moderators list
mod_group = Group.objects.get(name='mod')
moderators = User.objects.filter(groups=mod_group)
print(f"Users in mod group: {list(moderators.values_list('username', flat=True))}")

# Check if superuser is in moderators
print(f"Is superuser in moderators list: {superuser in moderators}")

# Test the template logic
print(f"\n--- Template Logic Test ---")
print(f"not user.is_staff: {not superuser.is_staff}")
print(f"not user in moderators: {not superuser in moderators}")
print(f"not user.is_superuser: {not superuser.is_superuser}")
print(f"Combined condition: {not superuser.is_staff and not superuser in moderators and not superuser.is_superuser}")

# Test the view logic
print(f"\n--- View Logic Test ---")
print(f"is_mod_or_staff(superuser): {is_mod_or_staff(superuser)}")
print(f"is_mod_or_staff(superuser) and not superuser.is_superuser: {is_mod_or_staff(superuser) and not superuser.is_superuser}")

print(f"\n✅ Debug completed!") 