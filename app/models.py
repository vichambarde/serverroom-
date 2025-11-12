"""Database models for the inventory management system."""
from datetime import datetime
from app import db

class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Item(db.Model):
    """Inventory item model."""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    qr_code_path = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with transactions
    transactions = db.relationship('Transaction', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'qr_code_path': self.qr_code_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Transaction(db.Model):
    """Transaction log for item movements."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.user_name} took {self.quantity} of item {self.item_id}>'
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item.name if self.item else 'Unknown',
            'user_name': self.user_name,
            'user_email': self.user_email,
            'quantity': self.quantity,
            'purpose': self.purpose,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
