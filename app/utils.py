"""Utility functions for email notifications and QR code generation."""
import os
import smtplib
import qrcode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, html_content):
    """
    Send an email using SMTP.
    
    Args:
        to_email: Recipient email address (can be a list)
        subject: Email subject
        html_content: HTML content of the email
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured. Email not sent.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_username
        msg['To'] = to_email if isinstance(to_email, str) else ', '.join(to_email)
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def generate_qr_code(item_id, item_name):
    """
    Generate a QR code for an inventory item.
    
    Args:
        item_id: The item's database ID
        item_name: The item's name
    
    Returns:
        str: The relative path to the saved QR code image
    """
    try:
        # Create QR code with item details
        qr_data = f"ITEM_ID:{item_id}|NAME:{item_name}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to static folder
        # Sanitize item_name to prevent path traversal attacks
        safe_item_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in item_name)
        safe_item_name = safe_item_name.replace(' ', '_')
        qr_filename = f"item_{item_id}_{safe_item_name}.png"
        
        # Use hardcoded directory path to prevent path traversal
        qr_dir = os.path.join('app', 'static', 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        qr_path = os.path.join(qr_dir, qr_filename)
        
        img.save(qr_path)
        
        # Return relative path for web access
        return f"static/qr_codes/{qr_filename}"
    
    except Exception as e:
        print(f"Failed to generate QR code: {str(e)}")
        return None

def create_item_added_email(item_name, quantity, description):
    """Create HTML email content for when an admin adds an item."""
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">New Item Added to Inventory</h2>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Item Name:</strong> {item_name}</p>
                <p><strong>Quantity:</strong> {quantity}</p>
                <p><strong>Description:</strong> {description or 'N/A'}</p>
            </div>
            <p style="margin-top: 20px; color: #7f8c8d;">
                This is an automated notification from the Inventory Management System.
            </p>
        </body>
    </html>
    """

def create_item_taken_email(user_name, user_email, item_name, quantity, purpose):
    """Create HTML email content for when a user takes an item."""
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #e74c3c;">Item Taken from Inventory</h2>
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px;">
                <p><strong>User Name:</strong> {user_name}</p>
                <p><strong>User Email:</strong> {user_email or 'N/A'}</p>
                <p><strong>Item Taken:</strong> {item_name}</p>
                <p><strong>Quantity:</strong> {quantity}</p>
                <p><strong>Purpose:</strong> {purpose or 'N/A'}</p>
            </div>
            <p style="margin-top: 20px; color: #7f8c8d;">
                This is an automated notification from the Inventory Management System.
            </p>
        </body>
    </html>
    """
