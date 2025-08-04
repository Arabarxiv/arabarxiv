from django.core.management.base import BaseCommand
from main.models import Post

class Command(BaseCommand):
    help = 'Regenerate meaningful IDs for all posts to ensure they are correct'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be made')
        
        # Get all posts
        posts = Post.objects.all()
        
        self.stdout.write(f'Found {posts.count()} posts to process')
        
        updated_count = 0
        error_count = 0
        
        for post in posts:
            try:
                # Check if post has categories
                if not post.categories.exists():
                    self.stdout.write(self.style.WARNING(f'Post "{post.title}" has no categories - skipping'))
                    error_count += 1
                    continue
                
                # Generate new meaningful ID
                new_meaningful_id = post.generate_meaningful_id()
                
                if not new_meaningful_id:
                    self.stdout.write(self.style.WARNING(f'Could not generate meaningful ID for post "{post.title}"'))
                    error_count += 1
                    continue
                
                # Check if the ID has changed
                if post.meaningful_id != new_meaningful_id:
                    self.stdout.write(f'Post "{post.title}":')
                    self.stdout.write(f'  Old ID: {post.meaningful_id}')
                    self.stdout.write(f'  New ID: {new_meaningful_id}')
                    
                    if not dry_run:
                        post.meaningful_id = new_meaningful_id
                        post.save(update_fields=['meaningful_id'])
                        self.stdout.write(f'  -> Updated')
                    else:
                        self.stdout.write(f'  -> Would update')
                    
                    updated_count += 1
                else:
                    self.stdout.write(f'Post "{post.title}" - ID unchanged: {post.meaningful_id}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing post "{post.title}": {str(e)}'))
                error_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Processing completed:'))
        self.stdout.write(f'  - Posts processed: {posts.count()}')
        self.stdout.write(f'  - Posts updated: {updated_count}')
        self.stdout.write(f'  - Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('Dry run completed. Run without --dry-run to apply changes.')) 