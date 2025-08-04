from django.core.management.base import BaseCommand
from main.models import Post, Category, MainCategory

class Command(BaseCommand):
    help = 'Generate meaningful IDs for existing posts'

    def handle(self, *args, **options):
        self.stdout.write('Starting to generate meaningful IDs for existing posts...')
        
        # Get all posts that don't have meaningful IDs
        posts_without_meaningful_id = Post.objects.filter(meaningful_id__isnull=True)
        
        if not posts_without_meaningful_id.exists():
            self.stdout.write(self.style.SUCCESS('All posts already have meaningful IDs!'))
            return
        
        self.stdout.write(f'Found {posts_without_meaningful_id.count()} posts without meaningful IDs')
        
        # Process each post
        for post in posts_without_meaningful_id:
            try:
                # Only generate meaningful ID if post has categories
                if post.categories.count() == 0:
                    self.stdout.write(self.style.WARNING(f'Post "{post.title}" has no categories - skipping'))
                    continue
                
                # Generate meaningful ID
                meaningful_id = post.generate_meaningful_id()
                if meaningful_id:
                    post.meaningful_id = meaningful_id
                    post.save(update_fields=['meaningful_id'])
                    self.stdout.write(f'Generated ID "{meaningful_id}" for post "{post.title}"')
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate ID for post "{post.title}" - no categories'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing post "{post.title}": {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Finished generating meaningful IDs!'))
        
        # Show some statistics
        total_posts = Post.objects.count()
        posts_with_meaningful_id = Post.objects.filter(meaningful_id__isnull=False).count()
        
        self.stdout.write(f'Total posts: {total_posts}')
        self.stdout.write(f'Posts with meaningful IDs: {posts_with_meaningful_id}')
        self.stdout.write(f'Posts without meaningful IDs: {total_posts - posts_with_meaningful_id}') 