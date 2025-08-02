from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment, PostView, Category, MainCategory

# Create your tests here.

class PostViewsAndCommentsTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create main category and category
        self.main_category = MainCategory.objects.create(
            name='علوم الحاسوب',
            english_name='Computer Science'
        )
        self.category = Category.objects.create(
            main_category=self.main_category,
            name='الذكاء الاصطناعي'
        )
        
        # Create test post
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            authors='Test Author',
            description='Test description',
            category=self.category,
            keywords='test, ai',
            status='Approved'
        )

    def test_get_view_count(self):
        """Test that get_view_count returns correct number of views"""
        # Initially no views
        self.assertEqual(self.post.get_view_count(), 0)
        
        # Add a view
        PostView.objects.create(post=self.post, user=self.user)
        self.assertEqual(self.post.get_view_count(), 1)
        
        # Add another view from different user
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        PostView.objects.create(post=self.post, user=user2)
        self.assertEqual(self.post.get_view_count(), 2)

    def test_get_comment_count(self):
        """Test that get_comment_count returns correct number of comments"""
        # Initially no comments
        self.assertEqual(self.post.get_comment_count(), 0)
        
        # Add a comment
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(self.post.get_comment_count(), 1)
        
        # Add another comment
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Another test comment'
        )
        self.assertEqual(self.post.get_comment_count(), 2)

    def test_user_profile_view_with_views_and_comments(self):
        """Test that user profile view shows posts with view and comment counts"""
        # Add some views and comments
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        PostView.objects.create(post=self.post, user=self.user)
        PostView.objects.create(post=self.post, user=user2)
        
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        Comment.objects.create(
            post=self.post,
            author=user2,
            content='Another test comment'
        )
        
        # Login and access user profile
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, '2')  # View count
        self.assertContains(response, '2')  # Comment count
        self.assertContains(response, 'المزيد من المعلومات')  # More info button

    def test_post_detail_link(self):
        """Test that the more info button links to post detail page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_profile'))
        
        # Check that the post detail link is present
        post_detail_url = reverse('post_detail', args=[self.post.id])
        self.assertContains(response, post_detail_url)
