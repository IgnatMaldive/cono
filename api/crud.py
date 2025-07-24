from flask import Blueprint, request, jsonify
import os
import re
from datetime import datetime
import requests
from urllib.parse import quote

crud = Blueprint('crud', __name__)

def generate_slug(title):
    """Generate a URL-friendly slug from a title."""
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Replace whitespace with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def create_frontmatter(title, date=None, tags=None, author=None):
    """Generate YAML frontmatter for a blog post."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    frontmatter = [
        '---',
        f'title: {title}',
        f'date: {date}'
    ]
    
    if tags:
        frontmatter.append(f'tags: {", ".join(tags)}')
    if author:
        frontmatter.append(f'author: {author}')
    
    frontmatter.append('---\n')
    return '\n'.join(frontmatter)

@crud.route('/api/posts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', [])
        author = data.get('author')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        # Generate slug and date
        date = datetime.now().strftime('%Y-%m-%d')
        slug = generate_slug(title)
        filename = f"{date}-{slug}.md"

        # Create frontmatter
        frontmatter = create_frontmatter(title, date, tags, author)
        
        # Combine frontmatter and content
        full_content = f"{frontmatter}\n{content}"

        # Trigger GitHub action
        github_token = os.environ.get('GHTOKEN')
        if not github_token:
            return jsonify({'error': 'GitHub token not configured'}), 500

        response = requests.post(
            'https://api.github.com/repos/IgnatMaldive/cono/dispatches',
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {github_token}',
            },
            json={
                'event_type': 'create-post',
                'client_payload': {
                    'filename': filename,
                    'content': full_content
                }
            }
        )

        if response.status_code != 204:
            return jsonify({'error': f'GitHub API error: {response.text}'}), response.status_code

        return jsonify({
            'message': 'Post creation triggered',
            'filename': filename,
            'slug': slug
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crud.route('/api/posts/<path:filename>', methods=['PUT'])
def update_post(filename):
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', [])
        author = data.get('author')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        # Create frontmatter
        frontmatter = create_frontmatter(title, None, tags, author)
        
        # Combine frontmatter and content
        full_content = f"{frontmatter}\n{content}"

        # Trigger GitHub action
        github_token = os.environ.get('GHTOKEN')
        if not github_token:
            return jsonify({'error': 'GitHub token not configured'}), 500

        response = requests.post(
            'https://api.github.com/repos/IgnatMaldive/cono/dispatches',
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {github_token}',
            },
            json={
                'event_type': 'update-post',
                'client_payload': {
                    'filename': filename,
                    'content': full_content
                }
            }
        )

        if response.status_code != 204:
            return jsonify({'error': f'GitHub API error: {response.text}'}), response.status_code

        return jsonify({
            'message': 'Post update triggered',
            'filename': filename
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crud.route('/api/posts/<path:filename>', methods=['DELETE'])
def delete_post(filename):
    try:
        # Trigger GitHub action
        github_token = os.environ.get('GHTOKEN')
        if not github_token:
            return jsonify({'error': 'GitHub token not configured'}), 500

        response = requests.post(
            'https://api.github.com/repos/IgnatMaldive/cono/dispatches',
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {github_token}',
            },
            json={
                'event_type': 'delete-post',
                'client_payload': {
                    'filename': filename
                }
            }
        )

        if response.status_code != 204:
            return jsonify({'error': f'GitHub API error: {response.text}'}), response.status_code

        return jsonify({
            'message': 'Post deletion triggered',
            'filename': filename
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500
