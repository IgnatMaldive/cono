from flask import Flask, render_template, url_for
import os
import markdown
from datetime import datetime
import requests
import random
import string

app = Flask(__name__)

def parse_frontmatter(content):
    frontmatter = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            fm_str = parts[1].strip()
            body = parts[2].strip()
            for line in fm_str.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter, body


def get_blog_posts():
    posts = []
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'contents')
    for filename in os.listdir(content_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(content_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                full_content = f.read()
                frontmatter, content = parse_frontmatter(full_content)
                html_content = markdown.markdown(content) # Convert Markdown to HTML
            
            title = frontmatter.get('title', os.path.splitext(filename)[0].replace("-", " ").title())
            date_str = frontmatter.get('date', filename.split("-")[0])
            
            posts.append({
                'filename': filename,
                'title': title,
                'date': date_str,
                'content': html_content,
                'frontmatter': frontmatter
            })
    # Sort posts by date, newest first
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

@app.route('/')
def hello():
    posts = get_blog_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<filename>')
def post(filename):
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'contents')
    filepath = os.path.join(content_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        full_content = f.read()
        frontmatter, content = parse_frontmatter(full_content)
        html_content = markdown.markdown(content)
    title = frontmatter.get('title', os.path.splitext(filename)[0].replace("-", " ").title())
    return render_template('post.html', post={'title': title, 'html_content': html_content, 'frontmatter': frontmatter})

@app.route('/test')
def test():
    return 'Test'

@app.route('/result')
def result():
   dict = {'phy':50,'che':60,'maths':70}
   return render_template('result.html', result = dict)

import base64

from flask import request, redirect

@app.route('/admin')
def admin():
    posts = get_blog_posts()
    return render_template('admin.html', posts=posts)

@app.route('/admin/create-post', methods=['POST'])
def create_post():
    title = request.form.get('title', 'Untitled Post') # Use .get with default for robustness
    content = request.form['content']
    
    # Generate current date for frontmatter
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Construct content with frontmatter
    full_content = f"---\ntitle: {title}\ndate: {current_date}\n---\n{content}"

    encoded_content = base64.b64encode(full_content.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {os.environ["GHTOKEN"]}',
    }

    data = {
        'event_type': 'create-dated-file',
        'client_payload': {
            'title': title, # Keep this as per remote's change
            'content': encoded_content,
        },
    }

    repo = os.environ.get('GITHUB_REPOSITORY', 'IgnatMaldive/cono')
    response = requests.post(f'https://api.github.com/repos/{repo}/dispatches', headers=headers, json=data)

    if response.ok:
        return redirect(url_for('hello'))
    else:
        return 'Error', 500

@app.route('/admin/edit-post/<filename>')
def edit_post(filename):
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'contents')
    filepath = os.path.join(content_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        full_content = f.read()
        frontmatter, content = parse_frontmatter(full_content)
    title = frontmatter.get('title', os.path.splitext(filename)[0].replace("-", " ").title())
    return render_template('edit_post.html', filename=filename, title=title, content=content, frontmatter=frontmatter)

@app.route('/admin/update-post', methods=['POST'])
def update_post():
    filename = request.form['filename']
    content = request.form['content']
    title = request.form.get('title', 'Untitled Post')

    repo = os.environ.get('GITHUB_REPOSITORY', 'IgnatMaldive/cono')

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {os.environ["GHTOKEN"]}',
    }

    # Get the current SHA and existing frontmatter
    response = requests.get(f'https://api.github.com/repos/{repo}/contents/contents/{filename}', headers=headers)

    if not response.ok:
        return 'Error getting file SHA', 500

    file_data = response.json()
    sha = file_data['sha']
    existing_content_b64 = file_data['content']
    existing_full_content = base64.b64decode(existing_content_b64).decode('utf-8')
    existing_frontmatter, _ = parse_frontmatter(existing_full_content)

    # Update frontmatter with new title, keep existing date or update if needed
    existing_frontmatter['title'] = title
    # You might want to update the date here if the post content changes significantly
    # existing_frontmatter['date'] = datetime.now().strftime("%Y-%m-%d")

    # Reconstruct frontmatter string
    fm_str = ""
    for key, value in existing_frontmatter.items():
        fm_str += f"{key}: {value}\n"

    full_content = f"---\n{fm_str}---\n{content}"

    encoded_content = base64.b64encode(full_content.encode('utf-8')).decode('utf-8')

    data = {
        'message': f'Update post: {filename}',
        'content': encoded_content,
        'sha': sha,
        'branch': 'main' # Assuming 'main' is your default branch
    }

    response = requests.put(f'https://api.github.com/repos/{repo}/contents/contents/{filename}', headers=headers, json=data)

    if response.ok:
        return redirect(url_for('hello'))
    else:
        return 'Error updating file', 500

@app.route('/admin/delete-post', methods=['POST'])
def delete_post():
    filename = request.form['filename']
    
    repo = os.environ.get('GITHUB_REPOSITORY', 'IgnatMaldive/cono')
    
    # Get the current SHA of the file
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {os.environ["GHTOKEN"]}',
    }
    
    response = requests.get(f'https://api.github.com/repos/{repo}/contents/contents/{filename}', headers=headers)
    
    if not response.ok:
        return 'Error getting file SHA for deletion', 500
    
    file_data = response.json()
    sha = file_data['sha']
    
    data = {
        'message': f'Delete post: {filename}',
        'sha': sha,
        'branch': 'main' # Assuming 'main' is your default branch
    }
    
    response = requests.delete(f'https://api.github.com/repos/{repo}/contents/contents/{filename}', headers=headers, json=data)
    
    if response.ok:
        return redirect(url_for('hello'))
    else:
        return 'Error deleting file', 500