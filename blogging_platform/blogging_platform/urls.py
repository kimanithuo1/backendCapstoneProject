# blog_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('blog.urls')),
    
    # Authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # Token Authentication (DRF)
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # JWT Authentication
    path('api/auth/jwt/create/', TokenObtainPairView.as_view(), name='jwt_create'),
    path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('api/auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)