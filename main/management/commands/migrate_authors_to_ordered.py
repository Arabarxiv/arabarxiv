from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Post, PostAuthor


class Command(BaseCommand):
    help = 'Migrate existing posts to use the new PostAuthor model for proper author ordering'

    def handle(self, *args, **options):
        self.stdout.write('Starting author migration...')
        
        posts = Post.objects.all()
        migrated_count = 0
        
        for post in posts:
            # Check if this post already has PostAuthor records
            if post.post_authors.exists():
                self.stdout.write(f'Post {post.id} already has ordered authors, skipping...')
                continue
            
            # Parse the old authors field
            if post.authors:
                authors_list = [author.strip() for author in post.authors.split(',')]
                
                # Create PostAuthor records
                for order, author_name in enumerate(authors_list, 1):
                    # Try to find the user by name
                    user = None
                    
                    # First try to find by exact username
                    try:
                        user = User.objects.get(username=author_name)
                    except User.DoesNotExist:
                        # Try to find by full name
                        try:
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
                        except:
                            pass
                    
                    if not user:
                        # If user not found, skip this author
                        self.stdout.write(f'User not found for author: {author_name} in post {post.id}')
                        continue
                    
                    # Check if this is the creator (first author or post.author)
                    is_creator = (order == 1) or (user == post.author)
                    
                    # Create PostAuthor record
                    PostAuthor.objects.create(
                        post=post,
                        user=user,
                        order=order,
                        is_creator=is_creator
                    )
                
                migrated_count += 1
                self.stdout.write(f'Migrated post {post.id}: {post.title}')
            else:
                # If no authors field, just add the post.author as first author
                PostAuthor.objects.create(
                    post=post,
                    user=post.author,
                    order=1,
                    is_creator=True
                )
                migrated_count += 1
                self.stdout.write(f'Migrated post {post.id} with single author: {post.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated_count} posts to use ordered authors!')
        ) 