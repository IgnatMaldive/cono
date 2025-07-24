from functools import wraps
import hmac
import hashlib
import os
from flask import request, jsonify

def verify_github_signature(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not webhook_secret:
            return jsonify({'error': 'Webhook secret not configured'}), 500

        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return jsonify({'error': 'No signature header'}), 401

        # Get request body as bytes
        request_data = request.get_data()
        
        # Calculate expected signature
        expected_signature = 'sha256=' + hmac.new(
            webhook_secret.encode('utf-8'),
            request_data,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({'error': 'Invalid signature'}), 401

        return f(*args, **kwargs)
    return decorated_function

def validate_post_data(data):
    errors = []
    
    # Required fields
    if not data.get('title'):
        errors.append('Title is required')
    elif len(data['title']) > 200:
        errors.append('Title must be less than 200 characters')
    
    if not data.get('content'):
        errors.append('Content is required')
    
    # Optional fields
    tags = data.get('tags', [])
    if not isinstance(tags, list):
        errors.append('Tags must be an array')
    elif any(not isinstance(tag, str) for tag in tags):
        errors.append('All tags must be strings')
    elif any(len(tag) > 50 for tag in tags):
        errors.append('Tags must be less than 50 characters')
    
    author = data.get('author')
    if author and len(author) > 100:
        errors.append('Author name must be less than 100 characters')
    
    return errors
