from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.app import app, db
from backend.models import User, Job
import hashlib

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == hashlib.sha256(data['password'].encode()).hexdigest():
            login_user(user)
            return jsonify({'success': True})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        user = User(
            username=data['username'],
            email=data['email'],
            password=hashlib.sha256(data['password'].encode()).hexdigest(),
            steam_id=data['steam_id']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.timestamp.desc()).all()
    return render_template('dashboard.html', jobs=jobs)
