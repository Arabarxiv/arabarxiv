from django.core.management.base import BaseCommand
from main.models import PostView, AnonymousPostView

class Command(BaseCommand):
    help = 'Migrate legacy anonymous views to the unified session-based PostView model'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration of legacy anonymous views...')
        
        # Get all anonymous views from the legacy model
        anonymous_views = AnonymousPostView.objects.all()
        migrated_count = 0
        
        for anonymous_view in anonymous_views:
            # Check if this view already exists in PostView
            existing_view = PostView.objects.filter(
                post=anonymous_view.post,
                session_key=anonymous_view.session_key
            ).first()
            
            if not existing_view:
                # Create new PostView entry
                PostView.objects.create(
                    post=anonymous_view.post,
                    session_key=anonymous_view.session_key,
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
                f'Successfully migrated {migrated_count} legacy anonymous views to session-based PostView model'
            )
        )
        
        # Show statistics
        total_views = PostView.objects.count()
        authenticated_views = PostView.objects.filter(user__isnull=False).count()
        session_views = PostView.objects.filter(user__isnull=True).count()
        
        self.stdout.write(f'\nCurrent Statistics:')
        self.stdout.write(f'Total views: {total_views}')
        self.stdout.write(f'Authenticated views: {authenticated_views}')
        self.stdout.write(f'Session-based views: {session_views}')
        
        # Optionally, you can delete the old AnonymousPostView records
        # Uncomment the following lines if you want to clean up:
        # deleted_count = anonymous_views.count()
        # anonymous_views.delete()
        # self.stdout.write(f'Deleted {deleted_count} old AnonymousPostView records') 