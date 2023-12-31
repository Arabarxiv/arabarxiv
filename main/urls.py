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
    path('terms', views.term_list, name='terms'),
    path('review', views.review_post, name='review'),
    path("review/assign_mod", views.assign_mod, name='assign_mod'), 
    path("authors", views.authors, name="authors"), 
    path('search_results', views.search_posts, name="search"), 
    path("become_reviewer", views.become_reviewer, name="become_reviewer"),
    path('create-translation-post', views.create_translation_post, name='create_translation_post'),
    path('author_guidelines', views.author_guidelines, name='author_guidelines'),
    path('contact', views.contact, name='contact'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)