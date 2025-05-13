import os
import time
import json
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app, jsonify

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Set up logging to files
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create log files for different categories
NORMAL_LOG_FILE = os.path.join(LOG_DIR, 'normal.log')
ADMIN_LOG_FILE = os.path.join(LOG_DIR, 'admin.log')
RANDOM_URI_LOG_FILE = os.path.join(LOG_DIR, 'random_uri.log')

# Cache for logs to avoid reading files repeatedly
log_cache = {
    'normal': [],
    'admin': [],
    'random_uri': []
}

# Function to load logs from file
def load_logs(log_type):
    """Load logs from file into memory cache"""
    if log_type == 'normal':
        file_path = NORMAL_LOG_FILE
    elif log_type == 'admin':
        file_path = ADMIN_LOG_FILE
    elif log_type == 'random_uri':
        file_path = RANDOM_URI_LOG_FILE
    else:
        return []
    
    logs = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        log_data = json.loads(line.strip())
                        # Convert string timestamp back to datetime
                        if 'timestamp' in log_data:
                            log_data['timestamp'] = datetime.strptime(log_data['timestamp'], '%Y-%m-%d %H:%M:%S')
                        logs.append(RequestLog.from_dict(log_data))
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
        except Exception as e:
            print(f"Error loading logs from {file_path}: {e}")
    
    return logs

class RequestLog:
    def __init__(self, request=None, timestamp=None, is_admin=False, is_random_uri=False, **kwargs):
        if request:
            self.timestamp = timestamp or datetime.now()
            self.method = getattr(request, 'method', 'UNKNOWN')
            self.path = getattr(request, 'path', 'UNKNOWN')
            self.args = dict(request.args) if hasattr(request, 'args') else {}
            self.form = dict(request.form) if hasattr(request, 'form') and request.form else None
            self.is_admin = is_admin  # Flag to identify admin routes
            self.is_random_uri = is_random_uri  # Flag to identify random URIs
            
            # Get the real IP address from proxy headers
            if hasattr(request, 'headers') and request.headers.get('X-Forwarded-For'):
                self.remote_addr = request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif hasattr(request, 'headers') and request.headers.get('X-Real-IP'):
                self.remote_addr = request.headers.get('X-Real-IP')
            else:
                self.remote_addr = getattr(request, 'remote_addr', 'UNKNOWN')
            
            # Handle user agent safely
            if hasattr(request, 'user_agent') and request.user_agent:
                self.user_agent = getattr(request.user_agent, 'string', str(request.user_agent))
            else:
                self.user_agent = 'UNKNOWN'
                
            self.referrer = getattr(request, 'referrer', None)
        else:
            # Initialize from kwargs (used when loading from file)
            self.timestamp = kwargs.get('timestamp', datetime.now())
            self.method = kwargs.get('method', 'UNKNOWN')
            self.path = kwargs.get('path', 'UNKNOWN')
            self.args = kwargs.get('args', {})
            self.form = kwargs.get('form', None)
            self.remote_addr = kwargs.get('remote_addr', 'UNKNOWN')
            self.user_agent = kwargs.get('user_agent', 'UNKNOWN')
            self.referrer = kwargs.get('referrer', None)
            self.is_admin = kwargs.get('is_admin', False)
            self.is_random_uri = kwargs.get('is_random_uri', False)

    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.timestamp, datetime) else self.timestamp,
            'method': self.method,
            'path': self.path,
            'args': self.args,
            'form': self.form,
            'remote_addr': self.remote_addr,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'is_admin': self.is_admin,
            'is_random_uri': self.is_random_uri
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a RequestLog instance from a dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        return cls(**data)

def log_request(request):
    """Add request to the appropriate logs file"""
    path = request.path
    
    # Determine if this is an admin route or a random URI
    is_admin = path.startswith('/admin')
    
    # Check if the path matches any registered routes
    is_random_uri = False
    if current_app:
        # Get all registered routes
        registered_routes = [rule.rule for rule in current_app.url_map.iter_rules()]
        # Check if the path matches any route (simple check, doesn't account for parameters)
        if not any(path == route or path.startswith(route.rstrip('/')) for route in registered_routes):
            is_random_uri = True
    
    # Create the log entry
    log_entry = RequestLog(request, is_admin=is_admin, is_random_uri=is_random_uri)
    log_dict = log_entry.to_dict()
    
    # Determine which log file to use
    if is_admin:
        log_file = ADMIN_LOG_FILE
        log_cache['admin'].append(log_entry)
    elif is_random_uri:
        log_file = RANDOM_URI_LOG_FILE
        log_cache['random_uri'].append(log_entry)
    else:
        log_file = NORMAL_LOG_FILE
        log_cache['normal'].append(log_entry)
    
    # Write to log file
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_dict) + '\n')
    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")

@admin_bp.route('/admin')
def admin_redirect():
    """Redirect to admin page with required key parameter"""
    return redirect(url_for('admin.admin_panel', key='REQUIRED'))


