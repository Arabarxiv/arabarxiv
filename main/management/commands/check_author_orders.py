from django.core.management.base import BaseCommand
from main.models import Post, PostAuthor


class Command(BaseCommand):
    help = 'Check the current author orders for posts'

    def handle(self, *args, **options):
        self.stdout.write('Checking author orders...')
        
        posts = Post.objects.all()
        
        for post in posts:
            if post.post_authors.exists():
                self.stdout.write(f'\nPost {post.id}: {post.title}')
                self.stdout.write(f'Old authors field: {post.authors}')
                
                ordered_authors = post.get_ordered_authors()
                self.stdout.write('Ordered authors:')
                for post_author in ordered_authors:
                    author_name = post_author.user.get_full_name() or post_author.user.username
                    self.stdout.write(f'  Order {post_author.order}: {author_name} (creator: {post_author.is_creator})')
            else:
                self.stdout.write(f'\nPost {post.id}: {post.title} - No PostAuthor records')
                self.stdout.write(f'Old authors field: {post.authors}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Check complete!') 