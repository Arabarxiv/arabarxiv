from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from main.models import Post

class Command(BaseCommand):
    help = 'Test device-based anonymous view tracking functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing device-based anonymous view tracking...')
        
        # Get a test post
        post = Post.objects.first()
        if not post:
            self.stdout.write(self.style.ERROR('No posts found in database'))
            return
        
        self.stdout.write(f'Testing with post: {post.title}')
        
        # Create a mock request factory
        factory = RequestFactory()
        
        # Test 1: Anonymous user view with device info
        self.stdout.write('Testing anonymous user view...')
        request = factory.get('/')
        request.user = AnonymousUser()  # Proper anonymous user
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        # Record view
        initial_count = post.get_total_view_count()
        post.record_view(request)
        final_count = post.get_total_view_count()
        
        if final_count > initial_count:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Anonymous view recorded successfully: {initial_count} → {final_count}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Anonymous view not recorded: {initial_count} → {final_count}')
            )
        
        # Test 2: Same device (should not create duplicate)
        self.stdout.write('Testing duplicate view prevention...')
        duplicate_count = post.get_total_view_count()
        post.record_view(request)
        after_duplicate_count = post.get_total_view_count()
        
        if after_duplicate_count == duplicate_count:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Duplicate prevention working: {duplicate_count} → {after_duplicate_count}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Duplicate prevention failed: {duplicate_count} → {after_duplicate_count}')
            )
        
        # Test 3: Different device (should create new view)
        self.stdout.write('Testing different device...')
        request2 = factory.get('/')
        request2.user = AnonymousUser()  # Proper anonymous user
        request2.META['REMOTE_ADDR'] = '192.168.1.101'
        request2.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        
        before_new_device = post.get_total_view_count()
        post.record_view(request2)
        after_new_device = post.get_total_view_count()
        
        if after_new_device > before_new_device:
            self.stdout.write(
                self.style.SUCCESS(f'✓ New device view recorded: {before_new_device} → {after_new_device}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ New device view not recorded: {before_new_device} → {after_new_device}')
            )
        
        # Test 4: Same IP but different user agent (should create new view)
        self.stdout.write('Testing same IP but different browser...')
        request3 = factory.get('/')
        request3.user = AnonymousUser()  # Proper anonymous user
        request3.META['REMOTE_ADDR'] = '192.168.1.100'  # Same IP
        request3.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'  # Different browser
        
        before_different_browser = post.get_total_view_count()
        post.record_view(request3)
        after_different_browser = post.get_total_view_count()
        
        if after_different_browser > before_different_browser:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Different browser view recorded: {before_different_browser} → {after_different_browser}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Different browser view not recorded: {before_different_browser} → {after_different_browser}')
            )
        
        # Show final statistics
        self.stdout.write('\nFinal Statistics:')
        self.stdout.write(f'Total views: {post.get_total_view_count()}')
        self.stdout.write(f'Authenticated views: {post.views.filter(user__isnull=False).count()}')
        self.stdout.write(f'Anonymous device views: {post.views.filter(user__isnull=True).count()}')
        self.stdout.write(f'PDF views: {post.pdf_views.count()}')
        
        # Show device breakdown
        self.stdout.write('\nDevice Breakdown:')
        anonymous_views = post.views.filter(user__isnull=True)
        for view in anonymous_views:
            self.stdout.write(f'  - IP: {view.ip_address}, Browser: {view.user_agent[:50]}...')
        
        self.stdout.write(self.style.SUCCESS('Device-based view tracking test completed!')) 