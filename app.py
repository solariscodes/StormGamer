from flask import Flask, render_template, jsonify, request, abort
import requests
import os
from admin import admin_bp, log_request

app = Flask(__name__, static_folder='static', template_folder='templates')

# Register the admin blueprint
app.register_blueprint(admin_bp)

# Set a default admin key if not provided in environment
if 'ADMIN' not in os.environ:
    os.environ['ADMIN'] = 'stormgamer_admin_key'  # Default key for development

# Log all requests
@app.before_request
def before_request():
    # Skip logging for static files
    if not request.path.startswith('/static/'):
        log_request(request)

API_BASE_URL = "https://web-production-cfff.up.railway.app"
ARTICLES_ENDPOINT = f"{API_BASE_URL}/articles"

# Editorial team data
EDITORIAL_TEAM = [
    {
        "name": "Rafael Oliveira",
        "role": "Chief Editor",
        "photo": "rafael.jpg",
        "bio": "Gamer since age 5, RPG specialist."
    },
    {
        "name": "Camila Santos",
        "role": "Content Editor",
        "photo": "camila.jpg",
        "bio": "Streamer and eSports commentator."
    },
    {
        "name": "Bruno Rodrigues",
        "role": "Writer",
        "photo": "bruno.jpg",
        "bio": "Strategy and simulation games expert."
    },
    {
        "name": "Fernanda Costa",
        "role": "Writer",
        "photo": "fernanda.jpg",
        "bio": "FPS and competitive games enthusiast."
    },
    {
        "name": "Thiago Almeida",
        "role": "Writer",
        "photo": "thiago.jpg",
        "bio": "Console and indie games specialist."
    },
    {
        "name": "Juliana Pereira",
        "role": "Social Media",
        "photo": "juliana.jpg",
        "bio": "Content creator and lifelong gamer."
    },
    {
        "name": "Lucas Silva",
        "role": "Video Editor",
        "photo": "lucas.jpg",
        "bio": "YouTuber and retro games expert."
    },
    {
        "name": "Mariana Ferreira",
        "role": "Proofreader",
        "photo": "mariana.jpg",
        "bio": "Translator and JRPG fan."
    }
]

@app.route('/')
def index():
    return render_template('index.html', editorial_team=EDITORIAL_TEAM)

@app.route('/article/<article_id>')
def article(article_id):
    # Call the external API to get all articles
    response = requests.get(ARTICLES_ENDPOINT)
    
    if response.status_code == 200:
        data = response.json()
        
        # Get the list of articles
        if isinstance(data, list):
            articles = data
        elif isinstance(data, dict) and 'articles' in data:
            articles = data['articles']
        else:
            abort(404)
        
        # Find the article with the matching ID
        article_found = None
        for article in articles:
            if not isinstance(article, dict):
                continue
                
            # Check if this is the article we're looking for
            if str(article.get('id', '')) == article_id:
                # Add full image URL if local path exists
                if 'local_image_path' in article:
                    article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
                
                # Format the content with paragraphs if it exists
                if 'content' in article and article['content']:
                    # Split by periods followed by space and rejoin with paragraph tags
                    content = article['content']
                    # Add paragraph breaks after sentences
                    content = content.replace('. ', '.</p><p>')
                    # Wrap the whole content in paragraph tags
                    article['formatted_content'] = f"<p>{content}</p>"
                
                article_found = article
                break
        
        if article_found:
            return render_template('article.html', article=article_found, editorial_team=EDITORIAL_TEAM)
    
    # Article not found
    abort(404)


@app.route('/api/article/<article_id>')
def api_article(article_id):
    # Call the external API to get all articles
    response = requests.get(ARTICLES_ENDPOINT)
    
    if response.status_code == 200:
        data = response.json()
        
        # Get the list of articles
        if isinstance(data, list):
            articles = data
        elif isinstance(data, dict) and 'articles' in data:
            articles = data['articles']
        else:
            return jsonify({'error': 'Article not found'}), 404
        
        # Find the article with the matching ID
        article_found = None
        for article in articles:
            if not isinstance(article, dict):
                continue
                
            # Check if this is the article we're looking for
            if str(article.get('id', '')) == article_id:
                # Add full image URL if local path exists
                if 'local_image_path' in article:
                    article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
                
                # Format the content with paragraphs if it exists
                if 'content' in article and article['content']:
                    # Split by periods followed by space and rejoin with paragraph tags
                    content = article['content']
                    # Add paragraph breaks after sentences
                    content = content.replace('. ', '.</p><p>')
                    # Wrap the whole content in paragraph tags
                    article['formatted_content'] = f"<p>{content}</p>"
                
                article_found = article
                break
        
        if article_found:
            return jsonify(article_found)
    
    # Article not found
    return jsonify({'error': 'Article not found'}), 404

@app.route('/api/articles')
def get_articles():
    # Get pagination parameters from request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Call the external API
    response = requests.get(ARTICLES_ENDPOINT)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if the response is a list or if articles are nested in the response
        if isinstance(data, list):
            articles = data
        elif isinstance(data, dict) and 'articles' in data:
            articles = data['articles']
        else:
            # Handle unexpected data structure
            return jsonify([])
        
        # Process each article
        processed_articles = []
        for article in articles:
            # Handle case where article might be a string or other non-dict
            if not isinstance(article, dict):
                continue
                
            # Add full image URL if local path exists
            if 'local_image_path' in article:
                article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
            
            processed_articles.append(article)
        
        # Simple pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Ensure we don't go out of bounds
        if start_idx >= len(processed_articles):
            return jsonify([])
            
        paginated_articles = processed_articles[start_idx:min(end_idx, len(processed_articles))]
        
        return jsonify(paginated_articles)
    
    return jsonify([])

@app.route('/search')
def search():
    # Get the search query from the request
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return redirect('/')
    
    # Call the external API to get all articles
    response = requests.get(ARTICLES_ENDPOINT)
    
    if response.status_code != 200:
        return render_template('search.html', query=query, articles=[], editorial_team=EDITORIAL_TEAM)
    
    data = response.json()
    
    # Get the list of articles
    if isinstance(data, list):
        articles = data
    elif isinstance(data, dict) and 'articles' in data:
        articles = data['articles']
    else:
        articles = []
    
    # Filter articles based on the search query
    search_results = []
    for article in articles:
        if not isinstance(article, dict):
            continue
            
        # Add full image URL if local path exists
        if 'local_image_path' in article:
            article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
        
        # Check if the query appears in the title, content, or author
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        author = article.get('author', '').lower()
        
        if query in title or query in content or query in author:
            search_results.append(article)
    
    return render_template('search.html', query=query, articles=search_results, editorial_team=EDITORIAL_TEAM)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
