from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import yadisk
from app import db, File, Category, Purchase, Transaction, yadisk_client
from decimal import Decimal
import uuid
import io

files = Blueprint('files', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            category_id = request.form.get('category_id')
            price = request.form.get('price')
            description = request.form.get('description')
            
            # Generate unique path for Yandex.Disk
            file_uuid = str(uuid.uuid4())
            base_path = f"/files/{current_user.id}/{file_uuid}"
            yadisk_path = f"{base_path}/{filename}"
            
            try:
                # Create directory structure if it doesn't exist
                for path in ["/files", f"/files/{current_user.id}", base_path]:
                    if not yadisk_client.exists(path):
                        try:
                            yadisk_client.mkdir(path)
                            print(f"Created directory: {path}")
                        except Exception as e:
                            print(f"Error creating directory {path}: {str(e)}")
                
                # Upload to Yandex.Disk
                file_data = io.BytesIO()
                file.save(file_data)
                file_data.seek(0)
                yadisk_client.upload(file_data, yadisk_path)
                print(f"File uploaded successfully to: {yadisk_path}")
                
                # Create file record in database
                new_file = File(
                    name=filename,
                    description=description,
                    price=Decimal(price),
                    yadisk_path=yadisk_path,
                    owner_id=current_user.id,
                    category_id=category_id
                )
                
                db.session.add(new_file)
                db.session.commit()
                
                flash('File uploaded successfully')
                return redirect(url_for('files.my_files'))
                
            except Exception as e:
                print(f"Upload error: {str(e)}")  # Debug log
                flash(f'Error uploading file: {str(e)}')
                return redirect(request.url)
                
        flash('File type not allowed')
        return redirect(request.url)
        
    categories = Category.query.all()
    return render_template('files/upload.html', categories=categories)

@files.route('/my-files')
@login_required
def my_files():
    files = File.query.filter_by(owner_id=current_user.id).all()
    return render_template('files/my_files.html', files=files)

@files.route('/browse')
def browse():
    category_id = request.args.get('category_id')
    search_query = request.args.get('q')
    
    query = File.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    if search_query:
        query = query.filter(
            (File.name.ilike(f'%{search_query}%')) |
            (File.description.ilike(f'%{search_query}%'))
        )
        
    files = query.all()
    categories = Category.query.all()
    
    return render_template('files/browse.html', files=files, categories=categories)

@files.route('/purchase/<int:file_id>')
@login_required
def purchase(file_id):
    file = File.query.get_or_404(file_id)
    
    if file.owner_id == current_user.id:
        flash('You cannot purchase your own file')
        return redirect(url_for('files.browse'))
        
    if current_user.balance < file.price:
        flash('Insufficient balance')
        return redirect(url_for('files.browse'))
        
    # Create purchase record
    purchase = Purchase(
        buyer_id=current_user.id,
        file_id=file.id,
        price=file.price
    )
    
    # Create transaction record for buyer
    buyer_transaction = Transaction(
        user_id=current_user.id,
        amount=-file.price,
        transaction_type='purchase',
        status='completed'
    )
    
    # Create transaction record for seller
    seller_transaction = Transaction(
        user_id=file.owner_id,
        amount=file.price,
        transaction_type='sale',
        status='completed'
    )
    
    # Update buyer's balance
    current_user.balance -= file.price
    
    # Update seller's balance
    file.owner.balance += file.price
    
    db.session.add(purchase)
    db.session.add(buyer_transaction)
    db.session.add(seller_transaction)
    db.session.commit()
    
    flash('File purchased successfully')
    return redirect(url_for('files.download', file_id=file.id))

@files.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file or has purchased it
    if not (file.owner_id == current_user.id or 
            Purchase.query.filter_by(buyer_id=current_user.id, file_id=file.id).first()):
        flash('Access denied')
        return redirect(url_for('files.browse'))
    
    try:
        # Download from Yandex.Disk
        file_data = io.BytesIO()
        yadisk_client.download(file.yadisk_path, file_data)
        file_data.seek(0)
        
        return send_file(
            file_data,
            download_name=file.name,
            as_attachment=True
        )
        
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('files.browse')) 