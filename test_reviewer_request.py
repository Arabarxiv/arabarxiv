#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.contrib.auth.models import User, Group
from main.models import ReviewerRequest, UserProfile
from main.views import is_mod_or_staff

def test_reviewer_functionality():
    """Test the reviewer request functionality"""
    print("=" * 60)
    print("TESTING REVIEWER REQUEST FUNCTIONALITY")
    print("=" * 60)
    
    # Check groups
    print("\n1. Checking groups:")
    groups = Group.objects.all()
    for group in groups:
        print(f"   - {group.name}")
    
    # Check users
    print("\n2. Checking users:")
    users = User.objects.all()
    for user in users:
        user_groups = [g.name for g in user.groups.all()]
        is_staff = user.is_staff
        is_superuser = user.is_superuser
        print(f"   - {user.username}: groups={user_groups}, staff={is_staff}, superuser={is_superuser}")
    
    # Test is_mod_or_staff function
    print("\n3. Testing is_mod_or_staff function:")
    for user in users:
        result = is_mod_or_staff(user)
        print(f"   - {user.username}: is_mod_or_staff = {result}")
    
    # Check existing reviewer requests
    print("\n4. Checking existing reviewer requests:")
    requests = ReviewerRequest.objects.all()
    for req in requests:
        print(f"   - User: {req.user.username}, Status: {req.status}, Date: {req.request_date}")
    
    # Check user profiles
    print("\n5. Checking user profiles:")
    for user in users:
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            print(f"   - {user.username}: email_confirmed={profile.email_confirmed}, completed={profile.completed}")
        else:
            print(f"   - {user.username}: No userprofile")
    
    # Test creating a reviewer request
    print("\n6. Testing reviewer request creation:")
    test_user = users.first()  # Use the first user for testing
    if test_user:
        print(f"   Testing with user: {test_user.username}")
        
        # Check if user already has a pending request
        existing_request = ReviewerRequest.objects.filter(user=test_user, status='pending').first()
        if existing_request:
            print(f"   ❌ User already has pending request")
        else:
            print(f"   ✅ No existing pending request")
        
        # Check if user is already a moderator
        if is_mod_or_staff(test_user):
            print(f"   ❌ User is already a moderator")
        else:
            print(f"   ✅ User is not a moderator")
        
        # Check email confirmation
        if hasattr(test_user, 'userprofile') and not test_user.userprofile.email_confirmed and not test_user.is_superuser:
            print(f"   ❌ User email not confirmed")
        else:
            print(f"   ✅ Email confirmation OK")

if __name__ == '__main__':
    test_reviewer_functionality() 