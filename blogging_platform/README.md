Project Structure

blogging_platform/
├── manage.py
├── requirements.txt
├── blog_platform/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── blog/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── permissions.py
    ├── urls.py
    ├── admin.py
    └── migrations/
Step 1: Initial Setup


Create Virtual Environment

bash 
python -m venv venv
Linux: source venv/bin/activate 
Windows: venv\Scripts\activate

Download django to venv

pip install django


Step 2: MySQL Database Setup

Create Database in MySQL

sql

CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'blog_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'localhost';
FLUSH PRIVILEGES;


Update settings.py

Update the DATABASES configuration with your MySQL credentials.




Step 3: Django Project Setup

Create Django Project
bash

django-admin startproject blogging_platform.
python manage.py startapp blog