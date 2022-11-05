# gunicorn -w 4 'main:app'
# local: flask run

import math
import re
import sys
import sqlite3

from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    connection = sqlite3.connect('db.sqlite3')
    connection.row_factory = sqlite3.Row
    return connection

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def pagination():
    conn = get_db_connection()

    post_count = conn.execute("SELECT count(*) AS count FROM entry_post;").fetchone()
    total = math.ceil(post_count['count']/10)
    page_list = [int(a) for a in range(1, total+1, 1)]

    conn.close()
    return page_list

@app.route('/')
def index():
    page_list = pagination()

    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM entry_post ORDER BY created_at DESC LIMIT 10").fetchall()
    entries = []
    for p in posts:
        entry = {}
        entry['title'] = p['title']
        entry['slug'] = p['slug']
        entry['body_snippet'] = remove_html_tags(p['body'])[0:200]
        if p['updated_at']:
            entry['date'] = p['updated_at'][0:10]
        else:
            entry['date'] = p['created_at'][0:10]

        category_list = []
        categories = conn.execute(f"SELECT category_id FROM entry_postcategory WHERE post_id = {p['id']};").fetchall()
        for c in categories:
            cat_obj = conn.execute(f"SELECT id, name, slug FROM entry_category WHERE id = {c['category_id']};").fetchone()
            category_list.append(cat_obj)
        entry['category_list'] = category_list

        entries.append(entry)

    conn.close()
    return render_template('index.html', posts=entries, pagination=page_list)

@app.route('/post/<slug>/')
def post(slug):
    page_list = pagination()

    conn = get_db_connection()
    post = conn.execute(f"SELECT * FROM entry_post WHERE slug = '{slug}'").fetchone()

    entry = {}
    entry['title'] = post['title']
    entry['slug'] = post['slug']
    entry['body'] = post['body']
    if post['updated_at']:
        entry['date'] = post['updated_at'][0:10]
    else:
        entry['date'] = post['created_at'][0:10]

    category_list = []
    categories = conn.execute(f"SELECT category_id FROM entry_postcategory WHERE post_id = {post['id']};").fetchall()
    for c in categories:
        cat_obj = conn.execute(f"SELECT id, name, slug FROM entry_category WHERE id = {c['category_id']};").fetchone()
        category_list.append(cat_obj)
    entry['category_list'] = category_list

    conn.close()
    return render_template('post.html', entry=entry, pagination=page_list)

@app.route('/category/<category_id>/')
def categories(category_id):
    """ Get all posts for a single category """
    page_list = pagination()

    conn = get_db_connection()

    category_name = conn.execute(f"SELECT name FROM entry_category WHERE entry_category.id = {category_id};").fetchone()
    cat_obj = {"name": category_name['name'], "id": category_id}

    query = f"SELECT entry_post.id, entry_post.title, entry_post.slug, entry_post.updated_at, entry_post.created_at FROM entry_post JOIN entry_postcategory ON entry_postcategory.post_id = entry_post.id JOIN entry_category ON entry_category.id = entry_postcategory.category_id WHERE entry_category.id = {category_id} ORDER BY entry_post.created_at DESC;"
    posts = conn.execute(query).fetchall()
    entries = []
    for post in posts:
        entry = {}
        entry['title'] = post['title']
        entry['slug'] = post['slug']
        if post['updated_at']:
            entry['date'] = post['updated_at'][0:10]
        else:
            entry['date'] = post['created_at'][0:10]
        entries.append(entry)

    conn.close()
    return render_template('category_posts.html', posts=entries, category=cat_obj, pagination=page_list)

@app.route('/pages/<page_number>/')
def pages(page_number):
    page_list = pagination()

    conn = get_db_connection()

    total = len(page_list) * 10
    ids = total - ((int(page_number) * 10) - 10)
    query = f"SELECT * FROM entry_post WHERE id <= {ids} ORDER BY created_at DESC LIMIT 10"

    posts = conn.execute(query).fetchall()
    entries = []
    for p in posts:
        entry = {}
        entry['title'] = p['title']
        entry['slug'] = p['slug']
        entry['body_snippet'] = remove_html_tags(p['body'])[0:200]
        if p['updated_at']:
            entry['date'] = p['updated_at'][0:10]
        else:
            entry['date'] = p['created_at'][0:10]

        category_list = []
        categories = conn.execute(f"SELECT category_id FROM entry_postcategory WHERE post_id = {p['id']};").fetchall()
        for c in categories:
            cat_obj = conn.execute(f"SELECT id, name, slug FROM entry_category WHERE id = {c['category_id']};").fetchone()
            category_list.append(cat_obj)
        entry['category_list'] = category_list

        entries.append(entry)

    conn.close()
    return render_template('index.html', posts=entries, pagination=page_list)

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
