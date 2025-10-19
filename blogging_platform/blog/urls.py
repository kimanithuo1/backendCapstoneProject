# blog/urls.py - Complete URL Configuration
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    BlogPostViewSet, CategoryViewSet, TagViewSet,
    UserViewSet, UserProfileViewSet, CommentViewSet,
    PostLikeViewSet, PostRatingViewSet, SubscriptionViewSet,
    NotificationViewSet
)

# API Router
router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='api-blogpost')
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'tags', TagViewSet, basename='api-tag')
router.register(r'users', UserViewSet, basename='api-user')
router.register(r'profiles', UserProfileViewSet, basename='api-userprofile')
router.register(r'comments', CommentViewSet, basename='api-comment')
router.register(r'likes', PostLikeViewSet, basename='api-postlike')
router.register(r'ratings', PostRatingViewSet, basename='api-postrating')
router.register(r'subscriptions', SubscriptionViewSet, basename='api-subscription')
router.register(r'notifications', NotificationViewSet, basename='api-notification')

app_name = 'blog'

urlpatterns = [
    # ===== TEMPLATE VIEWS =====
    # Home & Listing
    path('', views.home_view, name='home'),
    path('posts/', views.post_list_view, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail_view, name='post_detail'),
    
    # Categories
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<slug:slug>/', views.category_posts_view, name='category_posts'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & User
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-posts/', views.my_posts_view, name='my_posts'),
    path('profile/', views.profile_view, name='profile'),
    
    # Post Management
    path('create/', views.post_create_view, name='post_create'),
    path('edit/<slug:slug>/', views.post_edit_view, name='post_edit'),
    path('delete/<slug:slug>/', views.post_delete_view, name='post_delete'),
    
    # API Documentation
    path('api-docs/', views.api_docs_view, name='api_docs'),
    
    # ===== API ENDPOINTS =====
    path('api/', include(router.urls)),
]