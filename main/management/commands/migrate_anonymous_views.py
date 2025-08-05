from django.core.management.base import BaseCommand
from main.models import PostView, AnonymousPostView

class Command(BaseCommand):
    help = 'Migrate legacy anonymous views to the unified device-based PostView model'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration of legacy anonymous views...')
        
        # Get all anonymous views from the legacy model
        anonymous_views = AnonymousPostView.objects.all()
        migrated_count = 0
        
        for anonymous_view in anonymous_views:
            # For legacy session-based views, we'll create a generic device entry
            # since we don't have IP/user agent information
            existing_view = PostView.objects.filter(
                post=anonymous_view.post,
                ip_address='0.0.0.0',  # Placeholder for migrated data
                user_agent='Legacy Session Migration'
            ).first()
            
            if not existing_view:
                # Create new PostView entry with placeholder device info
                PostView.objects.create(
                    post=anonymous_view.post,
                    ip_address='0.0.0.0',  # Placeholder IP
                    user_agent='Legacy Session Migration',
                    viewed_at=anonymous_view.viewed_at
                )
                migrated_count += 1
            else:
                # Update existing view timestamp if needed
                if existing_view.viewed_at != anonymous_view.viewed_at:
                    existing_view.viewed_at = anonymous_view.viewed_at
                    existing_view.save()
                    migrated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully migrated {migrated_count} legacy anonymous views to device-based PostView model'
            )
        )
        
        # Show statistics
        total_views = PostView.objects.count()
        authenticated_views = PostView.objects.filter(user__isnull=False).count()
        device_views = PostView.objects.filter(user__isnull=True).count()
        
        self.stdout.write(f'\nCurrent Statistics:')
        self.stdout.write(f'Total views: {total_views}')
        self.stdout.write(f'Authenticated views: {authenticated_views}')
        self.stdout.write(f'Device-based views: {device_views}')
        
        # Optionally, you can delete the old AnonymousPostView records
        # Uncomment the following lines if you want to clean up:
        # deleted_count = anonymous_views.count()
        # anonymous_views.delete()
        # self.stdout.write(f'Deleted {deleted_count} old AnonymousPostView records') 