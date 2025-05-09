# StormGamer

StormGamer is a modern gaming news portal that provides the latest updates, reviews, and information about the gaming world.

## Features

- Main page with infinite scroll news feed
- Article detail pages with full content
- Modern UI with gaming-inspired color scheme
- Responsive design for all devices
- API integration with gaming news source

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: External gaming news API
- **Deployment**: Railway.app

## Deployment

This application is configured for deployment on Railway.app.

### Prerequisites

- Python 3.9+
- Flask
- Requests
- Gunicorn (for production)

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Visit `http://localhost:5000` in your browser

### Production Deployment

The application is configured for Railway.app deployment with:
- Procfile for web process
- runtime.txt for Python version
- requirements.txt for dependencies

## License

© 2025 StormGamer. All rights reserved.
