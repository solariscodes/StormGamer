document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');
    const themeText = document.getElementById('theme-text');
    
    // Check for saved theme preference or use default dark theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
    
    // Function to set the theme
    function setTheme(theme) {
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            themeIcon.className = 'fas fa-sun';
            themeText.textContent = 'Dark Mode';
        } else {
            document.documentElement.removeAttribute('data-theme');
            themeIcon.className = 'fas fa-moon';
            themeText.textContent = 'Light Mode';
        }
    }
    
    // Variables for infinite scrolling
    let currentPage = 1;
    const perPage = 10;
    let isLoading = false;
    let hasMoreItems = true;
    let isSingleArticleView = false;
    
    const newsContainer = document.getElementById('news-container');
    const mainContentArea = document.querySelector('.main-content');
    const heroSection = document.querySelector('.hero');
    
    // Check if we're on the article page
    const articleView = document.querySelector('.full-article');
    if (articleView) {
        isSingleArticleView = true;
    }
    
    // Initial load
    loadArticles();
    
    // Function to load articles from API
    function loadArticles() {
        if (isLoading || !hasMoreItems) return;
        
        isLoading = true;
        showLoadingIndicator();
        
        fetch(`/api/articles?page=${currentPage}&per_page=${perPage}`)
            .then(response => response.json())
            .then(articles => {
                // Remove loading indicator
                hideLoadingIndicator();
                
                // If no articles or empty array, no more items to load
                if (!articles || articles.length === 0) {
                    hasMoreItems = false;
                    addNoMoreContent();
                    return;
                }
                
                // Append articles to the container
                articles.forEach(article => {
                    appendArticleCard(article);
                });
                
                // Increment page for the next load
                currentPage++;
                isLoading = false;
            })
            .catch(error => {
                console.error('Error loading articles:', error);
                hideLoadingIndicator();
                showErrorMessage();
                isLoading = false;
            });
    }
    
    // Create and append article card to container
    function appendArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'news-card';
        
        // Make card clickable if it has an ID
        if (article.id) {
            card.classList.add('clickable');
            card.setAttribute('data-article-id', article.id);
            card.addEventListener('click', function(e) {
                e.preventDefault();
                loadArticleContent(article.id);
            });
        }
        
        // Use Editorial instead of editor names
        const editorLabel = 'Editorial';
        
        // Use placeholder image if no image available
        const imageUrl = article.full_image_url || 'https://via.placeholder.com/400x200?text=StormGamer';
        
        card.innerHTML = `
            <img src="${imageUrl}" alt="${article.title || 'Gaming News'}" class="news-img" onerror="this.src='https://via.placeholder.com/400x200?text=StormGamer'">
            <div class="news-content">
                <h3 class="news-title">${article.title || 'No Title Available'}</h3>
                <div class="news-meta">
                    <span><i class="far fa-newspaper"></i> ${editorLabel}</span>
                    <span><i class="fas fa-share-alt"></i> Share</span>
                </div>
            </div>
            <div class="card-overlay">
                <span><i class="fas fa-eye"></i> Read More</span>
            </div>
        `;
        
        newsContainer.appendChild(card);
    }
    
    // Show loading indicator
    function showLoadingIndicator() {
        // Check if loading indicator exists
        let loading = document.querySelector('.loading');
        if (!loading) {
            loading = document.createElement('div');
            loading.className = 'loading';
            loading.innerHTML = '<div class="spinner"></div><p>Loading gaming news...</p>';
            newsContainer.appendChild(loading);
        }
    }
    
    // Hide loading indicator
    function hideLoadingIndicator() {
        const loading = document.querySelector('.loading');
        if (loading) {
            loading.remove();
        }
    }
    
    // Show error message
    function showErrorMessage() {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.innerHTML = '<p><i class="fas fa-exclamation-circle"></i> Failed to load gaming news. Please try again later.</p>';
        newsContainer.appendChild(errorMsg);
    }
    
    // Add no more content message
    function addNoMoreContent() {
        const noMoreMsg = document.createElement('div');
        noMoreMsg.className = 'no-more-content';
        noMoreMsg.innerHTML = '<p>You\'ve reached the end of the news feed!</p>';
        newsContainer.appendChild(noMoreMsg);
    }
    
    // Implement infinite scroll with footer visibility
    window.addEventListener('scroll', function() {
        // Only load more articles if we're not in single article view
        if (!isSingleArticleView) {
            const footer = document.querySelector('footer');
            const footerPosition = footer.getBoundingClientRect();
            
            // Load more content when user is approaching the footer but not yet there
            // This ensures the footer is visible before loading more content
            if (footerPosition.top < window.innerHeight + 300 && footerPosition.top > window.innerHeight) {
                loadArticles();
            }
        }
    });
    
    // Add event listener for search functionality
    const searchInput = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');
    
    // The search form now submits directly to the backend
    // No need to handle it with JavaScript anymore
    
    // Add event listener for mobile search toggle if needed
    if (document.querySelector('.mobile-search-toggle')) {
        document.querySelector('.mobile-search-toggle').addEventListener('click', function() {
            document.querySelector('.search-container').classList.toggle('active');
        });
    }
    
    // Function to load an article without full page reload
    function loadArticleContent(articleId) {
        isLoading = true;
        showLoadingIndicator();
        
        // Save the current scroll position
        localStorage.setItem('scrollPosition', window.scrollY);
        
        // Set the browser URL to match the article being viewed without page reload
        history.pushState({articleId: articleId}, '', `/article/${articleId}`);
        
        // Fetch the article content
        fetch(`/api/article/${articleId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Article not found');
                }
                return response.json();
            })
            .then(article => {
                hideLoadingIndicator();
                displayArticle(article);
                isLoading = false;
            })
            .catch(error => {
                console.error('Error loading article:', error);
                hideLoadingIndicator();
                showErrorMessage('Failed to load the article. Please try again.');
                isLoading = false;
            });
    }
    
    // Function to display a single article
    function displayArticle(article) {
        isSingleArticleView = true;
        
        // Hide the hero section with search and title
        if (heroSection) heroSection.style.display = 'none';
        
        // Change the news container to full width instead of grid
        newsContainer.classList.add('article-view-mode');
        
        // Create a full article layout that will fill the entire column
        const articleHTML = `
            <div class="single-article-card">
                
                <h1 class="article-title">${article.title || 'No Title Available'}</h1>
                
                <div class="article-meta-info">
                    <span class="article-author">
                        <i class="far fa-newspaper"></i> Editorial
                    </span>
                </div>
                
                <div class="article-featured-image">
                    <img src="${article.full_image_url || 'https://via.placeholder.com/1200x600?text=StormGamer'}" 
                         alt="${article.title || 'Article'}" 
                         onerror="this.src='https://via.placeholder.com/1200x600?text=StormGamer'">
                </div>
                
                <div class="article-full-content">
                    ${article.formatted_content || article.content || '<p>No content available for this article.</p>'}
                </div>
                
                <div class="article-footer">
                    <div class="share-buttons">
                        <span>Share:</span>
                        <a href="#" class="share-icon"><i class="fab fa-twitter"></i></a>
                        <a href="#" class="share-icon"><i class="fab fa-facebook-f"></i></a>
                    </div>
                    <a href="javascript:void(0)" onclick="showNewsList()" class="more-articles-link">
                        <i class="fas fa-th-large"></i> More Articles
                    </a>
                </div>
            </div>
        `;
        
        // Replace the news container content
        newsContainer.innerHTML = articleHTML;
        
        // Add the article.css styles if they're not already added
        if (!document.getElementById('article-styles')) {
            const articleStyles = document.createElement('link');
            articleStyles.id = 'article-styles';
            articleStyles.rel = 'stylesheet';
            articleStyles.href = '/static/css/article.css';
            document.head.appendChild(articleStyles);
        }
        
        // Scroll to top
        window.scrollTo(0, 0);
        
        // Update document title
        document.title = `${article.title || 'Article'} - StormGamer`;
    }
    
    // Array of editor names
    const editorNames = [
        "Lucas Silva",
        "Gabriel Oliveira",
        "Matheus Santos",
        "Rafael Costa",
        "Bruno Almeida",
        "Felipe Souza",
        "Thiago Pereira",
        "Leonardo Ferreira"
    ];
    
    // Helper function to get a random editor name
    function getRandomEditor() {
        const randomIndex = Math.floor(Math.random() * editorNames.length);
        return editorNames[randomIndex];
    }
    
    // Helper function to format the date or return a random editor
    function formatDate(dateString) {
        if (!dateString) return getRandomEditor();
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return getRandomEditor();
            }
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (e) {
            return getRandomEditor();
        }
    }
    
    // Function to go back to the news list
    function showNewsList() {
        // Show the news grid and hide the article view
        if (heroSection) heroSection.style.display = 'block';
        isSingleArticleView = false;
        
        // Remove the article-view-mode class to restore grid layout
        newsContainer.classList.remove('article-view-mode');
        
        // Clear the container
        newsContainer.innerHTML = '';
        
        // Reset and reload articles
        currentPage = 1;
        hasMoreItems = true;
        loadArticles();
        
        // Update the URL
        history.pushState({}, '', '/');
        
        // Update document title
        document.title = 'StormGamer - Gaming News Portal';
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function(event) {
        if (event.state && event.state.articleId) {
            loadArticleContent(event.state.articleId);
        } else {
            showNewsList();
        }
    });
});
