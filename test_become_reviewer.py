#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.contrib.auth.models import User, Group
from main.models import ReviewerRequest, UserProfile
from main.views import is_mod_or_staff, become_reviewer
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

def test_become_reviewer_process():
    """Test the complete become reviewer process"""
    print("=" * 60)
    print("TESTING BECOME REVIEWER PROCESS")
    print("=" * 60)
    
    # Get a regular user (not staff, not superuser)
    regular_user = User.objects.filter(is_staff=False, is_superuser=False).first()
    
    if not regular_user:
        print("❌ No regular user found for testing")
        return
    
    print(f"Testing with user: {regular_user.username}")
    
    # Check initial state
    print(f"\n1. Initial state:")
    print(f"   - Is moderator: {is_mod_or_staff(regular_user)}")
    print(f"   - Has pending request: {ReviewerRequest.objects.filter(user=regular_user, status='pending').exists()}")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create a POST request to become_reviewer
    request = factory.post('/become_reviewer')
    request.user = regular_user
    
    # Add messages framework
    setattr(request, 'session', {})
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # Call the become_reviewer view
    print(f"\n2. Calling become_reviewer view...")
    response = become_reviewer(request)
    
    print(f"   - Response status: {response.status_code}")
    print(f"   - Response URL: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Check if request was created
    print(f"\n3. After calling become_reviewer:")
    pending_request = ReviewerRequest.objects.filter(user=regular_user, status='pending').first()
    if pending_request:
        print(f"   ✅ Reviewer request created: ID={pending_request.id}")
        print(f"   - Status: {pending_request.status}")
        print(f"   - Date: {pending_request.request_date}")
    else:
        print(f"   ❌ No reviewer request created")
    
    # Test admin approval process
    print(f"\n4. Testing admin approval process:")
    if pending_request:
        # Get admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            print(f"   Admin user: {admin_user.username}")
            
            # Simulate admin approval
            pending_request.status = 'approved'
            pending_request.processed_date = django.utils.timezone.now()
            pending_request.processed_by = admin_user
            pending_request.save()
            
            # Add user to mod group
            mod_group = Group.objects.get(name='mod')
            regular_user.groups.add(mod_group)
            
            print(f"   ✅ Request approved by admin")
            print(f"   - User added to 'mod' group: {'mod' in [g.name for g in regular_user.groups.all()]}")
            print(f"   - Is moderator now: {is_mod_or_staff(regular_user)}")
        else:
            print(f"   ❌ No admin user found")
    
    # Clean up for testing
    print(f"\n5. Cleaning up test data:")
    if pending_request:
        pending_request.delete()
        print(f"   ✅ Deleted test reviewer request")
    
    # Remove user from mod group if added
    if 'mod' in [g.name for g in regular_user.groups.all()]:
        mod_group = Group.objects.get(name='mod')
        regular_user.groups.remove(mod_group)
        print(f"   ✅ Removed user from 'mod' group")

if __name__ == '__main__':
    test_become_reviewer_process() 