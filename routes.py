from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, Category, File, User
from slugify import slugify

main = Blueprint('main', __name__)

@main.route('/')
def index():
    recent_files = File.query.order_by(File.created_at.desc()).limit(10).all()
    categories = Category.query.all()
    return render_template('index.html', recent_files=recent_files, categories=categories)

@main.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        parent_id = request.form.get('parent_id')
        
        if not name:
            flash('Category name is required')
            return redirect(url_for('main.categories'))
            
        # Create slug from name
        slug = slugify(name)
        
        # Check if slug already exists
        if Category.query.filter_by(slug=slug).first():
            flash('Category with this name already exists')
            return redirect(url_for('main.categories'))
            
        category = Category(
            name=name,
            slug=slug,
            parent_id=parent_id if parent_id else None
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully')
        return redirect(url_for('main.categories'))
        
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@main.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    files = File.query.filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, files=files)

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
        
    total_users = User.query.count()
    total_files = File.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_files = File.query.order_by(File.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_files=total_files,
                         recent_users=recent_users,
                         recent_files=recent_files)

@main.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
        
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@main.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
def admin_update_user_role(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.index'))
        
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role in [UserRole.ADMIN, UserRole.MODERATOR, UserRole.USER]:
        user.role = new_role
        db.session.commit()
        flash('User role updated successfully')
    else:
        flash('Invalid role')
        
    return redirect(url_for('main.admin_users')) 