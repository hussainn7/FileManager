from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from yookassa import Configuration, Payment
import uuid
from decimal import Decimal
from app import db, Transaction, User
import os

payments = Blueprint('payments', __name__)

# Configure YooKassa
Configuration.account_id = os.getenv('YOOKASSA_SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')

@payments.route('/balance')
@login_required
def balance():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template('payments/balance.html', balance=current_user.balance, transactions=transactions)

@payments.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount')
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal < 100:  # Minimum 100 RUB
                flash('Minimum deposit amount is 100 RUB')
                return redirect(url_for('payments.deposit'))
            
            print(f"Processing deposit request for amount: {amount_decimal}")  # Debug log
            
            # Create YooKassa payment
            idempotence_key = str(uuid.uuid4())
            payment_data = {
                "amount": {
                    "value": str(amount_decimal),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": url_for('payments.payment_callback', _external=True)
                },
                "capture": True,
                "description": f"Deposit {amount_decimal} tokens",
                "metadata": {
                    "user_id": current_user.id
                }
            }
            
            print("Creating payment with data:", payment_data)  # Debug log
            
            payment = Payment.create(payment_data, idempotence_key)
            
            print(f"Created payment with ID: {payment.id}, status: {payment.status}")  # Debug log
            
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount_decimal,
                transaction_type='deposit',
                payment_id=payment.id,
                status='pending'
            )
            
            try:
                db.session.add(transaction)
                db.session.commit()
                print(f"Created transaction record: ID={transaction.id}, payment_id={payment.id}")  # Debug log
            except Exception as e:
                print(f"Error creating transaction: {str(e)}")  # Debug log
                db.session.rollback()
                flash('Error creating transaction record')
                return redirect(url_for('payments.deposit'))
            
            confirmation_url = payment.confirmation.confirmation_url
            print(f"Redirecting to payment URL: {confirmation_url}")  # Debug log
            return redirect(confirmation_url)
            
        except (ValueError, TypeError) as e:
            print(f"Error processing deposit: {str(e)}")  # Debug log
            flash('Invalid amount')
            return redirect(url_for('payments.deposit'))
            
    return render_template('payments/deposit.html')

@payments.route('/payment/callback')
@login_required
def payment_callback():
    # Try to get payment_id from different possible sources
    payment_id = request.args.get('payment_id') or request.args.get('orderId')
    
    print("Callback received with args:", request.args)  # Debug log
    
    if not payment_id:
        # If no payment_id in args, try to find the latest pending transaction for the user
        transaction = Transaction.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).order_by(Transaction.created_at.desc()).first()
        
        if transaction:
            payment_id = transaction.payment_id
            print(f"Found pending transaction with payment_id: {payment_id}")  # Debug log
        else:
            flash('Payment identification failed')
            return redirect(url_for('payments.deposit'))
    
    try:
        # Get payment status from YooKassa
        payment = Payment.find_one(payment_id)
        print(f"Payment found with status: {payment.status}")  # Debug log
        
        # Find corresponding transaction
        transaction = Transaction.query.filter_by(payment_id=payment_id).first()
        if not transaction:
            print(f"No transaction found for payment_id: {payment_id}")  # Debug log
            flash('Transaction not found')
            return redirect(url_for('payments.deposit'))
        
        print(f"Found transaction: ID={transaction.id}, Status={transaction.status}")  # Debug log
        
        if payment.status == 'succeeded' or payment.status == 'waiting_for_capture':
            if transaction.status != 'completed':
                # Update transaction status
                transaction.status = 'completed'
                
                # Add tokens to user's balance
                user = User.query.get(transaction.user_id)
                if user:
                    print(f"Updating balance for user {user.id}")  # Debug log
                    print(f"Current balance: {user.balance}")  # Debug log
                    print(f"Adding amount: {transaction.amount}")  # Debug log
                    
                    # Ensure we're working with Decimal objects
                    current_balance = Decimal(str(user.balance)) if user.balance else Decimal('0')
                    amount_to_add = Decimal(str(transaction.amount))
                    
                    user.balance = current_balance + amount_to_add
                    
                    print(f"New balance will be: {user.balance}")  # Debug log
                    
                    try:
                        db.session.commit()
                        print("Database commit successful")  # Debug log
                        flash('Payment successful! Tokens have been added to your balance.')
                    except Exception as commit_error:
                        print(f"Error during commit: {str(commit_error)}")  # Debug log
                        db.session.rollback()
                        flash('Error updating balance')
                else:
                    print(f"User not found for ID: {transaction.user_id}")  # Debug log
                    flash('User not found')
            else:
                print("Transaction was already completed")  # Debug log
                flash('Payment was already processed')
        else:
            print(f"Payment status is not succeeded: {payment.status}")  # Debug log
            transaction.status = 'failed'
            db.session.commit()
            flash('Payment failed or cancelled')
            
    except Exception as e:
        print(f"Payment callback error: {str(e)}")  # Debug log
        flash(f'Error processing payment: {str(e)}')
        
    return redirect(url_for('payments.balance'))

@payments.route('/webhook', methods=['POST'])
def webhook():
    try:
        event_json = request.get_json()
        payment = Payment.find_one(event_json['object']['id'])
        
        if payment.status == 'succeeded':
            transaction = Transaction.query.filter_by(payment_id=payment.id).first()
            if transaction and transaction.status != 'completed':
                transaction.status = 'completed'
                
                # Add tokens to user's balance
                user = User.query.get(transaction.user_id)
                if user:
                    user.balance = user.balance + transaction.amount
                    db.session.commit()
                
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400 