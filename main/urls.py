from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.real_home, name='real_home'),
    path('home', views.real_home, name='real_home'),
    path('posts', views.home, name='posts'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('create-post', views.create_post, name='create_post'),
    path("logout", views.logout_view, name="logout"),
    path("login", views.custom_login_view, name="login"),
    path("palestine", views.palestine_view, name="palestine"),
    #path('user_profile/', views.profile_view, name='user_profile'),
    path('user_profile', views.modify_profile, name='user_profile'),
    path('profile/<int:user_id>/', views.public_profile, name='public_profile'),
    path('terms', views.term_list, name='terms'),
    path('categories', views.category_hierarchy, name='category_hierarchy'),
    path('review', views.review_post, name='review'),
    path('review/start/<int:post_id>/', views.start_reviewing, name='start_reviewing'),
    path('review/detailed/<int:post_id>/', views.detailed_review, name='detailed_review'),
    path("review/assign_mod", views.assign_mod, name='assign_mod'), 
    path("authors", views.authors, name="authors"), 
    path('search_results', views.search_posts, name="search"), 
    path("become_reviewer", views.become_reviewer, name="become_reviewer"),
    path('create-translation-post', views.create_translation_post, name='create_translation_post'),
    path('author_guidelines', views.author_guidelines, name='author_guidelines'),
    path('contact', views.contact, name='contact'),
    path('confirm-email/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('resend-confirmation-email/<int:user_id>/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('bibtex', views.bibtex_converter, name='bibtex_converter'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/submit-draft/<int:post_id>/', views.submit_draft, name='submit_draft'),
    path('translation/submit-draft/<int:post_id>/', views.submit_translation_draft, name='submit_translation_draft'),
    path('post/request-re-review/<int:post_id>/', views.request_re_review, name='request_re_review'),
    path('get-categories/', views.get_categories, name='get_categories'),
    path('get-users/', views.get_users, name='get_users'),
    path('get-moderators/', views.get_moderators, name='get_moderators'),

    path('reviewer-request-status/', views.check_reviewer_request_status, name='reviewer_request_status'),
    path('post/<str:meaningful_id>/', views.post_detail_by_meaningful_id, name='post_detail_by_meaningful_id'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/download-pdf/', views.download_pdf, name='download_pdf'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('author/<str:author_name>/', views.find_user_by_name, name='find_user_by_name'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/confirm/<str:token>/', views.confirm_newsletter_signup, name='confirm_newsletter_signup'),
    path('newsletter/unsubscribe/<str:token>/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    path('newsletter/test/', views.newsletter_test, name='newsletter_test'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)