from flask import Flask, render_template, jsonify, request, abort, redirect, Response
import requests
import os
from admin import admin_bp, log_request
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')

# Register the admin blueprint
app.register_blueprint(admin_bp)

# Log all requests
@app.before_request
def before_request():
    # Skip logging for static files
    if not request.path.startswith('/static/'):
        log_request(request)

# Add routes for robots.txt and sitemap.xml
@app.route('/robots.txt')
def robots_txt():
    # Read the static robots.txt file
    robots_content = open(os.path.join(app.static_folder, 'robots.txt'), 'r').read()
    
    # Replace the placeholder sitemap URL with the actual URL
    sitemap_url = request.url_root.rstrip('/') + "/sitemap.xml"
    robots_content = robots_content.replace('Sitemap: /sitemap.xml', f'Sitemap: {sitemap_url}')
    
    # Return the modified content
    return Response(robots_content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    # Generate dynamic sitemap with current date
    now = datetime.now()
    sitemap_template = app.jinja_env.get_template('sitemap.xml')
    return Response(sitemap_template.render(now=now, request=request), mimetype='application/xml')

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
    return render_template('index.html', editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)

@app.route('/article/<article_id>')
def article(article_id):
    # Check if this is a fragment request from JavaScript
    is_fragment = request.args.get('format') == 'fragment'
    
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
                if 'local_image_path' in article and article['local_image_path']:
                    article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
                # Ensure we have an ID for generating color hash fallbacks
                if 'id' not in article:
                    article['id'] = article_id
                
                # Only process articles with images
                if not ('full_image_url' in article or ('local_image_path' in article and article['local_image_path'])):
                    abort(404)
                    
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
            # For direct access, we already log the request via the before_request handler
            # Make all articles available to the template for the "Next Article" feature
            # Filter articles to only include those with images
            articles_with_images = [a for a in articles if 'full_image_url' in a or ('local_image_path' in a and a['local_image_path'])]
            return render_template('article.html', article=article_found, all_articles=articles_with_images, 
                                  editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL,
                                  is_fragment=is_fragment)
    
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

@app.route('/search')
def search():
    # Get the search query from the request
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return redirect('/')
    
    # Call the external API to get all articles
    response = requests.get(ARTICLES_ENDPOINT)
    
    if response.status_code != 200:
        return render_template('search.html', query=query, articles=[], editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)
    
    data = response.json()
    
    # Get the list of articles
    if isinstance(data, list):
        articles = data
    elif isinstance(data, dict) and 'articles' in data:
        articles = data['articles']
    else:
        articles = []
    
    # Filter articles based on the search query and ensure they have images
    search_results = []
    for article in articles:
        if not isinstance(article, dict):
            continue
            
        # Add full image URL if local path exists
        if 'local_image_path' in article and article['local_image_path']:
            article['full_image_url'] = f"{API_BASE_URL}/{article['local_image_path']}"
        
        # Skip articles without images
        if not (article.get('full_image_url') or (article.get('local_image_path') and article['local_image_path'].strip())):
            continue
        
        # Check if the query appears in the title, content, or author
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        author = article.get('author', '').lower()
        
        if query in title or query in content or query in author:
            search_results.append(article)
    
    return render_template('search.html', query=query, articles=search_results, editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)

@app.route('/team')
def team():
    """Page for the editorial team"""
    return render_template('team.html', editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)

@app.route('/team/<member_name>')
def team_member(member_name):
    """Page for a specific team member"""
    # Find the team member with the matching name
    member_found = None
    for member in EDITORIAL_TEAM:
        # Convert name to URL-friendly format for comparison
        url_name = member['name'].lower().replace(' ', '-')
        if url_name == member_name:
            member_found = member
            break
    
    if member_found:
        return render_template('team_member.html', member=member_found, editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)
    else:
        abort(404)  # Member not found

@app.route('/track-view/article/<article_id>')
def track_article_view(article_id):
    """Track an article view when loaded via JavaScript (doesn't render a page)"""
    # We create a simulated request with the proper path to log it correctly
    class SimulatedRequest:
        def __init__(self, path, method="GET", remote_addr=None, user_agent=None, referrer=None):
            self.path = path
            self.method = method
            self.args = {}
            self.form = {}
            self.remote_addr = remote_addr or request.remote_addr
            self.user_agent = user_agent or request.user_agent
            self.referrer = referrer or request.referrer
            self.headers = request.headers
    
    # Create a simulated request that mimics what would happen if user navigated directly
    simulated_req = SimulatedRequest(path=f"/article/{article_id}")
    
    # Log this simulated request
    log_request(simulated_req)
    
    # Return an empty response with 200 status
    return "", 200

@app.route('/auth')
def auth():
    """Page for sign in and sign up"""
    return render_template('auth.html', editorial_team=EDITORIAL_TEAM, api_base_url=API_BASE_URL)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
