from django.core.management.base import BaseCommand
from main.models import Post, PostAuthor
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Fix author order for a specific post'

    def add_arguments(self, parser):
        parser.add_argument('post_id', type=int, help='Post ID to fix')
        parser.add_argument('--authors', nargs='+', help='Author names in correct order (right to left)')

    def handle(self, *args, **options):
        post_id = options['post_id']
        authors = options.get('authors', [])
        
        try:
            post = Post.objects.get(id=post_id)
            self.stdout.write(f'Fixing author order for post {post_id}: {post.title}')
            
            if not authors:
                self.stdout.write('Please provide author names in correct order using --authors')
                return
            
            # Clear existing PostAuthor records
            post.post_authors.all().delete()
            
            # Create new PostAuthor records in the correct order
            for order, author_name in enumerate(authors, 1):
                # Try to find the user
                user = None
                
                # Try exact username first
                try:
                    user = User.objects.get(username=author_name)
                except User.DoesNotExist:
                    # Try to find by full name
                    name_parts = author_name.split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = ' '.join(name_parts[1:])
                        users = User.objects.filter(first_name__icontains=first_name, 
                                                  last_name__icontains=last_name)
                        if users.count() == 1:
                            user = users.first()
                        else:
                            # Try exact match
                            users = User.objects.filter(first_name=first_name, last_name=last_name)
                            if users.count() == 1:
                                user = users.first()
                
                if user:
                    is_creator = (user == post.author)
                    PostAuthor.objects.create(
                        post=post,
                        user=user,
                        order=order,
                        is_creator=is_creator
                    )
                    self.stdout.write(f'  Order {order}: {user.get_full_name() or user.username} (creator: {is_creator})')
                else:
                    self.stdout.write(f'  User not found: {author_name}')
            
            # Update the authors string field
            post.authors = post.get_authors_string()
            post.save(update_fields=['authors'])
            
            self.stdout.write(self.style.SUCCESS(f'Successfully fixed author order for post {post_id}'))
            
        except Post.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Post {post_id} not found')) 