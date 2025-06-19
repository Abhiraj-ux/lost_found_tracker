from flask import Flask, request, session, redirect, url_for, render_template, jsonify
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MySQL configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

# NLP Matching
def compute_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form.get('phone_no')
        password = request.form['password'].encode('utf-8')
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (username, email, password_hash, phone_no) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, phone_number)
            )
            conn.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password_hash FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password, user[1].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/lost_report', methods=['GET', 'POST'])
def lost_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session['user_id']
        category_id = request.form['category_id']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        item_name = request.form['item_name']
        description = request.form['description']
        date_lost = request.form['date_lost']
        phone_number = request.form.get('phone_no')
        image = request.files['image']

        image_path = None
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Locations (state, city, country) VALUES (%s, %s, %s)",
                (state, city, country)
            )
            location_id = cursor.lastrowid
            cursor.execute(
                """INSERT INTO LostItems 
                   (user_id, category_id, location_id, item_name, description, date_lost, phone_no, image_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, category_id, location_id, item_name, description, date_lost, phone_number, image_path)
            )
            conn.commit()
            lost_id = cursor.lastrowid
            match_items(lost_id, item_name, description)
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard'))
    return render_template('lost_report.html')

@app.route('/found_report', methods=['GET', 'POST'])
def found_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session['user_id']
        category_id = request.form['category_id']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        item_name = request.form['item_name']
        description = request.form['description']
        date_found = request.form['date_found']
        phone_number = request.form.get('phone_no')
        image = request.files['image']

        image_path = None
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Locations (state, city, country) VALUES (%s, %s, %s)",
                (state, city, country)
            )
            location_id = cursor.lastrowid
            cursor.execute(
                """INSERT INTO FoundItems 
                   (user_id, category_id, location_id, item_name, description, date_found, phone_no, image_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, category_id, location_id, item_name, description, date_found, phone_number, image_path)
            )
            conn.commit()
            found_id = cursor.lastrowid
            match_found_item(found_id, item_name, description)
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard'))
    return render_template('found_report.html')

@app.route('/matching')
def matching():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            lu.lost_id AS lost_item_id,
            lu.item_name AS lost_item_name,
            lu.description AS lost_description,
            lu.date_lost AS lost_date,
            lu.phone_no AS lost_phone_no,
            fu.found_id AS found_item_id,
            fu.item_name AS found_item_name,
            fu.description AS found_description,
            fu.date_found AS found_date,
            fu.phone_no AS found_phone_no,
            m.similarity_score
        FROM Matches m
        JOIN LostItems lu ON m.lost_id = lu.lost_id
        JOIN FoundItems fu ON m.found_id = fu.found_id
        ORDER BY m.similarity_score DESC
    """)
    matches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('matching.html', matches=matches)

# Matching Logic
def match_items(lost_id, lost_name, lost_description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT found_id, item_name, description FROM FoundItems")
    found_items = cursor.fetchall()

    for found_id, found_name, found_description in found_items:
        text1 = f"{lost_name} {lost_description}"
        text2 = f"{found_name} {found_description}"
        score = compute_similarity(text1, text2)
        if score > 0.5:
            cursor.execute(
                "INSERT INTO Matches (lost_id, found_id, similarity_score) VALUES (%s, %s, %s)",
                (lost_id, found_id, score)
            )
    conn.commit()
    cursor.close()
    conn.close()

def match_found_item(found_id, found_name, found_description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lost_id, item_name, description FROM LostItems")
    lost_items = cursor.fetchall()

    for lost_id, lost_name, lost_description in lost_items:
        text1 = f"{found_name} {found_description}"
        text2 = f"{lost_name} {lost_description}"
        score = compute_similarity(text1, text2)
        if score > 0.5:
            cursor.execute(
                "INSERT INTO Matches (lost_id, found_id, similarity_score) VALUES (%s, %s, %s)",
                (lost_id, found_id, score)
            )
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
