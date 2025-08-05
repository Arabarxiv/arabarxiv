from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Post, MainCategory, Category

class Command(BaseCommand):
    help = 'Test new comprehensive meaningful ID generation with multiple categories'

    def handle(self, *args, **options):
        self.stdout.write('Testing new comprehensive meaningful ID generation...')
        
        # Get or create test user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found in database'))
            return
        
        # Get or create test categories
        main_category1, created = MainCategory.objects.get_or_create(
            name='علوم الحاسوب',
            defaults={'english_name': 'Computer Science'}
        )
        
        main_category2, created = MainCategory.objects.get_or_create(
            name='الرياضيات',
            defaults={'english_name': 'Mathematics'}
        )
        
        category1, created = Category.objects.get_or_create(
            name='الذكاء الاصطناعي',
            defaults={'main_category': main_category1}
        )
        
        category2, created = Category.objects.get_or_create(
            name='تعلم الآلة',
            defaults={'main_category': main_category1}
        )
        
        category3, created = Category.objects.get_or_create(
            name='الجبر الخطي',
            defaults={'main_category': main_category2}
        )
        
        self.stdout.write(f'Created categories: {category1.name}, {category2.name}, {category3.name}')
        self.stdout.write(f'Main categories: {main_category1.name}(ID:{main_category1.id}), {main_category2.name}(ID:{main_category2.id})')
        self.stdout.write(f'Sub categories: {category1.name}(ID:{category1.id}), {category2.name}(ID:{category2.id}), {category3.name}(ID:{category3.id})')
        
        # Test 1: Post with single category
        self.stdout.write('\n=== Test 1: Post with single category ===')
        post1 = Post.objects.create(
            author=user,
            title='Test Post 1 - Single Category',
            authors='Test Author',
            description='Test description',
            keywords='test, single, category',
            status='Approved'
        )
        post1.categories.add(category1)
        
        meaningful_id1 = post1.generate_meaningful_id()
        if meaningful_id1:
            post1.meaningful_id = meaningful_id1
            post1.save()
        display1 = post1.get_meaningful_id_display()
        self.stdout.write(f'Post 1 meaningful ID: {meaningful_id1}')
        self.stdout.write(f'Post 1 display: {display1}')
        self.stdout.write(f'Post 1 categories: {[cat.name for cat in post1.categories.all()]}')
        
        # Test 2: Post with two categories from same main category
        self.stdout.write('\n=== Test 2: Post with two categories (same main category) ===')
        post2 = Post.objects.create(
            author=user,
            title='Test Post 2 - Two Categories Same Main',
            authors='Test Author',
            description='Test description',
            keywords='test, two, categories, same',
            status='Approved'
        )
        post2.categories.add(category1, category2)
        
        meaningful_id2 = post2.generate_meaningful_id()
        if meaningful_id2:
            post2.meaningful_id = meaningful_id2
            post2.save()
        display2 = post2.get_meaningful_id_display()
        self.stdout.write(f'Post 2 meaningful ID: {meaningful_id2}')
        self.stdout.write(f'Post 2 display: {display2}')
        self.stdout.write(f'Post 2 categories: {[cat.name for cat in post2.categories.all()]}')
        
        # Test 3: Post with two categories from different main categories
        self.stdout.write('\n=== Test 3: Post with two categories (different main categories) ===')
        post3 = Post.objects.create(
            author=user,
            title='Test Post 3 - Two Categories Different Main',
            authors='Test Author',
            description='Test description',
            keywords='test, two, categories, different',
            status='Approved'
        )
        post3.categories.add(category1, category3)
        
        meaningful_id3 = post3.generate_meaningful_id()
        if meaningful_id3:
            post3.meaningful_id = meaningful_id3
            post3.save()
        display3 = post3.get_meaningful_id_display()
        self.stdout.write(f'Post 3 meaningful ID: {meaningful_id3}')
        self.stdout.write(f'Post 3 display: {display3}')
        self.stdout.write(f'Post 3 categories: {[cat.name for cat in post3.categories.all()]}')
        
        # Test 4: Post with three categories
        self.stdout.write('\n=== Test 4: Post with three categories ===')
        post4 = Post.objects.create(
            author=user,
            title='Test Post 4 - Three Categories',
            authors='Test Author',
            description='Test description',
            keywords='test, three, categories',
            status='Approved'
        )
        post4.categories.add(category1, category2, category3)
        
        meaningful_id4 = post4.generate_meaningful_id()
        if meaningful_id4:
            post4.meaningful_id = meaningful_id4
            post4.save()
        display4 = post4.get_meaningful_id_display()
        self.stdout.write(f'Post 4 meaningful ID: {meaningful_id4}')
        self.stdout.write(f'Post 4 display: {display4}')
        self.stdout.write(f'Post 4 categories: {[cat.name for cat in post4.categories.all()]}')
        
        # Test 5: Post with categories in different order
        self.stdout.write('\n=== Test 5: Categories in different order ===')
        post5 = Post.objects.create(
            author=user,
            title='Test Post 5 - Different Order',
            authors='Test Author',
            description='Test description',
            keywords='test, order',
            status='Approved'
        )
        post5.categories.add(category3, category1)  # Different order
        
        meaningful_id5 = post5.generate_meaningful_id()
        if meaningful_id5:
            post5.meaningful_id = meaningful_id5
            post5.save()
        display5 = post5.get_meaningful_id_display()
        self.stdout.write(f'Post 5 meaningful ID: {meaningful_id5}')
        self.stdout.write(f'Post 5 display: {display5}')
        self.stdout.write(f'Post 5 categories: {[cat.name for cat in post5.categories.all()]}')
        
        # Show detailed breakdown
        self.stdout.write('\n=== Detailed Breakdown ===')
        for i, post in enumerate([post1, post2, post3, post4, post5], 1):
            self.stdout.write(f'\nPost {i}:')
            self.stdout.write(f'  ID: {post.meaningful_id}')
            self.stdout.write(f'  Display: {post.get_meaningful_id_display()}')
            self.stdout.write(f'  Categories: {[f"{cat.main_category.name}/{cat.name}" for cat in post.categories.all()]}')
        
        # Show summary
        self.stdout.write('\n=== Summary ===')
        self.stdout.write('New comprehensive meaningful ID format:')
        self.stdout.write('Format: main1.main2.sub1.sub2.sequence')
        self.stdout.write('Features:')
        self.stdout.write('1. Includes ALL categories (not just the first)')
        self.stdout.write('2. Main categories and sub categories are separated')
        self.stdout.write('3. IDs are padded to 4 digits for consistency')
        self.stdout.write('4. Sequence number is based on the first category')
        self.stdout.write('5. Order is preserved based on main category ID, then sub category ID')
        
        # Clean up
        for post in [post1, post2, post3, post4, post5]:
            post.delete()
        
        self.stdout.write(self.style.SUCCESS('Test completed!')) 