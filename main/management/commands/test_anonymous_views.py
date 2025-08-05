from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from main.models import Post, MainCategory, Category

class Command(BaseCommand):
    help = 'Test session-based anonymous view tracking functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing session-based anonymous view tracking...')
        
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
            title='Test Anonymous Views Post',
            authors='Test Author',
            description='Test description for anonymous views',
            keywords='test, anonymous, views',
            status='Approved'
        )
        post.categories.add(category)
        
        self.stdout.write(f'Created fresh test post: {post.title}')
        
        # Create a mock request factory
        factory = RequestFactory()
        
        # Test 1: Anonymous user view with session
        self.stdout.write('Testing anonymous user view...')
        request = factory.get('/')
        request.user = AnonymousUser()  # Proper anonymous user
        
        # Add session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
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
        
        # Test 2: Same session (should not create duplicate)
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
        
        # Test 3: Different session (should create new view)
        self.stdout.write('Testing different session...')
        request2 = factory.get('/')
        request2.user = AnonymousUser()  # Proper anonymous user
        
        # Add session middleware for new session
        middleware.process_request(request2)
        request2.session.save()
        
        before_new_session = post.get_total_view_count()
        post.record_view(request2)
        after_new_session = post.get_total_view_count()
        
        if after_new_session > before_new_session:
            self.stdout.write(
                self.style.SUCCESS(f'✓ New session view recorded: {before_new_session} → {after_new_session}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ New session view not recorded: {before_new_session} → {after_new_session}')
            )
        
        # Show final statistics
        self.stdout.write('\nFinal Statistics:')
        self.stdout.write(f'Total views: {post.get_total_view_count()}')
        self.stdout.write(f'Authenticated views: {post.views.filter(user__isnull=False).count()}')
        self.stdout.write(f'Anonymous session views: {post.views.filter(user__isnull=True).count()}')
        self.stdout.write(f'PDF views: {post.pdf_views.count()}')
        
        # Show session breakdown
        self.stdout.write('\nSession Breakdown:')
        anonymous_views = post.views.filter(user__isnull=True)
        for view in anonymous_views:
            self.stdout.write(f'  - Session: {view.session_key[:8]}...')
        
        # Clean up test post
        post.delete()
        self.stdout.write(self.style.SUCCESS('Session-based view tracking test completed!')) 