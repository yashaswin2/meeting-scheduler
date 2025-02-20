from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meetings.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=True)  # Made name optional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    meetings = db.relationship('Meeting', backref='organizer', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes
    template_type = db.Column(db.String(50), nullable=False, default='basic')
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Meeting templates
MEETING_TEMPLATES = {
    'basic': {
        'name': 'Basic Meeting',
        'sections': ['Agenda', 'Discussion Points', 'Action Items', 'Next Steps']
    },
    'scrum': {
        'name': 'Scrum Meeting',
        'sections': ['What did you do yesterday?', 'What will you do today?', 'Any blockers?']
    },
    'project_review': {
        'name': 'Project Review',
        'sections': ['Project Status', 'Milestones', 'Risks', 'Budget', 'Timeline']
    },
    'brainstorming': {
        'name': 'Brainstorming',
        'sections': ['Topic', 'Ideas Generated', 'Selected Ideas', 'Next Actions']
    }
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    meetings = Meeting.query.filter_by(user_id=current_user.id).order_by(Meeting.date).all()
    return render_template('dashboard.html', meetings=meetings, templates=MEETING_TEMPLATES)

@app.route('/meeting/templates')
@login_required
def meeting_templates():
    return render_template('templates.html', templates=MEETING_TEMPLATES)

@app.route('/meeting/create_with_template/<template_type>', methods=['GET', 'POST'])
@login_required
def create_meeting_with_template(template_type):
    if template_type not in MEETING_TEMPLATES:
        flash('Invalid template type')
        return redirect(url_for('meeting_templates'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        duration = request.form.get('duration')
        notes = {}
        
        # Collect notes from each section
        for section in MEETING_TEMPLATES[template_type]['sections']:
            notes[section] = request.form.get(f'section_{section.lower().replace(" ", "_")}')
        
        meeting = Meeting(
            title=title,
            description=description,
            date=datetime.strptime(date_str, '%Y-%m-%dT%H:%M'),
            duration=duration,
            template_type=template_type,
            notes=json.dumps(notes),
            user_id=current_user.id
        )
        
        db.session.add(meeting)
        db.session.commit()
        flash('Meeting created successfully')
        return redirect(url_for('dashboard'))
    
    return render_template(
        'create_meeting_template.html',
        template=MEETING_TEMPLATES[template_type],
        template_type=template_type
    )

@app.route('/create_meeting', methods=['GET', 'POST'])
@login_required
def create_meeting():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        duration = int(request.form.get('duration'))

        date_time_str = f"{date_str} {time_str}"
        meeting_date = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')

        meeting = Meeting(
            title=title,
            description=description,
            date=meeting_date,
            duration=duration,
            user_id=current_user.id
        )
        db.session.add(meeting)
        db.session.commit()
        flash('Meeting created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_meeting.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)
