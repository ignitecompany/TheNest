import os
import json
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session

load_dotenv('../.env')

# Puntamento diretto alla cartella frontend mappata in Docker
template_dir = os.path.abspath('/frontend/templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv('FLASK_SECRETKEY', 'chiave_segreta_default')

USERS_FILE = os.path.join(os.path.dirname(__file__), 'users_mock.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect(url_for('login'))

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        users = load_users()
        user = next((u for u in users if u['username'] == identifier or u['email'] == identifier), None)

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenziali non valide. Controlla username/email e password.'

    return render_template('login.html', error=error)

# --- SIGN-UP STEP 1 ---
@app.route('/signup/step1', methods=['GET', 'POST'])
def signup_step1():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_users()
        if any(u['email'] == email for u in users):
            error = 'Questa email è già registrata.'
        else:
            session['temp_email'] = email
            session['temp_password'] = generate_password_hash(password)
            return redirect(url_for('signup_step2'))

    return render_template('signup_step1.html', error=error)

# --- SIGN-UP STEP 2 ---
@app.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    if 'temp_email' not in session:
        return redirect(url_for('signup_step1'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')

        users = load_users()
        if any(u['username'] == username for u in users):
            error = 'Questo username è già preso. Scegline un altro.'
        else:
            new_user = {
                "id": len(users) + 1,
                "username": username,
                "email": session['temp_email'],
                "password_hash": session['temp_password'],
                "bio": bio,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            users.append(new_user)
            save_users(users)

            session.pop('temp_email', None)
            session.pop('temp_password', None)
            session['user'] = username

            return redirect(url_for('dashboard'))

    return render_template('signup_step2.html', error=error)

# --- DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)