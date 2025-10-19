# blog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogPostViewSet, CategoryViewSet, TagViewSet,
    UserViewSet, UserProfileViewSet, CommentViewSet,
    PostLikeViewSet, PostRatingViewSet, SubscriptionViewSet,
    NotificationViewSet
)

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='blogpost')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', PostLikeViewSet, basename='postlike')
router.register(r'ratings', PostRatingViewSet, basename='postrating')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]