def calculate_statistics(logs):
    """Calculate various statistics from the logs"""
    if not logs:
        return {
            'unique_ips': [],
            'unique_ips_count': 0,
            'ip_frequency': {},
            'top_ips': [],  # Empty pre-sliced list
            'path_frequency': {},
            'top_paths': [],  # Empty pre-sliced list
            'user_agent_frequency': {},
            'top_user_agents': [],  # Empty pre-sliced list
            'hourly_requests': {},
            'daily_requests': {},
            'method_distribution': {},
            'status_distribution': {},
            'unique_user_agents': [],
            'unique_user_agents_count': 0,
            'most_visited_page': 'None',
            'most_active_ip': 'None',
            'requests_today': 0,
            'requests_this_hour': 0,
            'referrer_distribution': {},
            'traffic_by_hour': [],
            'recent_errors': [],
            'geo_distribution': {}
        }
    
    # Extract data - filter out admin routes for statistics
    filtered_logs = [log for log in logs if not getattr(log, 'is_admin', False)]
    
    if not filtered_logs:
        return {
            'unique_ips': [],
            'unique_ips_count': 0,
            'ip_frequency': {},
            'top_ips': [],
            'path_frequency': {},
            'top_paths': [],
            'user_agent_frequency': {},
            'top_user_agents': [],
            'hourly_requests': {},
            'daily_requests': {},
            'method_distribution': {},
            'unique_user_agents': [],
            'unique_user_agents_count': 0,
            'most_visited_page': 'None',
            'most_active_ip': 'None',
            'requests_today': 0,
            'requests_this_hour': 0,
            'referrer_distribution': {},
            'traffic_by_hour': []
        }
    
    # Extract data
    ips = [log.remote_addr for log in filtered_logs]
    paths = [log.path for log in filtered_logs]
    user_agents = [log.user_agent for log in filtered_logs]
    methods = [log.method for log in filtered_logs]
    referrers = [log.referrer for log in filtered_logs if log.referrer]
    
    # Count unique IPs
    unique_ips = list(set(ips))
    ip_frequency = dict(Counter(ips).most_common())
    
    # Count unique paths
    path_frequency = dict(Counter(paths).most_common())
    
    # Count unique user agents
    unique_user_agents = list(set(user_agents))
    user_agent_frequency = dict(Counter(user_agents).most_common())
    
    # Count HTTP methods
    method_distribution = dict(Counter(methods))
    
    # Count referrers
    referrer_distribution = dict(Counter(referrers).most_common(10))
    
    # Time-based statistics
    now = datetime.now()
    today = now.date()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    
    # Requests by hour and day
    hourly_requests = defaultdict(int)
    daily_requests = defaultdict(int)
    
    for log in filtered_logs:
        log_date = log.timestamp.date()
        log_hour = log.timestamp.replace(minute=0, second=0, microsecond=0)
        
        hourly_requests[log_hour.strftime('%Y-%m-%d %H:00')] += 1
        daily_requests[log_date.strftime('%Y-%m-%d')] += 1
    
    # Sort by time
    hourly_requests = dict(sorted(hourly_requests.items()))
    daily_requests = dict(sorted(daily_requests.items()))
    
    # Traffic by hour of day (0-23)
    traffic_by_hour = [0] * 24
    for log in filtered_logs:
        hour = log.timestamp.hour
        traffic_by_hour[hour] += 1
    
    # Count today's and this hour's requests
    requests_today = sum(1 for log in filtered_logs if log.timestamp.date() == today)
    requests_this_hour = sum(1 for log in filtered_logs if log.timestamp.replace(minute=0, second=0, microsecond=0) == current_hour)
    
    # Find most visited page and most active IP
    most_visited_page = max(path_frequency.items(), key=lambda x: x[1])[0] if path_frequency else 'None'
    most_active_ip = max(ip_frequency.items(), key=lambda x: x[1])[0] if ip_frequency else 'None'
    
    # Prepare data for charts
    hourly_data = [{'time': k, 'count': v} for k, v in list(hourly_requests.items())[-24:]]
    daily_data = [{'date': k, 'count': v} for k, v in list(daily_requests.items())[-30:]]
    
    # Convert dictionary items to lists for template usage
    top_ips = list(ip_frequency.items())[:10]
    top_paths = list(path_frequency.items())[:15]  # Get top 15 paths (was originally [:15] in template)
    top_user_agents = list(user_agent_frequency.items())[:10]
    
    return {
        'unique_ips': unique_ips,
        'unique_ips_count': len(unique_ips),
        'ip_frequency': ip_frequency,
        'top_ips': top_ips,  # Pre-sliced top 10 IPs
        'path_frequency': path_frequency,
        'top_paths': top_paths,  # Pre-sliced top 10 paths
        'user_agent_frequency': user_agent_frequency,
        'top_user_agents': top_user_agents,  # Pre-sliced top 10 user agents
        'hourly_requests': hourly_data,
        'daily_requests': daily_data,
        'method_distribution': method_distribution,
        'unique_user_agents': unique_user_agents,
        'unique_user_agents_count': len(unique_user_agents),
        'most_visited_page': most_visited_page,
        'most_active_ip': most_active_ip,
        'requests_today': requests_today,
        'requests_this_hour': requests_this_hour,
        'referrer_distribution': referrer_distribution,
        'traffic_by_hour': traffic_by_hour
    }


