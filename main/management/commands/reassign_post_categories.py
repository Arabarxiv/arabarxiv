from django.core.management.base import BaseCommand
from main.models import Post, Category, MainCategory

class Command(BaseCommand):
    help = 'Reassign posts that were incorrectly assigned AI category to their proper categories'

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
        
        # Get the AI category
        try:
            computer_science = MainCategory.objects.get(name='علوم الحاسوب والتكنولوجيا')
            ai_category = Category.objects.get(name='الذكاء الاصطناعي', main_category=computer_science)
        except (MainCategory.DoesNotExist, Category.DoesNotExist):
            self.stdout.write(self.style.ERROR('AI category not found. Please run populate_categories first.'))
            return
        
        # Find posts that only have the AI category and were created recently (likely incorrectly assigned)
        # We'll look for posts that have meaningful_id starting with the AI category pattern
        ai_posts = Post.objects.filter(
            categories=ai_category,
            meaningful_id__startswith=f'{computer_science.id}.{ai_category.id}.'
        )
        
        self.stdout.write(f'Found {ai_posts.count()} posts with AI category that might need reassignment')
        
        if not ai_posts.exists():
            self.stdout.write(self.style.SUCCESS('No posts found that need category reassignment!'))
            return
        
        # For now, we'll just report these posts
        # In a real scenario, you might want to:
        # 1. Look at the post title/description to guess the category
        # 2. Ask the user to manually reassign
        # 3. Use some AI/ML to categorize based on content
        
        self.stdout.write('\nPosts with AI category that might need reassignment:')
        for post in ai_posts:
            self.stdout.write(f'  - Post ID: {post.id}')
            self.stdout.write(f'    Title: {post.title}')
            self.stdout.write(f'    Meaningful ID: {post.meaningful_id}')
            self.stdout.write(f'    Created: {post.created_at}')
            self.stdout.write('')
        
        if not dry_run:
            self.stdout.write(self.style.WARNING(
                'This command only reports posts that might need reassignment. '
                'Manual review and reassignment is recommended for accurate categorization.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Dry run completed. Review the posts above and manually reassign categories as needed.'
            )) 