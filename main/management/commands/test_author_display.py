from django.core.management.base import BaseCommand
from main.models import Post


class Command(BaseCommand):
    help = 'Test author display for a specific post'

    def add_arguments(self, parser):
        parser.add_argument('post_id', type=int, help='Post ID to test')

    def handle(self, *args, **options):
        post_id = options['post_id']
        
        try:
            post = Post.objects.get(id=post_id)
            self.stdout.write(f'Testing Post {post_id}: {post.title}')
            self.stdout.write('=' * 50)
            
            # Test the get_ordered_authors method
            self.stdout.write('1. get_ordered_authors() method:')
            ordered_authors = post.get_ordered_authors()
            if ordered_authors.exists():
                for post_author in ordered_authors:
                    author_name = post_author.user.get_full_name() or post_author.user.username
                    self.stdout.write(f'   Order {post_author.order}: {author_name}')
            else:
                self.stdout.write('   No PostAuthor records found')
            
            self.stdout.write('')
            
            # Test the get_authors_string method
            self.stdout.write('2. get_authors_string() method:')
            authors_string = post.get_authors_string()
            self.stdout.write(f'   Result: {authors_string}')
            
            self.stdout.write('')
            
            # Test the old authors field
            self.stdout.write('3. Old authors field:')
            self.stdout.write(f'   post.authors: {post.authors}')
            
            self.stdout.write('')
            
            # Test PostAuthor records directly
            self.stdout.write('4. PostAuthor records (direct query):')
            post_authors = post.post_authors.all().order_by('order')
            if post_authors.exists():
                for pa in post_authors:
                    author_name = pa.user.get_full_name() or pa.user.username
                    self.stdout.write(f'   Order {pa.order}: {author_name} (creator: {pa.is_creator})')
            else:
                self.stdout.write('   No PostAuthor records found')
            
        except Post.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Post {post_id} not found')) 