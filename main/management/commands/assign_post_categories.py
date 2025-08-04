from django.core.management.base import BaseCommand
from main.models import Post, Category, MainCategory

class Command(BaseCommand):
    help = 'Interactively assign categories to posts that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-assign-ai',
            action='store_true',
            help='Automatically assign AI category to posts without categories',
        )

    def handle(self, *args, **options):
        auto_assign_ai = options['auto_assign_ai']
        
        # Get posts without categories
        posts_without_categories = Post.objects.filter(categories__isnull=True)
        
        if not posts_without_categories.exists():
            self.stdout.write(self.style.SUCCESS('All posts have categories assigned!'))
            return
        
        self.stdout.write(f'Found {posts_without_categories.count()} posts without categories')
        
        if auto_assign_ai:
            # Get the AI category
            try:
                computer_science = MainCategory.objects.get(name='علوم الحاسوب والتكنولوجيا')
                ai_category = Category.objects.get(name='الذكاء الاصطناعي', main_category=computer_science)
                
                for post in posts_without_categories:
                    post.categories.add(ai_category)
                    # Regenerate meaningful ID
                    meaningful_id = post.generate_meaningful_id()
                    if meaningful_id:
                        post.meaningful_id = meaningful_id
                        post.save(update_fields=['meaningful_id'])
                    self.stdout.write(f'Assigned AI category to post "{post.title}" (ID: {post.id})')
                
                self.stdout.write(self.style.SUCCESS('Successfully assigned AI category to all posts without categories'))
                return
                
            except (MainCategory.DoesNotExist, Category.DoesNotExist):
                self.stdout.write(self.style.ERROR('AI category not found. Please run populate_categories first.'))
                return
        
        # Show available categories
        self.stdout.write('\nAvailable Categories:')
        main_categories = MainCategory.objects.prefetch_related('categories').all()
        
        for main_cat in main_categories:
            self.stdout.write(f'\n{main_cat.id}. {main_cat.name} ({main_cat.english_name})')
            for sub_cat in main_cat.categories.all():
                self.stdout.write(f'  {sub_cat.id}. {sub_cat.name}')
        
        # Interactive assignment
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Interactive Category Assignment')
        self.stdout.write('='*50)
        
        for post in posts_without_categories:
            self.stdout.write(f'\nPost: {post.title} (ID: {post.id})')
            self.stdout.write(f'Description: {post.description[:100]}...')
            
            try:
                category_id = input('Enter category ID (or press Enter to skip): ').strip()
                if category_id:
                    category = Category.objects.get(id=int(category_id))
                    post.categories.add(category)
                    
                    # Regenerate meaningful ID
                    meaningful_id = post.generate_meaningful_id()
                    if meaningful_id:
                        post.meaningful_id = meaningful_id
                        post.save(update_fields=['meaningful_id'])
                    
                    self.stdout.write(f'  -> Assigned to: {category.main_category.name} - {category.name}')
                    self.stdout.write(f'  -> New meaningful ID: {post.meaningful_id}')
                else:
                    self.stdout.write('  -> Skipped')
            except (ValueError, Category.DoesNotExist):
                self.stdout.write(self.style.ERROR('  -> Invalid category ID, skipped'))
            except KeyboardInterrupt:
                self.stdout.write('\nAssignment cancelled')
                break
        
        self.stdout.write(self.style.SUCCESS('\nCategory assignment completed!')) 