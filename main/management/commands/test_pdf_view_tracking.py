from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from main.models import Post, MainCategory, Category

class Command(BaseCommand):
    help = 'Test PDF view tracking functionality for both authenticated and anonymous users'

    def handle(self, *args, **options):
        self.stdout.write('Testing PDF view tracking functionality...')
        
        # Create a fresh test post
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found in database'))
            return
            
        # Create main category and category if they don't exist
        main_category, created = MainCategory.objects.get_or_create(
            name='علوم الحاسوب',
            defaults={'english_name': 'Computer Science'}
        )
        category, created = Category.objects.get_or_create(
            name='الذكاء الاصطناعي',
            defaults={'main_category': main_category}
        )
        
        # Create a fresh test post
        post = Post.objects.create(
            author=user,
            title='Test PDF Tracking Post',
            authors='Test Author',
            description='Test description for PDF tracking',
            keywords='test, pdf, tracking',
            status='Approved'
        )
        post.categories.add(category)
        
        self.stdout.write(f'Created fresh test post: {post.title}')
        
        # Create a mock request factory
        factory = RequestFactory()
        
        # Test 1: Anonymous user PDF download (should record view)
        self.stdout.write('\nTesting anonymous user PDF download...')
        request = factory.get('/')
        request.user = AnonymousUser()
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        initial_count = post.get_total_view_count()
        result = post.add_pdf_view(request.user)
        final_count = post.get_total_view_count()
        
        if result and final_count > initial_count:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Anonymous PDF view recorded: {initial_count} → {final_count}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Anonymous PDF view not recorded: {initial_count} → {final_count}')
            )
        
        # Test 2: Same anonymous device PDF download (should not create duplicate)
        self.stdout.write('Testing duplicate anonymous PDF download...')
        duplicate_count = post.get_total_view_count()
        result = post.add_pdf_view(request.user)
        after_duplicate_count = post.get_total_view_count()
        
        if not result and after_duplicate_count == duplicate_count:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Duplicate anonymous PDF prevention working: {duplicate_count} → {after_duplicate_count}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Duplicate anonymous PDF prevention failed: {duplicate_count} → {after_duplicate_count}')
            )
        
        # Test 3: Authenticated user PDF download (should record PDF view)
        self.stdout.write('\nTesting authenticated user PDF download...')
        request2 = factory.get('/')
        request2.user = user
        request2.META['REMOTE_ADDR'] = '192.168.1.200'
        request2.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        
        before_auth_pdf = post.get_total_view_count()
        result = post.add_pdf_view(request2.user)
        after_auth_pdf = post.get_total_view_count()
        
        if result and after_auth_pdf > before_auth_pdf:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Authenticated PDF view recorded: {before_auth_pdf} → {after_auth_pdf}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Authenticated PDF view not recorded: {before_auth_pdf} → {after_auth_pdf}')
            )
        
        # Test 4: Same authenticated user PDF download (should not create duplicate)
        self.stdout.write('Testing duplicate authenticated PDF download...')
        duplicate_auth_count = post.get_total_view_count()
        result = post.add_pdf_view(request2.user)
        after_duplicate_auth_count = post.get_total_view_count()
        
        if not result and after_duplicate_auth_count == duplicate_auth_count:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Duplicate authenticated PDF prevention working: {duplicate_auth_count} → {after_duplicate_auth_count}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Duplicate authenticated PDF prevention failed: {duplicate_auth_count} → {after_duplicate_auth_count}')
            )
        
        # Test 5: Authenticated user views post details then downloads PDF (should not double count)
        self.stdout.write('\nTesting authenticated user: view post then download PDF...')
        request3 = factory.get('/')
        request3.user = user
        request3.META['REMOTE_ADDR'] = '192.168.1.200'
        request3.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        
        # First view the post details
        before_post_view = post.get_total_view_count()
        post.record_view(request3)
        after_post_view = post.get_total_view_count()
        
        # Then try to download PDF
        before_pdf_after_post = post.get_total_view_count()
        result = post.add_pdf_view(request3.user)
        after_pdf_after_post = post.get_total_view_count()
        
        if after_post_view > before_post_view and after_pdf_after_post == before_pdf_after_post:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Post view recorded, PDF view properly prevented: {before_post_view} → {after_post_view} → {after_pdf_after_post}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Post view or PDF prevention failed: {before_post_view} → {after_post_view} → {after_pdf_after_post}')
            )
        
        # Show final statistics
        self.stdout.write('\nFinal Statistics:')
        self.stdout.write(f'Total views: {post.get_total_view_count()}')
        self.stdout.write(f'Authenticated views: {post.views.filter(user__isnull=False).count()}')
        self.stdout.write(f'Anonymous device views: {post.views.filter(user__isnull=True).count()}')
        self.stdout.write(f'PDF views: {post.pdf_views.count()}')
        
        # Show view breakdown
        self.stdout.write('\nView Breakdown:')
        authenticated_views = post.views.filter(user__isnull=False)
        for view in authenticated_views:
            self.stdout.write(f'  - User: {view.user.username}, IP: {view.ip_address}')
        
        anonymous_views = post.views.filter(user__isnull=True)
        for view in anonymous_views:
            self.stdout.write(f'  - Anonymous IP: {view.ip_address}, Browser: {view.user_agent[:50]}...')
        
        pdf_views = post.pdf_views.all()
        for view in pdf_views:
            self.stdout.write(f'  - PDF view by: {view.user.username}')
        
        # Clean up test post
        post.delete()
        self.stdout.write(self.style.SUCCESS('PDF view tracking test completed!')) 