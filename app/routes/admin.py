"""Admin routes for inventory management."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from app import db
from app.models import Item, Transaction
from app.utils import generate_qr_code, send_email, create_item_added_email
from app.routes.auth import login_required
import pandas as pd
from io import BytesIO
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required(role='admin')
def dashboard():
    """Admin dashboard."""
    items = Item.query.all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(10).all()
    total_items = len(items)
    total_transactions = Transaction.query.count()
    low_stock_items = Item.query.filter(Item.quantity <= 5).all()
    
    return render_template('admin/dashboard.html', 
                         items=items, 
                         transactions=transactions,
                         total_items=total_items,
                         total_transactions=total_transactions,
                         low_stock_items=low_stock_items)

@bp.route('/items')
@login_required(role='admin')
def items():
    """View all items."""
    items = Item.query.all()
    return render_template('admin/items.html', items=items)

@bp.route('/items/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_item():
    """Add a new item."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', 0, type=int)
        
        if not name:
            flash('Item name is required', 'danger')
            return redirect(url_for('admin.add_item'))
        
        # Check if item already exists
        existing_item = Item.query.filter_by(name=name).first()
        if existing_item:
            flash('Item with this name already exists', 'danger')
            return redirect(url_for('admin.add_item'))
        
        # Create new item
        new_item = Item(name=name, description=description, quantity=quantity)
        db.session.add(new_item)
        db.session.commit()
        
        # Generate QR code
        qr_path = generate_qr_code(new_item.id, new_item.name)
        if qr_path:
            new_item.qr_code_path = qr_path
            db.session.commit()
        
        # Send email notification to admin
        admin_email = os.getenv('ADMIN_EMAIL')
        if admin_email:
            email_content = create_item_added_email(name, quantity, description)
            send_email(admin_email, 'New Item Added to Inventory', email_content)
        
        flash(f'Item "{name}" added successfully!', 'success')
        return redirect(url_for('admin.items'))
    
    return render_template('admin/add_item.html')

@bp.route('/items/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_item(item_id):
    """Edit an existing item."""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form.get('name', '').strip()
        item.description = request.form.get('description', '').strip()
        item.quantity = request.form.get('quantity', 0, type=int)
        
        if not item.name:
            flash('Item name is required', 'danger')
            return redirect(url_for('admin.edit_item', item_id=item_id))
        
        # Regenerate QR code if name changed
        if item.qr_code_path:
            old_qr_path = os.path.join('app', item.qr_code_path)
            if os.path.exists(old_qr_path):
                os.remove(old_qr_path)
        
        qr_path = generate_qr_code(item.id, item.name)
        if qr_path:
            item.qr_code_path = qr_path
        
        db.session.commit()
        flash(f'Item "{item.name}" updated successfully!', 'success')
        return redirect(url_for('admin.items'))
    
    return render_template('admin/edit_item.html', item=item)

@bp.route('/items/delete/<int:item_id>', methods=['POST'])
@login_required(role='admin')
def delete_item(item_id):
    """Delete an item."""
    item = Item.query.get_or_404(item_id)
    
    # Delete QR code file
    if item.qr_code_path:
        qr_path = os.path.join('app', item.qr_code_path)
        if os.path.exists(qr_path):
            os.remove(qr_path)
    
    db.session.delete(item)
    db.session.commit()
    
    flash(f'Item "{item.name}" deleted successfully!', 'success')
    return redirect(url_for('admin.items'))

@bp.route('/transactions')
@login_required(role='admin')
def transactions():
    """View all transactions."""
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('admin/transactions.html', transactions=transactions)

@bp.route('/export/items')
@login_required(role='admin')
def export_items():
    """Export items to Excel."""
    items = Item.query.all()
    
    # Create DataFrame
    data = [{
        'ID': item.id,
        'Name': item.name,
        'Description': item.description or '',
        'Quantity': item.quantity,
        'Created At': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
        'Updated At': item.updated_at.strftime('%Y-%m-%d %H:%M:%S') if item.updated_at else ''
    } for item in items]
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Items')
    
    output.seek(0)
    
    filename = f'inventory_items_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=filename)

@bp.route('/export/transactions')
@login_required(role='admin')
def export_transactions():
    """Export transactions to Excel."""
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    
    # Create DataFrame
    data = [{
        'ID': t.id,
        'Item Name': t.item.name if t.item else 'Unknown',
        'User Name': t.user_name,
        'User Email': t.user_email or '',
        'Quantity': t.quantity,
        'Purpose': t.purpose or '',
        'Timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S') if t.timestamp else ''
    } for t in transactions]
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')
    
    output.seek(0)
    
    filename = f'inventory_transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=filename)
