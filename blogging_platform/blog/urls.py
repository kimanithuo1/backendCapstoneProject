from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'posts', views.BlogPostViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'likes', views.PostLikeViewSet)
router.register(r'ratings', views.PostRatingViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
