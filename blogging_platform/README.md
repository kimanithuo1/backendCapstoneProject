# Django REST API Blogging Platform

A comprehensive blogging platform built with Django and Django REST Framework, featuring user authentication, post management, comments, likes, ratings, subscriptions, and notifications.

## Features
git - **User Management**: Registration, authentication, profiles with JWT tokens
- **Blog Posts**: Full CRUD operations, draft/published/archived status, scheduled publishing
- **Categories and Tags**: Organize posts with categories and tags
- **Comments**: Threaded comments on posts
- **Likes and Ratings**: Users can like posts and rate them (1-5 stars)
- **Subscriptions**: Subscribe to authors or categories for notifications
- **Notifications**: Real-time notifications for new posts, comments, likes, ratings
- **Search and Filtering**: Advanced filtering and search capabilities
- **Pagination**: Efficient pagination for large datasets
- **Media Upload**: Support for featured images and profile pictures
- **CORS Support**: Ready for frontend integration
- **Admin Panel**: Django admin interface for content management

## Project Structure

```
blogging_platform/
├── manage.py
├── requirements.txt
├── blogging_platform/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── blog/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── media/ (created after setup)
├── static/ (created after setup)
├── staticfiles/ (created after setup)
└── README.md
```

## Requirements

- Python 3.8+
- Django 5.0+
- Django REST Framework 3.14+
- Other dependencies listed in requirements.txt

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token pair
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token

### Users
- `GET /api/users/` - List users
- `POST /api/users/` - Register new user
- `GET /api/users/{id}/` - User details
- `GET /api/users/me/` - Current user profile
- `GET /api/users/{id}/posts/` - User's published posts

### User Profiles
- `GET /api/profiles/me/` - Get current user profile
- `PUT /api/profiles/me/` - Update current user profile

### Blog Posts
- `GET /api/posts/` - List posts (published for anonymous, all for authenticated)
- `POST /api/posts/` - Create new post
- `GET /api/posts/{id}/` - Post details
- `PUT /api/posts/{id}/` - Update post
- `DELETE /api/posts/{id}/` - Delete post
- `POST /api/posts/{id}/publish/` - Publish draft post
- `POST /api/posts/{id}/unpublish/` - Unpublish post
- `POST /api/posts/{id}/archive/` - Archive post
- `POST /api/posts/{id}/like/` - Like post
- `POST /api/posts/{id}/unlike/` - Unlike post
- `GET /api/posts/drafts/` - User's draft posts
- `GET /api/posts/published/` - All published posts
- `GET /api/posts/scheduled/` - User's scheduled posts
- `GET /api/posts/my_posts/` - Current user's posts
- `GET /api/posts/by_category/?category_id={id}` - Posts by category
- `GET /api/posts/by_author/?author_id={id}` - Posts by author
- `GET /api/posts/most_liked/` - Most liked posts
- `GET /api/posts/top_rated/` - Top rated posts
- `GET /api/posts/trending/` - Trending posts

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category
- `GET /api/categories/{id}/posts/` - Posts in category

### Tags
- `GET /api/tags/` - List tags
- `POST /api/tags/` - Create tag
- `GET /api/tags/{id}/` - Tag details
- `PUT /api/tags/{id}/` - Update tag
- `DELETE /api/tags/{id}/` - Delete tag
- `GET /api/tags/{id}/posts/` - Posts with tag

### Comments
- `GET /api/comments/` - List approved comments
- `POST /api/comments/` - Create comment
- `GET /api/comments/{id}/` - Comment details
- `PUT /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment
- `GET /api/comments/post_comments/?post_id={id}` - Comments on post
- `GET /api/comments/my_comments/` - Current user's comments

### Likes
- `GET /api/likes/` - Current user's likes
- `POST /api/likes/` - Like a post
- `DELETE /api/likes/{id}/` - Remove like

### Ratings
- `GET /api/ratings/` - Current user's ratings
- `POST /api/ratings/` - Rate a post
- `PUT /api/ratings/{id}/` - Update rating
- `DELETE /api/ratings/{id}/` - Remove rating

### Subscriptions
- `GET /api/subscriptions/` - Current user's subscriptions
- `POST /api/subscriptions/` - Subscribe to author/category
- `DELETE /api/subscriptions/{id}/` - Unsubscribe
- `POST /api/subscriptions/subscribe_author/` - Subscribe to author
- `POST /api/subscriptions/subscribe_category/` - Subscribe to category
- `POST /api/subscriptions/{id}/unsubscribe/` - Unsubscribe

### Notifications
- `GET /api/notifications/` - Current user's notifications
- `POST /api/notifications/{id}/mark_read/` - Mark notification as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `GET /api/notifications/unread_count/` - Unread notifications count

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

Tokens can be obtained from `/api/auth/token/` endpoint by providing username and password.

## Configuration

Key settings in `blogging_platform/settings.py`:

- Database: Currently configured for SQLite (can be changed to PostgreSQL/MySQL)
- JWT: Access tokens expire in 1 hour, refresh tokens in 7 days
- CORS: Configured for localhost development
- Media: Uploaded files stored in `media/` directory
- Static: Static files served via WhiteNoise

## Development

- Run tests: `python manage.py test`
- Create migrations: `python manage.py makemigrations blog`
- Apply migrations: `python manage.py migrate`
- Access admin: `http://127.0.0.1:8000/admin/`

## Deployment

For production deployment:

1. Set `DEBUG = False`
2. Configure production database
3. Set proper `SECRET_KEY`
4. Configure email settings for notifications
5. Set up static files serving
6. Configure CORS for your frontend domain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
