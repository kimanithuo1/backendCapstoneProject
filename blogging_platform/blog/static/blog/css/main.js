// ============================================
// BLOGGING PLATFORM - MAIN JAVASCRIPT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    initMobileNav();
    
    // Alert Close Buttons
    initAlerts();
    
    // Smooth Scrolling
    initSmoothScroll();
    
    // Form Validation
    initFormValidation();
    
    // Lazy Loading Images
    initLazyLoading();
    
    // Read Time Calculator
    calculateReadTime();
});

// ===== MOBILE NAVIGATION =====
function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
}

// ===== ALERTS =====
function initAlerts() {
    const alertCloses = document.querySelectorAll('.alert-close');
    
    alertCloses.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        });
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

// ===== SMOOTH SCROLLING =====
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// ===== FORM VALIDATION =====
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, 'This field is required');
                } else {
                    clearFieldError(field);
                }
                
                // Email validation
                if (field.type === 'email' && field.value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(field.value)) {
                        isValid = false;
                        showFieldError(field, 'Please enter a valid email');
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    field.classList.add('error');
    field.style.borderColor = 'var(--danger)';
    
    let errorDiv = field.parentElement.querySelector('.form-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        field.parentElement.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('error');
    field.style.borderColor = '';
    const errorDiv = field.parentElement.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// ===== LAZY LOADING =====
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// ===== READ TIME CALCULATOR =====
function calculateReadTime() {
    const articles = document.querySelectorAll('.post-content');
    
    articles.forEach(article => {
        const text = article.textContent;
        const wordCount = text.trim().split(/\s+/).length;
        const readTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words/min
        
        const readTimeElement = article.querySelector('.read-time');
        if (readTimeElement) {
            readTimeElement.textContent = `${readTime} min read`;
        }
    });
}

// ===== LIKE BUTTON =====
function likePost(postId) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.href = '/login/?next=' + window.location.pathname;
        return;
    }
    
    fetch(`/api/posts/${postId}/like/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            const likeButton = document.querySelector(`[data-post-id="${postId}"] .like-count`);
            if (likeButton) {
                likeButton.textContent = data.likes_count;
            }
            showAlert('Post liked!', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    });
}

// ===== SHOW ALERT =====
function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.messages-container') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close">&times;</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Add close functionality
    alert.querySelector('.alert-close').addEventListener('click', function() {
        alert.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    });
    
    // Auto-dismiss
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}

// ===== COMMENT SUBMISSION =====
function submitComment(postId, content, parentId = null) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.href = '/login/?next=' + window.location.pathname;
        return;
    }
    
    const data = {
        post: postId,
        content: content,
        parent: parentId
    };
    
    fetch('/api/comments/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            showAlert('Comment posted successfully!', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert('Error posting comment', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    });
}

// ===== SEARCH FUNCTIONALITY =====
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 3) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                searchPosts(query);
            }, 500);
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

function searchPosts(query) {
    fetch(`/api/posts/?search=${encodeURIComponent(query)}&page_size=5`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displaySearchResults(posts) {
    const searchResults = document.getElementById('searchResults');
    
    if (!posts || posts.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
        searchResults.style.display = 'block';
        return;
    }
    
    searchResults.innerHTML = posts.map(post => `
        <a href="/posts/${post.slug}/" class="search-result-item">
            <h4>${post.title}</h4>
            <p>${post.excerpt.substring(0, 100)}...</p>
        </a>
    `).join('');
    
    searchResults.style.display = 'block';
}

// ===== INFINITE SCROLL =====
function initInfiniteScroll() {
    const postsContainer = document.querySelector('.posts-grid');
    if (!postsContainer) return;
    
    let page = 2;
    let loading = false;
    let hasMore = true;
    
    window.addEventListener('scroll', function() {
        if (loading || !hasMore) return;
        
        const scrollPosition = window.innerHeight + window.scrollY;
        const pageHeight = document.documentElement.scrollHeight;
        
        if (scrollPosition >= pageHeight - 500) {
            loading = true;
            loadMorePosts(page++);
        }
    });
    
    function loadMorePosts(pageNum) {
        const url = new URL(window.location.href);
        url.searchParams.set('page', pageNum);
        
        fetch(`/api/posts/?page=${pageNum}`)
            .then(response => response.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    appendPosts(data.results);
                    hasMore = data.next !== null;
                } else {
                    hasMore = false;
                }
                loading = false;
            })
            .catch(error => {
                console.error('Error loading posts:', error);
                loading = false;
            });
    }
    
    function appendPosts(posts) {
        posts.forEach(post => {
            const postCard = createPostCard(post);
            postsContainer.appendChild(postCard);
        });
    }
}

function createPostCard(post) {
    const article = document.createElement('article');
    article.className = 'post-card';
    article.innerHTML = `
        <div class="post-image ${!post.featured_image ? 'post-image-placeholder' : ''}">
            ${post.featured_image 
                ? `<img src="${post.featured_image}" alt="${post.title}">`
                : '<div class="placeholder-icon"><i class="fas fa-image"></i></div>'
            }
            <div class="post-overlay">
                <span class="category-badge">${post.category_name}</span>
            </div>
        </div>
        <div class="post-content">
            <div class="post-meta">
                <img src="https://ui-avatars.com/api/?name=${post.author}&background=667eea&color=fff" 
                     alt="${post.author}" class="author-avatar">
                <div class="post-meta-info">
                    <span class="author-name">${post.author}</span>
                    <span class="post-date">${formatDate(post.published_date)}</span>
                </div>
            </div>
            <h3 class="post-title">
                <a href="/posts/${post.slug}/">${post.title}</a>
            </h3>
            <p class="post-excerpt">${post.excerpt.substring(0, 150)}...</p>
            <div class="post-footer">
                <div class="post-stats">
                    <span><i class="fas fa-eye"></i> ${post.views_count}</span>
                    <span><i class="fas fa-heart"></i> ${post.likes_count}</span>
                    <span><i class="fas fa-comment"></i> ${post.comments_count}</span>
                </div>
                <a href="/posts/${post.slug}/" class="read-more">
                    Read More <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
    return article;
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== COPY TO CLIPBOARD =====
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showAlert('Failed to copy', 'danger');
    });
}

// ===== SHARE POST =====
function sharePost(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        }).catch(err => console.log('Error sharing:', err));
    } else {
        copyToClipboard(url);
    }
}

// ===== NOTIFICATION CHECKER =====
function checkNotifications() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    fetch('/api/notifications/unread_count/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const badge = document.querySelector('.notification-badge');
        if (badge && data.unread_count > 0) {
            badge.textContent = data.unread_count;
            badge.style.display = 'block';
        }
    })
    .catch(error => console.error('Error fetching notifications:', error));
}

// Check notifications every 30 seconds
if (document.querySelector('.notification-badge')) {
    checkNotifications();
    setInterval(checkNotifications, 30000);
}

// ===== DARK MODE TOGGLE =====
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (!darkModeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    darkModeToggle.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// ===== BACK TO TOP BUTTON =====
function initBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTop.style.display = 'none';
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTop.style.display = 'flex';
        } else {
            backToTop.style.display = 'none';
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize back to top button
initBackToTop();

// ===== EXPORT FUNCTIONS =====
window.blogPlatform = {
    likePost,
    submitComment,
    sharePost,
    copyToClipboard,
    showAlert
};