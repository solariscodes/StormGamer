import os
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Store logs in memory
http_logs = []
MAX_LOGS = 1000  # Maximum number of logs to store

class RequestLog:
    def __init__(self, request, timestamp=None):
        self.timestamp = timestamp or datetime.now()
        self.method = request.method
        self.path = request.path
        self.args = dict(request.args)
        self.form = dict(request.form) if request.form else None
        self.remote_addr = request.remote_addr
        self.user_agent = request.user_agent.string
        self.referrer = request.referrer

    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'method': self.method,
            'path': self.path,
            'args': self.args,
            'form': self.form,
            'remote_addr': self.remote_addr,
            'user_agent': self.user_agent,
            'referrer': self.referrer
        }

def log_request(request):
    """Add request to the logs"""
    global http_logs
    http_logs.append(RequestLog(request))
    
    # Trim logs if they exceed the maximum
    if len(http_logs) > MAX_LOGS:
        http_logs = http_logs[-MAX_LOGS:]

@admin_bp.route('/admin')
def admin_redirect():
    """Redirect to admin page with required key parameter"""
    return redirect(url_for('admin.admin_panel', key='REQUIRED'))

@admin_bp.route('/admin/panel')
def admin_panel():
    """Admin panel to view HTTP logs"""
    # Get the admin key from environment variable
    admin_key = os.environ.get('ADMIN', 'default_key_for_development')
    
    # Check if the key parameter matches the environment variable
    if request.args.get('key') != admin_key:
        abort(403)  # Forbidden
    
    # Clear logs if requested
    if request.args.get('clear') == '1':
        global http_logs
        http_logs = []
        return redirect(url_for('admin.admin_panel', key=admin_key))
    
    # Get the logs to display
    logs = [log.to_dict() for log in reversed(http_logs)]
    
    # Get server information
    server_info = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': os.sys.version,
        'flask_version': current_app.version,
        'request_count': len(http_logs),
    }
    
    return render_template('admin.html', logs=logs, server_info=server_info, admin_key=admin_key)
