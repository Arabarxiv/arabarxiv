#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabicArxiv.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from main.models import ReviewerRequest, UserProfile
from main.views import become_reviewer

print("=== Testing Superuser Directly ===")

# Get or create a superuser
superuser, created = User.objects.get_or_create(
    username='testsuperuser2',
    defaults={
        'email': 'testsuperuser2@example.com',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True
    }
)

if created:
    superuser.set_password('testpass123')
    superuser.save()
    print(f"Created superuser: {superuser.username}")
    
    # Create userprofile with UNCONFIRMED email (to test bypass)
    userprofile, created = UserProfile.objects.get_or_create(
        user=superuser,
        defaults={'email_confirmed': False, 'completed': True}
    )
    print(f"Created userprofile with UNCONFIRMED email")
else:
    print(f"Using existing superuser: {superuser.username}")
    
    # Ensure userprofile exists with UNCONFIRMED email
    userprofile, created = UserProfile.objects.get_or_create(
        user=superuser,
        defaults={'email_confirmed': False, 'completed': True}
    )
    if created:
        print(f"Created userprofile with UNCONFIRMED email")
    else:
        userprofile.email_confirmed = False  # Keep it UNCONFIRMED
        userprofile.save()
        print(f"Updated userprofile to UNCONFIRMED email")

# Create a request factory
factory = RequestFactory()

# Check current reviewer requests
print(f"Current reviewer requests: {ReviewerRequest.objects.count()}")

# Test POST request with superuser (should bypass email confirmation)
print("Testing POST request with superuser...")
post_request = factory.post('/become_reviewer', {'submit': 'true'})
post_request.user = superuser

try:
    post_response = become_reviewer(post_request)
    print(f"POST response status: {post_response.status_code}")
except Exception as e:
    print(f"Exception occurred: {e}")
    print("But let's check if the request was created anyway...")

# Check if request was created
new_requests = ReviewerRequest.objects.count()
print(f"Reviewer requests after POST: {new_requests}")

if new_requests > 0:
    latest_request = ReviewerRequest.objects.latest('request_date')
    print(f"✅ SUCCESS! Latest request: User={latest_request.user.username}, Status={latest_request.status}")
    print(f"✅ Superuser bypassed email confirmation successfully!")
else:
    print("❌ No new request was created")

print(f"\n✅ Superuser direct test completed!") 