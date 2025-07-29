#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from main.models import UserProfile

def test_login():
    """Test the login functionality"""
    print("=== Testing Login Functionality ===")
    
    # Check if superuser exists
    try:
        user = User.objects.get(username='aadmin')
        print(f"✅ Superuser found: {user.username}")
        print(f"   Active: {user.is_active}")
        print(f"   Superuser: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
    except User.DoesNotExist:
        print("❌ Superuser not found!")
        return
    
    # Check UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"✅ UserProfile found")
        print(f"   Email confirmed: {profile.email_confirmed}")
        print(f"   Profile completed: {profile.completed}")
    except UserProfile.DoesNotExist:
        print("❌ UserProfile not found!")
        return
    
    # Test authentication
    print("\n=== Testing Authentication ===")
    
    # Test with correct credentials (you'll need to enter the password)
    print("Please enter the password for 'aadmin':")
    password = input("Password: ")
    
    authenticated_user = authenticate(username='aadmin', password=password)
    if authenticated_user:
        print("✅ Authentication successful!")
        print(f"   User: {authenticated_user.username}")
        print(f"   Active: {authenticated_user.is_active}")
    else:
        print("❌ Authentication failed!")
        print("   This could be due to:")
        print("   - Incorrect password")
        print("   - User is not active")
        print("   - Authentication backend issues")

if __name__ == '__main__':
    test_login() 