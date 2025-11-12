"""User routes for taking items."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Item, Transaction
from app.utils import send_email, create_item_taken_email
from app.routes.auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/dashboard')
@login_required(role='user')
def dashboard():
    """User dashboard."""
    items = Item.query.filter(Item.quantity > 0).all()
    return render_template('user/dashboard.html', items=items)

@bp.route('/scan')
@login_required(role='user')
def scan():
    """QR code scanner page."""
    return render_template('user/scan.html')

@bp.route('/item/<int:item_id>')
@login_required(role='user')
def view_item(item_id):
    """View item details."""
    item = Item.query.get_or_404(item_id)
    return render_template('user/view_item.html', item=item)

@bp.route('/take/<int:item_id>', methods=['GET', 'POST'])
@login_required(role='user')
def take_item(item_id):
    """Take an item from inventory."""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        user_email = request.form.get('user_email', '').strip()
        quantity = request.form.get('quantity', 0, type=int)
        purpose = request.form.get('purpose', '').strip()
        
        # Validation
        if not user_name:
            flash('Your name is required', 'danger')
            return redirect(url_for('user.take_item', item_id=item_id))
        
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('user.take_item', item_id=item_id))
        
        if quantity > item.quantity:
            flash(f'Not enough items in stock. Available: {item.quantity}', 'danger')
            return redirect(url_for('user.take_item', item_id=item_id))
        
        # Create transaction
        transaction = Transaction(
            item_id=item.id,
            user_name=user_name,
            user_email=user_email if user_email else None,
            quantity=quantity,
            purpose=purpose if purpose else None
        )
        db.session.add(transaction)
        
        # Update item quantity
        item.quantity -= quantity
        db.session.commit()
        
        # Send email notifications
        admin_email = os.getenv('ADMIN_EMAIL')
        email_content = create_item_taken_email(user_name, user_email, item.name, quantity, purpose)
        
        # Send to admin
        if admin_email:
            send_email(admin_email, f'Item Taken: {item.name}', email_content)
        
        # Send to user if email provided
        if user_email:
            send_email(user_email, f'Confirmation: You took {item.name}', email_content)
        
        flash(f'Successfully took {quantity} of "{item.name}"!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/take_item.html', item=item)

@bp.route('/api/item/<int:item_id>')
@login_required(role='user')
def api_get_item(item_id):
    """API endpoint to get item details (for QR scanner)."""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())
