# blog/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    BlogPost, Category, Tag, UserProfile, Comment,
    PostLike, PostRating, Subscription, Notification
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'posts_count', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def get_posts_count(self, obj):
        return obj.blog_posts.filter(status='published').count()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Create profile automatically
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'full_name', 'bio', 
            'profile_picture', 'website', 'location', 'birth_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'posts_count', 'created_at']
        read_only_fields = ['slug', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']
        read_only_fields = ['slug', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    post_title = serializers.ReadOnlyField(source='post.title')
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'post_title', 'author', 'author_id',
            'content', 'parent', 'replies_count',
            'created_at', 'updated_at', 'is_approved'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_replies_count(self, obj):
        return obj.replies.filter(is_approved=True).count()

    def validate_content(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        return value


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_profile_picture = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_profile_picture', 'content', 
            'parent', 'replies', 'created_at', 'updated_at', 'is_approved'
        ]

    def get_author_profile_picture(self, obj):
        if hasattr(obj.author, 'profile') and obj.author.profile.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author.profile.profile_picture.url)
        return None

    def get_replies(self, obj):
        if obj.replies.exists():
            replies = obj.replies.filter(is_approved=True)
            return CommentSerializer(replies, many=True).data
        return []


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    post_title = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = PostLike
        fields = ['id', 'post', 'post_title', 'user', 'created_at']
        read_only_fields = ['created_at']


class PostRatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    post_title = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = PostRating
        fields = ['id', 'post', 'post_title', 'user', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    author_profile = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True, 
        queryset=Tag.objects.all(),
        source='tags',
        required=False
    )
    likes_count = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    ratings_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    user_has_liked = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'author_id', 'author_profile',
            'category', 'category_name', 'tags', 'tag_ids', 'status', 'featured_image',
            'published_date', 'scheduled_publish', 'created_at', 'updated_at',
            'views_count', 'likes_count', 'average_rating', 'ratings_count',
            'comments_count', 'user_has_liked', 'user_rating'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'published_date', 'views_count']

    def get_author_profile(self, obj):
        if hasattr(obj.author, 'profile'):
            return {
                'bio': obj.author.profile.bio,
                'profile_picture': self.context['request'].build_absolute_uri(
                    obj.author.profile.profile_picture.url
                ) if obj.author.profile.profile_picture else None
            }
        return None

    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = PostRating.objects.get(post=obj, user=request.user)
                return {'rating': rating.rating, 'review': rating.review}
            except PostRating.DoesNotExist:
                return None
        return None

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

    def validate_content(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Content must be at least 20 characters long.")
        return value

    def validate_scheduled_publish(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled publish date must be in the future.")
        return value


class BlogPostListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category_name',
            'tags', 'featured_image', 'published_date', 'views_count',
            'likes_count', 'comments_count', 'status'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.ReadOnlyField(source='subscriber.username')
    author_name = serializers.ReadOnlyField(source='author.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Subscription
        fields = [
            'id', 'subscriber', 'subscription_type', 'author', 'author_name',
            'category', 'category_name', 'created_at', 'is_active'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        if data['subscription_type'] == 'author' and not data.get('author'):
            raise serializers.ValidationError("Author is required for author subscriptions.")
        if data['subscription_type'] == 'category' and not data.get('category'):
            raise serializers.ValidationError("Category is required for category subscriptions.")
        return data


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')
    post_title = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'post', 'post_title', 'sender', 
            'sender_name', 'message', 'is_read', 'created_at'
        ]
        read_only_fields = ['created_at']