# blog/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import (
    BlogPost, Category, Tag, UserProfile, Comment,
    PostLike, PostRating, Subscription, Notification
)
from .serializers import (
    BlogPostSerializer, BlogPostListSerializer,
    CategorySerializer, TagSerializer,
    UserSerializer, UserProfileSerializer,
    CommentSerializer, CommentDetailSerializer,
    PostLikeSerializer, PostRatingSerializer,
    SubscriptionSerializer, NotificationSerializer
)
from .permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly, IsSubscriberOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BlogPostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'tags', 'status']
    search_fields = ['title', 'content', 'author__username', 'tags__name']
    ordering_fields = ['published_date', 'created_at', 'title', 'views_count', 'likes__count']
    ordering = ['-created_at']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return BlogPost.objects.filter(status='published').select_related(
                'author', 'category'
            ).prefetch_related('tags')
        
        return BlogPost.objects.all().select_related(
            'author', 'category'
        ).prefetch_related('tags')

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        return BlogPostSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        
        if post.author != request.user:
            return Response(
                {'error': 'You can only publish your own posts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if post.status == 'published':
            return Response(
                {'error': 'Post is already published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.publish()
        
        # Send notifications to subscribers
        self._notify_subscribers(post)
        
        serializer = self.get_serializer(post)
        return Response(
            {'message': 'Post published successfully.', 'post': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        post = self.get_object()
        
        if post.author != request.user:
            return Response(
                {'error': 'You can only unpublish your own posts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if post.status != 'published':
            return Response(
                {'error': 'Only published posts can be unpublished.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.unpublish()
        serializer = self.get_serializer(post)
        return Response(
            {'message': 'Post unpublished successfully.', 'post': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        post = self.get_object()
        
        if post.author != request.user:
            return Response(
                {'error': 'You can only archive your own posts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.archive()
        serializer = self.get_serializer(post)
        return Response(
            {'message': 'Post archived successfully.', 'post': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        
        if not created:
            return Response(
                {'message': 'You already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                notification_type='new_like',
                post=post,
                sender=request.user,
                message=f"{request.user.username} liked your post '{post.title}'"
            )
        
        return Response(
            {'message': 'Post liked successfully.', 'likes_count': post.likes_count},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        try:
            like = PostLike.objects.get(post=post, user=request.user)
            like.delete()
            return Response(
                {'message': 'Post unliked successfully.', 'likes_count': post.likes_count},
                status=status.HTTP_200_OK
            )
        except PostLike.DoesNotExist:
            return Response(
                {'error': 'You have not liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def drafts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        drafts = BlogPost.objects.filter(
            author=request.user, 
            status='draft'
        ).select_related('category').prefetch_related('tags')
        
        page = self.paginate_queryset(drafts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(drafts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def published(self, request):
        published = BlogPost.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')
        
        page = self.paginate_queryset(published)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(published, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        scheduled = BlogPost.objects.filter(
            author=request.user,
            status='draft',
            scheduled_publish__isnull=False,
            scheduled_publish__gt=timezone.now()
        ).select_related('category').prefetch_related('tags')
        
        page = self.paginate_queryset(scheduled)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(scheduled, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        posts = BlogPost.objects.filter(
            author=request.user
        ).select_related('category').prefetch_related('tags')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            posts = posts.filter(status=status_filter)
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        posts = self.get_queryset().filter(category_id=category_id, status='published')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_author(self, request):
        author_id = request.query_params.get('author_id')
        if not author_id:
            return Response(
                {'error': 'author_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        posts = self.get_queryset().filter(author_id=author_id, status='published')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def most_liked(self, request):
        posts = BlogPost.objects.annotate(
            like_count=Count('likes')
        ).filter(status='published').order_by('-like_count')[:10]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        posts = BlogPost.objects.annotate(
            avg_rating=Avg('ratings__rating')
        ).filter(status='published', avg_rating__isnull=False).order_by('-avg_rating')[:10]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        # Get posts from last 7 days sorted by views and likes
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        
        posts = BlogPost.objects.annotate(
            like_count=Count('likes')
        ).filter(
            status='published',
            published_date__gte=week_ago
        ).order_by('-views_count', '-like_count')[:10]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def _notify_subscribers(self, post):
        # Notify author subscribers
        author_subscriptions = Subscription.objects.filter(
            author=post.author,
            subscription_type='author',
            is_active=True
        )
        
        for sub in author_subscriptions:
            Notification.objects.create(
                user=sub.subscriber,
                notification_type='new_post',
                post=post,
                sender=post.author,
                message=f"{post.author.username} published a new post: '{post.title}'"
            )
        
        # Notify category subscribers
        if post.category:
            category_subscriptions = Subscription.objects.filter(
                category=post.category,
                subscription_type='category',
                is_active=True
            )
            
            for sub in category_subscriptions:
                Notification.objects.create(
                    user=sub.subscriber,
                    notification_type='new_post',
                    post=post,
                    sender=post.author,
                    message=f"New post in {post.category.name}: '{post.title}'"
                )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        category = self.get_object()
        posts = BlogPost.objects.filter(
            category=category,
            status='published'
        ).select_related('author').prefetch_related('tags')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = BlogPost.objects.filter(
            tags=tag,
            status='published'
        ).select_related('author', 'category')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        user = self.get_object()
        posts = BlogPost.objects.filter(
            author=user,
            status='published'
        ).select_related('category').prefetch_related('tags')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_approved=True).select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        
        # Create notification for post author
        if comment.post.author != self.request.user:
            Notification.objects.create(
                user=comment.post.author,
                notification_type='new_comment',
                post=comment.post,
                sender=self.request.user,
                message=f"{self.request.user.username} commented on your post '{comment.post.title}'"
            )

    @action(detail=False, methods=['get'])
    def post_comments(self, request):
        post_id = request.query_params.get('post_id')
        if not post_id:
            return Response(
                {'error': 'post_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comments = self.queryset.filter(post_id=post_id, parent__isnull=True)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentDetailSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comments = Comment.objects.filter(author=request.user).select_related('post')
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all().select_related('user', 'post')
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        if PostLike.objects.filter(post_id=post_id, user=request.user).exists():
            return Response(
                {'error': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class PostRatingViewSet(viewsets.ModelViewSet):
    queryset = PostRating.objects.all().select_related('user', 'post')
    serializer_class = PostRatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'rating']
    ordering_fields = ['rating', 'created_at']

    def perform_create(self, serializer):
        rating = serializer.save(user=self.request.user)
        
        # Create notification for post author
        if rating.post.author != self.request.user:
            Notification.objects.create(
                user=rating.post.author,
                notification_type='new_rating',
                post=rating.post,
                sender=self.request.user,
                message=f"{self.request.user.username} rated your post '{rating.post.title}' - {rating.rating} stars"
            )

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        if PostRating.objects.filter(post_id=post_id, user=request.user).exists():
            return Response(
                {'error': 'You have already rated this post. Use PUT to update.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().select_related('subscriber', 'author', 'category')
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSubscriberOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subscription_type', 'is_active']

    def get_queryset(self):
        return self.queryset.filter(subscriber=self.request.user)

    def perform_create(self, serializer):
        serializer.save(subscriber=self.request.user)

    @action(detail=False, methods=['post'])
    def subscribe_author(self, request):
        author_id = request.data.get('author_id')
        if not author_id:
            return Response(
                {'error': 'author_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            author = User.objects.get(id=author_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Author not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if author == request.user:
            return Response(
                {'error': 'You cannot subscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            author=author,
            subscription_type='author',
            defaults={'is_active': True}
        )
        
        if not created:
            if subscription.is_active:
                return Response(
                    {'message': 'Already subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                subscription.is_active = True
                subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def subscribe_category(self, request):
        category_id = request.data.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            category=category,
            subscription_type='category',
            defaults={'is_active': True}
        )
        
        if not created:
            if subscription.is_active:
                return Response(
                    {'message': 'Already subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                subscription.is_active = True
                subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        subscription = self.get_object()
        subscription.is_active = False
        subscription.save()
        
        return Response(
            {'message': 'Unsubscribed successfully'},
            status=status.HTTP_200_OK
        )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'notification_type']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response(
            {'message': 'All notifications marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})