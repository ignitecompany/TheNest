import os
import re
import random
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_mail import Mail, Message
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session

load_dotenv('../.env')

# Configurazione ambiente
template_dir = os.path.abspath('/frontend/templates')
static_dir = os.path.abspath('/frontend/static')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv('FLASK_SECRETKEY')

# Configurazione Databse MySQL via SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurazione mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# ER

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_has = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pfp_url = db.Column(db.String(255))

    projects = db.relationship('Project', backref='author', lazy=True)

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    vision = db.Column(db.Text)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')
    live_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    roles = db.relationship('ProjectRole', backref='project', lazy=True, cascade='all, delete-orphan')

class ProjectRole(db.Model):
    __tablename__ = 'project_role'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[\W_]', password):
        return False
    return True


# Rotte

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        # Ricerca utente tramite SQLAlchemy (username o email)
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if user and check_password_hash(user.password_has, password):
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenziali non valide. Controlla username/email e password.'

    return render_template('login.html', error=error)

@app.route('/signup/step1', methods=['GET', 'POST'])
def signup_step1():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Questa email è già registrata.'
        elif not is_strong_password(password):
            error = 'La password deve avere almeno 8 caratteri, una maisucola, un numero e un carattere speciale.'
        else:
            otp_code = str(random.randint(100000, 999999))
            session['temp_email'] = email
            session['temp_password'] = generate_password_hash(password)
            session['otp_code'] = otp_code

            try:
                msg = Message(
                    subject='Codice di verifica - The Nest',
                    recipients=[email],
                )
                msg.html = render_template('email_verification.html', otp_code=otp_code)
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Errore invio email SMTP: {e}")
                error = 'Errore durante l\'invio dell\'email di verifica. Riprova più tardi.'
                return render_template('signup_step1.html', error=error)
            return redirect(url_for('signup_verify'))

    return render_template('signup_step1.html', error=error)

@app.route('/signup/verify', methods=['GET', 'POST'])
def signup_verify():
    if 'temp_email' not in session:
        return redirect(url_for('signup_step1'))

    error = None
    if request.method == 'POST':
        user_code = request.form.get('otp_code')
        if user_code == session.get('otp_code'):
            session.pop('otp_code', None)
            return redirect(url_for('signup_step2'))
        else:
            error = 'Codice di verifica errato. Riprova.'

    return render_template('signup_verify.html', error=error)

@app.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    if 'temp_email' not in session:
        return redirect(url_for('signup_step1'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            error = 'Questo username è già preso. Scegline un altro.'
        else:
            new_user = User(
                username=username,
                email=session['temp_email'],
                password_has=session['temp_password'],
                bio=bio
            )
            db.session.add(new_user)
            db.session.commit()

            session.pop('temp_email', None)
            session.pop('temp_password', None)
            session['user'] = username

            return redirect(url_for('dashboard'))

    return render_template('signup_step2.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

@app.route('/signup')
def signup():
    return redirect(url_for('signup_step1'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)