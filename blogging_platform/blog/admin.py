# blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BlogPost, Category, Tag, UserProfile, Comment,
    PostLike, PostRating, Subscription, Notification
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Posts Count'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Posts Count'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status', 
        'published_date', 'views_count', 'likes_count', 'comments_count'
    ]
    list_filter = ['status', 'category', 'created_at', 'published_date']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = [
        'created_at', 'updated_at', 'views_count', 
        'likes_count', 'comments_count', 'average_rating'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Publishing', {
            'fields': ('status', 'published_date', 'scheduled_publish')
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def likes_count(self, obj):
        return obj.likes_count
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        return obj.comments_count
    comments_count.short_description = 'Comments'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'website', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'website', 'location', 'birth_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'post', 'content_preview', 
        'is_approved', 'is_reply', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'unapprove_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} comments unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']


@admin.register(PostRating)
class PostRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'rating', 'review_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'post__title', 'review']
    readonly_fields = ['created_at', 'updated_at']
    
    def review_preview(self, obj):
        if obj.review:
            return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
        return '-'
    review_preview.short_description = 'Review'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'subscriber', 'subscription_type', 
        'get_target', 'is_active', 'created_at'
    ]
    list_filter = ['subscription_type', 'is_active', 'created_at']
    search_fields = ['subscriber__username', 'author__username', 'category__name']
    readonly_fields = ['created_at']
    
    def get_target(self, obj):
        if obj.subscription_type == 'author':
            return format_html('<strong>Author:</strong> {}', obj.author.username)
        return format_html('<strong>Category:</strong> {}', obj.category.name)
    get_target.short_description = 'Subscribed To'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'notification_type', 'message_preview', 
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message', 'sender__username']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notifications marked as read.')
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected as unread"


# Customize Admin Site
admin.site.site_header = "Blogging Platform Administration"
admin.site.site_title = "Blog Admin Portal"
admin.site.index_title = "Welcome to Blog Administration"