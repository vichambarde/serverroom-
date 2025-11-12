#!/bin/bash

# Setup script for Local Inventory Management System
# This script installs dependencies and sets up the system on Ubuntu/Debian-based Linux systems

set -e  # Exit on error

echo "=========================================="
echo "Local Inventory Management System Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script should be run as root or with sudo"
    echo "Usage: sudo bash setup.sh"
    exit 1
fi

# Update package list
echo "[1/7] Updating package list..."
apt-get update -qq

# Install Python3 and pip if not already installed
echo "[2/7] Installing Python3 and pip..."
apt-get install -y python3 python3-pip python3-venv

# Install system dependencies
echo "[3/7] Installing system dependencies..."
apt-get install -y libsqlite3-dev

# Create virtual environment
echo "[4/7] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install Python packages
echo "[5/7] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create database directory
echo "[6/7] Creating database directory..."
mkdir -p /var/local/inventory_system
chmod 755 /var/local/inventory_system

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[7/7] Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and configure:"
    echo "   - SMTP email settings (for notifications)"
    echo "   - Admin credentials (username and password)"
    echo "   - Admin email address"
    echo ""
else
    echo "[7/7] .env file already exists, skipping..."
fi

# Set permissions
echo "Setting permissions..."
chmod +x app.py
chmod 600 .env  # Secure the .env file

# Initialize database
echo "Initializing database..."
source venv/bin/activate
python3 << EOF
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
EOF

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "   OR for production with Gunicorn:"
echo "   source venv/bin/activate"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "3. Access the application:"
echo "   http://localhost:5000"
echo ""
echo "Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Remember to change these in the .env file!"
echo "=========================================="