@admin_bp.route('/admin/api/stats')
def admin_api_stats():
    """API endpoint to get statistics in JSON format"""
    # Get the admin key from environment variable
    admin_key = os.environ.get('ADMIN')
    
    # If ADMIN environment variable is not set, deny access
    if not admin_key:
        abort(403)  # Forbidden
    
    # Check if the key parameter matches the environment variable
    if request.args.get('key') != admin_key:
        abort(403)  # Forbidden
    
    # Load logs if cache is empty
    if not log_cache['normal']:
        log_cache['normal'] = load_logs('normal')
    
    # Calculate statistics
    stats = calculate_statistics(log_cache['normal'])
    
    return jsonify(stats)

@admin_bp.route('/admin/panel')
def admin_panel():
    """Admin panel to view HTTP logs"""
    # Get the admin key from environment variable
    admin_key = os.environ.get('ADMIN')
    
    # If ADMIN environment variable is not set, deny access
    if not admin_key:
        abort(403)  # Forbidden
    
    # Check if the key parameter matches the environment variable
    if request.args.get('key') != admin_key:
        abort(403)  # Forbidden
    
    # Get log type from query parameter, default to normal logs
    log_type = request.args.get('log_type', 'normal')
    
    # Ensure log type is valid
    if log_type not in ['normal', 'admin', 'random_uri']:
        log_type = 'normal'
    
    # Load logs if cache is empty
    if not log_cache[log_type]:
        log_cache[log_type] = load_logs(log_type)
    
    # If normal logs are not loaded yet, load them for statistics
    if not log_cache['normal'] and log_type != 'normal':
        log_cache['normal'] = load_logs('normal')
    
    # Get the logs to display
    logs_to_display = log_cache[log_type]
    logs = [log.to_dict() for log in reversed(logs_to_display)]
    
    # Calculate statistics from normal logs only (excluding admin routes)
    stats = calculate_statistics(log_cache['normal'])
    
    # Get log counts
    log_counts = {
        'normal': len(log_cache['normal']),
        'admin': len(log_cache['admin']) if log_cache['admin'] else len(load_logs('admin')),
        'random_uri': len(log_cache['random_uri']) if log_cache['random_uri'] else len(load_logs('random_uri')),
    }
    log_counts['total'] = log_counts['normal'] + log_counts['admin'] + log_counts['random_uri']
    
    # Get server information
    server_info = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': os.sys.version,
        'flask_version': getattr(current_app, 'version', 'Unknown'),
        'request_count': log_counts['normal'],  # Only count normal logs
        'unique_ips': stats['unique_ips_count'],
        'unique_user_agents': stats['unique_user_agents_count'],
        'most_visited_page': stats['most_visited_page'],
        'most_active_ip': stats['most_active_ip'],
        'requests_today': stats['requests_today'],
        'requests_this_hour': stats['requests_this_hour']
    }
    
    # Get recent visit times per IP for additional insight
    recent_visits = {}
    for log in log_cache['normal']:
        if log.remote_addr not in recent_visits:
            recent_visits[log.remote_addr] = log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(log.timestamp, datetime) else log.timestamp
    
    return render_template('admin_new.html', 
                           http_logs=logs,  # Use the selected logs
                           server_info=server_info, 
                           key=admin_key,
                           stats=stats,
                           recent_visits=recent_visits,
                           log_counts=log_counts,
                           active_tab=log_type)

@admin_bp.route('/admin/clear-logs', methods=['POST'])
def clear_logs():
    """API endpoint to clear logs"""
    # Get the admin key from environment variable
    admin_key = os.environ.get('ADMIN')
    
    # If ADMIN environment variable is not set, deny access
    if not admin_key:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Check if the key parameter matches the environment variable
    if request.args.get('key') != admin_key:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        # Get log type from query parameter, default to all
        log_type = request.args.get('log_type', 'all')
        
        # Print debug info
        print(f"Clearing logs of type: {log_type}")
        
        # Clear the specified logs
        if log_type == 'normal' or log_type == 'all':
            log_cache['normal'] = []
            if os.path.exists(NORMAL_LOG_FILE):
                with open(NORMAL_LOG_FILE, 'w') as f:
                    f.write('')  # Clear file
        
        if log_type == 'admin' or log_type == 'all':
            log_cache['admin'] = []
            if os.path.exists(ADMIN_LOG_FILE):
                with open(ADMIN_LOG_FILE, 'w') as f:
                    f.write('')  # Clear file
        
        if log_type == 'random_uri' or log_type == 'all':
            log_cache['random_uri'] = []
            if os.path.exists(RANDOM_URI_LOG_FILE):
                with open(RANDOM_URI_LOG_FILE, 'w') as f:
                    f.write('')  # Clear file
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error clearing logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Create the log directory and files if they don't exist
def init_log_files():
    """Initialize log files if they don't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    for file_path in [NORMAL_LOG_FILE, ADMIN_LOG_FILE, RANDOM_URI_LOG_FILE]:
        if not os.path.exists(file_path):
            open(file_path, 'a').close()

# Initialize log files when module is loaded
init_log_files()
