# url_shortener.py (Updated for LinkedIn Preview)

from flask import Flask, render_template_string, request, redirect, g
import string
import random
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'urls.db'

# --- Database Functions ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL UNIQUE,
                long_url TEXT NOT NULL
            )
        ''')
        db.commit()

# --- Helper Function ---

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        cursor = get_db().cursor()
        cursor.execute("SELECT short_code FROM urls WHERE short_code = ?", (short_code,))
        if not cursor.fetchone():
            return short_code

# --- HTML Template ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener by Yash Vardhan Pandey</title>
    
    <!-- === ADDED META TAGS FOR LINKEDIN PREVIEW === -->
    <meta property="og:title" content="Full-Stack URL Shortener Project">
    <meta property="og:description" content="A custom URL shortener built with Python, Flask, and SQLite by Yash Vardhan Pandey. Deployed live on Render.">
    <meta property="og:type" content="website">
    
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #121212; color: #e0e0e0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background-color: #1e1e1e; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); text-align: center; width: 90%; max-width: 500px; }
        h1 { color: #00bcd4; margin-bottom: 20px; }
        input[type='url'] { width: calc(100% - 22px); padding: 10px; margin-bottom: 20px; border: 1px solid #333; border-radius: 5px; background-color: #2c2c2c; color: #e0e0e0; font-size: 16px; }
        button { background-color: #00bcd4; color: #121212; border: none; padding: 12px 20px; border-radius: 5px; font-size: 16px; cursor: pointer; transition: background-color 0.3s ease; }
        button:hover { background-color: #0097a7; }
        .result { margin-top: 30px; background-color: #2c2c2c; padding: 15px; border-radius: 5px; word-wrap: break-word; }
        .result a { color: #00e5ff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>URL Shortener</h1>
        <form method="post">
            <input type="url" name="long_url" placeholder="Enter a long URL here" required>
            <button type="submit">Shorten</button>
        </form>
        {% if short_url %}
        <div class="result">
            <p>Your shortened URL:</p>
            <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_code = generate_short_code()
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        db.commit()
        
        short_url = request.host_url + short_code
        return render_template_string(HTML_TEMPLATE, short_url=short_url)
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

# Initialize the database when the app starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)