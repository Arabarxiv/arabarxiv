from django.core.management.base import BaseCommand
from main.models import Post, Category, MainCategory

class Command(BaseCommand):
    help = 'Fix posts that were incorrectly assigned AI category and allow proper reassignment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-ai',
            action='store_true',
            help='Remove AI category from all posts to start fresh',
        )
        parser.add_argument(
            '--show-posts',
            action='store_true',
            help='Show all posts and their current categories',
        )

    def handle(self, *args, **options):
        if options['show_posts']:
            self.show_posts()
            return
            
        if options['remove_ai']:
            self.remove_ai_categories()
            return
        
        # Default behavior: show posts and offer to fix
        self.show_posts()
        self.stdout.write('\n' + '='*60)
        self.stdout.write('To remove AI category from all posts, run:')
        self.stdout.write('python manage.py fix_post_categories --remove-ai')
        self.stdout.write('='*60)

    def show_posts(self):
        """Show all posts and their current categories"""
        self.stdout.write('Current Posts and Categories:')
        self.stdout.write('='*60)
        
        posts = Post.objects.all().prefetch_related('categories', 'categories__main_category')
        
        for post in posts:
            categories = post.categories.all()
            category_names = [f'{cat.main_category.name} - {cat.name}' for cat in categories]
            
            self.stdout.write(f'\nID: {post.id}')
            self.stdout.write(f'Title: {post.title}')
            self.stdout.write(f'Meaningful ID: {post.meaningful_id}')
            self.stdout.write(f'Categories: {", ".join(category_names) if category_names else "None"}')

    def remove_ai_categories(self):
        """Remove AI category from all posts"""
        try:
            computer_science = MainCategory.objects.get(name='علوم الحاسوب والتكنولوجيا')
            ai_category = Category.objects.get(name='الذكاء الاصطناعي', main_category=computer_science)
            
            # Find posts with AI category
            ai_posts = Post.objects.filter(categories=ai_category)
            
            if not ai_posts.exists():
                self.stdout.write(self.style.SUCCESS('No posts found with AI category'))
                return
            
            self.stdout.write(f'Found {ai_posts.count()} posts with AI category')
            self.stdout.write('Removing AI category from all posts...')
            
            for post in ai_posts:
                post.categories.remove(ai_category)
                # Clear meaningful ID since post now has no categories
                post.meaningful_id = None
                post.save(update_fields=['meaningful_id'])
                self.stdout.write(f'  - Removed AI category from "{post.title}"')
            
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully removed AI category from {ai_posts.count()} posts'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Run: python manage.py assign_post_categories')
            self.stdout.write('   (This will let you interactively assign proper categories)')
            self.stdout.write('2. Or run: python manage.py assign_post_categories --auto-assign-ai')
            self.stdout.write('   (This will automatically reassign AI category)')
            
        except (MainCategory.DoesNotExist, Category.DoesNotExist):
            self.stdout.write(self.style.ERROR('AI category not found. Please run populate_categories first.')) 