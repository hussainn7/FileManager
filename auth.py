from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_mail import Message  # Temporarily disabled
import uuid
from functools import wraps

auth = Blueprint('auth', __name__)

def init_auth(database, User_model):
    global db, User
    db = database
    User = User_model

# Temporarily disabled
# def send_verification_email(user):
#     token = str(uuid.uuid4())
#     user.verification_token = token
#     db.session.commit()
    
#     msg = Message('Verify your email',
#                   sender='noreply@yourdomain.com',
#                   recipients=[user.email])
    
#     verification_url = url_for('auth.verify_email', token=token, _external=True)
#     msg.body = f'Please click the following link to verify your email: {verification_url}'
#     mail.send(msg)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter((User.email == email) | (User.username == username)).first()
        if user:
            flash('Email or username already exists')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            is_verified=True  # Temporarily set to True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Temporarily disabled
        # send_verification_email(new_user)
        # flash('Registration successful. Please check your email to verify your account.')
        flash('Registration successful. You can now log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

# Temporarily disabled
# @auth.route('/verify-email/<token>')
# def verify_email(token):
#     user = User.query.filter_by(verification_token=token).first()
#     if user:
#         user.is_verified = True
#         user.verification_token = None
#         db.session.commit()
#         flash('Email verified successfully. You can now log in.')
#     else:
#         flash('Invalid verification token.')
#     return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Temporarily disabled email verification check
            # if not user.is_verified:
            #     flash('Please verify your email before logging in.')
            #     return redirect(url_for('auth.login'))
                
            login_user(user)
            return redirect(url_for('main.index'))
            
        flash('Invalid username or password')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    # Temporarily disabled
    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     user = User.query.filter_by(email=email).first()
        
    #     if user:
    #         token = str(uuid.uuid4())
    #         user.reset_token = token
    #         db.session.commit()
            
    #         msg = Message('Reset Your Password',
    #                       sender='noreply@yourdomain.com',
    #                       recipients=[user.email])
                          
    #         reset_url = url_for('auth.reset_password', token=token, _external=True)
    #         msg.body = f'To reset your password, visit the following link: {reset_url}'
    #         mail.send(msg)
            
    #         flash('Check your email for the instructions to reset your password')
    #         return redirect(url_for('auth.login'))
            
    #     flash('Email address not found')
    flash('Password reset functionality is temporarily disabled')
    return redirect(url_for('auth.login'))
    # return render_template('auth/reset_password_request.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Temporarily disabled
    # user = User.query.filter_by(reset_token=token).first()
    # if not user:
    #     flash('Invalid or expired reset token')
    #     return redirect(url_for('auth.login'))
        
    # if request.method == 'POST':
    #     password = request.form.get('password')
    #     user.password_hash = generate_password_hash(password)
    #     user.reset_token = None
    #     db.session.commit()
        
    #     flash('Your password has been reset.')
    #     return redirect(url_for('auth.login'))
        
    # return render_template('auth/reset_password.html')
    flash('Password reset functionality is temporarily disabled')
    return redirect(url_for('auth.login')) 