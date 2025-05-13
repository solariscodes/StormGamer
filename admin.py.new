import os
import time
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app, jsonify

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Store logs in memory
http_logs = []
MAX_LOGS = 1000  # Maximum number of logs to store

class RequestLog:
    def __init__(self, request, timestamp=None):
        self.timestamp = timestamp or datetime.now()
        self.method = getattr(request, 'method', 'UNKNOWN')
        self.path = getattr(request, 'path', 'UNKNOWN')
        self.args = dict(request.args) if hasattr(request, 'args') else {}
        self.form = dict(request.form) if hasattr(request, 'form') and request.form else None
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
    
    # Extract data
    ips = [log.remote_addr for log in logs]
    paths = [log.path for log in logs]
    user_agents = [log.user_agent for log in logs]
    methods = [log.method for log in logs]
    referrers = [log.referrer for log in logs if log.referrer]
    
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
    
    for log in logs:
        log_date = log.timestamp.date()
        log_hour = log.timestamp.replace(minute=0, second=0, microsecond=0)
        
        hourly_requests[log_hour.strftime('%Y-%m-%d %H:00')] += 1
        daily_requests[log_date.strftime('%Y-%m-%d')] += 1
    
    # Sort by time
    hourly_requests = dict(sorted(hourly_requests.items()))
    daily_requests = dict(sorted(daily_requests.items()))
    
    # Traffic by hour of day (0-23)
    traffic_by_hour = [0] * 24
    for log in logs:
        hour = log.timestamp.hour
        traffic_by_hour[hour] += 1
    
    # Count today's and this hour's requests
    requests_today = sum(1 for log in logs if log.timestamp.date() == today)
    requests_this_hour = sum(1 for log in logs if log.timestamp.replace(minute=0, second=0, microsecond=0) == current_hour)
    
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
    
    # Calculate statistics
    stats = calculate_statistics(http_logs)
    
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
    
    # Get the logs to display
    logs = [log.to_dict() for log in reversed(http_logs)]
    
    # Calculate statistics
    stats = calculate_statistics(http_logs)
    
    # Get server information
    server_info = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': os.sys.version,
        'flask_version': getattr(current_app, 'version', 'Unknown'),
        'request_count': len(http_logs),
        'unique_ips': stats['unique_ips_count'],
        'unique_user_agents': stats['unique_user_agents_count'],
        'most_visited_page': stats['most_visited_page'],
        'most_active_ip': stats['most_active_ip'],
        'requests_today': stats['requests_today'],
        'requests_this_hour': stats['requests_this_hour']
    }
    
    # Get recent visit times per IP for additional insight
    recent_visits = {}
    for log in http_logs:
        if log.remote_addr not in recent_visits:
            recent_visits[log.remote_addr] = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('admin_new.html', 
                           http_logs=http_logs, 
                           server_info=server_info, 
                           key=admin_key,
                           stats=stats,
                           recent_visits=recent_visits)

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
    
    # Clear the logs
    global http_logs
    http_logs = []
    
    return jsonify({'success': True})
