from django.core.management.base import BaseCommand
from main.models import Post, Category
import random

class Command(BaseCommand):
    help = 'Assign random categories to posts that don\'t have categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed',
            type=int,
            help='Random seed for reproducible results',
        )

    def handle(self, *args, **options):
        # Set random seed if provided
        if options['seed']:
            random.seed(options['seed'])
            self.stdout.write(f'Using random seed: {options["seed"]}')
        
        # Get posts without categories
        posts_without_categories = Post.objects.filter(categories__isnull=True)
        
        if not posts_without_categories.exists():
            self.stdout.write(self.style.SUCCESS('All posts already have categories assigned!'))
            return
        
        self.stdout.write(f'Found {posts_without_categories.count()} posts without categories')
        
        # Get all available categories
        all_categories = list(Category.objects.all())
        
        if not all_categories:
            self.stdout.write(self.style.ERROR('No categories found. Please run populate_categories first.'))
            return
        
        self.stdout.write(f'Available categories: {len(all_categories)}')
        
        # Assign random categories
        assigned_count = 0
        category_counts = {}
        
        for post in posts_without_categories:
            # Pick a random category
            random_category = random.choice(all_categories)
            
            # Assign the category
            post.categories.add(random_category)
            
            # Generate meaningful ID
            meaningful_id = post.generate_meaningful_id()
            if meaningful_id:
                post.meaningful_id = meaningful_id
                post.save(update_fields=['meaningful_id'])
            
            # Track category usage
            category_name = f"{random_category.main_category.name} - {random_category.name}"
            category_counts[category_name] = category_counts.get(category_name, 0) + 1
            
            self.stdout.write(f'  - "{post.title}" -> {category_name} (ID: {post.meaningful_id})')
            assigned_count += 1
        
        # Show summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('ASSIGNMENT SUMMARY')
        self.stdout.write('='*60)
        self.stdout.write(f'Total posts assigned: {assigned_count}')
        self.stdout.write('\nCategory distribution:')
        
        for category_name, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f'  {category_name}: {count} posts')
        
        self.stdout.write(self.style.SUCCESS('\nRandom category assignment completed!'))
        self.stdout.write('\nYou can now test the meaningful IDs with different categories:')
        self.stdout.write('  - AI posts: /post/13.101.x/')
        self.stdout.write('  - Math posts: /post/12.93.x/')
        self.stdout.write('  - Physics posts: /post/12.94.x/')
        self.stdout.write('  - etc.') 