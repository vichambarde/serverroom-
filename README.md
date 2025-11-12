# Local Inventory Management System

A fully functional, production-ready inventory management system built with Python Flask, featuring QR code scanning, email notifications, and Excel export capabilities.

## Features

### 🔐 User Authentication
- Two user roles: **Admin** and **User**
- Secure session-based authentication
- Role-based access control

### 👨‍💼 Admin Portal
- Add, edit, and delete inventory items
- Automatic QR code generation for each item
- View all items and transaction history
- Generate and download Excel reports
- Real-time low stock alerts
- Email notifications for all activities

### 👤 User Portal
- Scan QR codes via browser camera
- View item details and availability
- Take items with form submission
- Automatic quantity updates
- Transaction logging with timestamps

### 📧 Email Notifications (SMTP)
- Admin notified when new items are added
- Admin and user notified when items are taken
- Configurable SMTP settings for any email provider

### 📊 Excel Export
- Export complete inventory to Excel
- Export transaction history to Excel
- Uses Pandas and OpenPyXL for data processing

### 📱 QR Code Integration
- Automatic QR code generation for all items
- Browser-based QR scanning (no app required)
- Uses html5-qrcode library

### 💾 Data Storage
- SQLite database for persistent storage
- Configurable database location
- Default location: `/var/local/inventory_system/database.db`

## Technology Stack

- **Backend:** Python Flask 3.0
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** SQLite
- **Email:** Python smtplib
- **QR Codes:** qrcode library + html5-qrcode (JS)
- **Excel:** pandas, openpyxl
- **Environment:** python-dotenv

## Installation

### Prerequisites
- Ubuntu/Debian-based Linux system
- Python 3.8 or higher
- Root or sudo access

### Quick Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd serverroom-
```

2. Run the setup script:
```bash
sudo bash setup.sh
```

3. Edit the `.env` file with your configuration:
```bash
nano .env
```

Configure the following:
- SMTP email settings
- Admin credentials
- Admin email address
- Secret key (auto-generated)

4. Start the application:
```bash
source venv/bin/activate
python3 app.py
```

Or for production:
```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

5. Access the application:
```
http://localhost:5000
```

## Project Structure

```
serverroom-/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── utils.py             # Utility functions (email, QR codes)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── admin.py         # Admin routes
│   │   └── user.py          # User routes
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── index.html       # Landing page
│   │   ├── login.html       # Login page
│   │   ├── admin/           # Admin templates
│   │   └── user/            # User templates
│   └── static/
│       ├── css/             # Custom CSS (if needed)
│       ├── js/              # Custom JavaScript (if needed)
│       └── qr_codes/        # Generated QR codes
├── app.py                   # Main application entry point
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Configuration

### Environment Variables (.env)

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_PATH=/var/local/inventory_system/database.db

# SMTP Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=5000
```

### Gmail SMTP Setup

To use Gmail for email notifications:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Create a new app password
3. Use the app password in the `.env` file

## Usage

### Admin Login

1. Navigate to `http://localhost:5000`
2. Click "Login"
3. Use admin credentials (default: admin / admin123)

### Admin Functions

- **Dashboard:** View statistics and recent activity
- **Add Item:** Create new inventory items with QR codes
- **Edit Item:** Update item details and quantity
- **Delete Item:** Remove items from inventory
- **View Transactions:** See complete transaction history
- **Export Data:** Download Excel files of inventory and transactions

### User Login

Create user accounts through the database or use the admin credentials to access user functions.

### User Functions

- **Scan QR Code:** Use camera to scan item QR codes
- **View Items:** Browse available inventory
- **Take Item:** Submit a form to take items from inventory

## Security Features

- Session-based authentication
- Password hashing (Werkzeug)
- SQL injection prevention (SQLAlchemy ORM)
- CSRF protection (Flask)
- Secure secret key generation
- Environment variable configuration
- Input validation and sanitization

## Troubleshooting

### Database Issues

If you encounter database errors:
```bash
rm -f /var/local/inventory_system/database.db
source venv/bin/activate
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Email Not Sending

- Verify SMTP credentials in `.env`
- Check firewall settings for outbound SMTP
- Ensure Gmail App Password is correct (if using Gmail)
- Check application logs for error messages

### QR Scanner Not Working

- Ensure HTTPS or localhost is being used
- Grant camera permissions in browser
- Check browser compatibility (modern browsers required)

## Production Deployment

### Using Gunicorn

```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
```

### Using Systemd Service

Create `/etc/systemd/system/inventory.service`:

```ini
[Unit]
Description=Inventory Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/serverroom-
Environment="PATH=/path/to/serverroom-/venv/bin"
ExecStart=/path/to/serverroom-/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable inventory
sudo systemctl start inventory
```

### Using Nginx Reverse Proxy

Create `/etc/nginx/sites-available/inventory`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/serverroom-/app/static;
    }
}
```

## License

This project is open source and available for use and modification.

## Support

For issues, questions, or contributions, please contact the system administrator or open an issue in the repository.

## Changelog

### Version 1.0.0 (Initial Release)
- Complete Flask-based inventory system
- QR code generation and scanning
- Email notifications via SMTP
- Excel export functionality
- Admin and user portals
- Session-based authentication
- SQLite database with persistent storage
- Bootstrap-based responsive UI
- Automated setup script