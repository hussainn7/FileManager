from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import yadisk
from decimal import Decimal
from sqlalchemy import DECIMAL
from flask.cli import with_appcontext
import click
from slugify import slugify

# Load environment variables
load_dotenv()

app = Flask(__name__, 
    static_folder='public_html/static',
    static_url_path='/static')

# Production configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APPLICATION_ROOT'] = '/'  # Set this to your subdirectory if needed

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
# mail = Mail(app)  # Temporarily disabled
admin = Admin(app, name='File Exchange CMS', template_mode='bootstrap3')

# Initialize Yandex.Disk client
yadisk_client = yadisk.YaDisk(token=os.getenv('YADISK_TOKEN'))

# Ensure the base directory exists
with app.app_context():
    try:
        if not yadisk_client.exists('/files'):
            yadisk_client.mkdir('/files')
            print("Created base directory on Yandex.Disk")
    except Exception as e:
        print(f"Error checking/creating base directory: {str(e)}")

# User roles
class UserRole:
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=UserRole.USER)
    balance = db.Column(DECIMAL(10, 2), default=0)
    is_verified = db.Column(db.Boolean, default=True)  # Temporarily set to True by default
    verification_token = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    files = db.relationship('File', backref='owner', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    files = db.relationship('File', backref='category', lazy=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(DECIMAL(10, 2), nullable=False)
    yadisk_path = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    purchases = db.relationship('Purchase', backref='file', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(DECIMAL(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, purchase
    payment_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    price = db.Column(DECIMAL(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create admin views
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Category, db.session))
admin.add_view(AdminModelView(File, db.session))
admin.add_view(AdminModelView(Transaction, db.session))
admin.add_view(AdminModelView(Purchase, db.session))

# Register blueprints
from auth import auth, init_auth
from files import files
from payments import payments
from routes import main

# Initialize auth with required models
init_auth(db, User)

app.register_blueprint(auth)
app.register_blueprint(files)
app.register_blueprint(payments)
app.register_blueprint(main)

@click.command('create-categories')
@with_appcontext
def create_categories_command():
    """Create initial categories."""
    categories = [
        {
            'name': 'Documents',
            'subcategories': [
                'Business Documents',
                'Legal Documents',
                'Academic Papers',
                'Templates'
            ]
        },
        {
            'name': 'Software',
            'subcategories': [
                'Scripts',
                'Applications',
                'Source Code',
                'Plugins'
            ]
        },
        {
            'name': 'Media',
            'subcategories': [
                'Images',
                'Audio',
                'Video',
                'Graphics'
            ]
        },
        {
            'name': 'Educational',
            'subcategories': [
                'Courses',
                'Tutorials',
                'Study Materials',
                'Research Papers'
            ]
        }
    ]
    
    for category_data in categories:
        # Create main category
        main_category = Category.query.filter_by(name=category_data['name']).first()
        if not main_category:
            main_category = Category(
                name=category_data['name'],
                slug=slugify(category_data['name'])
            )
            db.session.add(main_category)
            db.session.commit()
            print(f"Created main category: {main_category.name}")
            
            # Create subcategories
            for sub_name in category_data['subcategories']:
                sub_category = Category.query.filter_by(name=sub_name).first()
                if not sub_category:
                    sub_category = Category(
                        name=sub_name,
                        slug=slugify(sub_name),
                        parent_id=main_category.id
                    )
                    db.session.add(sub_category)
            db.session.commit()
            print(f"Created subcategories for {main_category.name}")
    
    print("Categories created successfully")

app.cli.add_command(create_categories_command)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@example.com',
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role=UserRole.ADMIN,
                is_verified=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully")
            
    app.run(debug=True) 