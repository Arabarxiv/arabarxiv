from django.core.management.base import BaseCommand
from main.models import MainCategory, Category
from main.forms import GroupedCategoryWidget

class Command(BaseCommand):
    help = 'Test the GroupedCategoryWidget functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing GroupedCategoryWidget...')
        
        # Check if we have main categories and subcategories
        main_categories = MainCategory.objects.all()
        categories = Category.objects.all()
        
        self.stdout.write(f'Found {main_categories.count()} main categories')
        self.stdout.write(f'Found {categories.count()} subcategories')
        
        if main_categories.exists():
            self.stdout.write('\nMain Categories:')
            for main_cat in main_categories:
                self.stdout.write(f'  - {main_cat.name}')
                subcategories = main_cat.categories.all()
                if subcategories.exists():
                    for sub_cat in subcategories:
                        self.stdout.write(f'    └─ {sub_cat.name}')
                else:
                    self.stdout.write('    └─ (no subcategories)')
        
        # Test the widget rendering
        widget = GroupedCategoryWidget()
        html = widget.render('category', None, {'class': 'form-control'})
        
        self.stdout.write('\nWidget HTML preview:')
        self.stdout.write(html[:500] + '...' if len(html) > 500 else html)
        
        self.stdout.write(self.style.SUCCESS('Widget test completed successfully!')) 