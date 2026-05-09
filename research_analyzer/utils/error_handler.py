import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def send_error_email(error_msg):
    """Send error notification email"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = os.getenv('ADMIN_EMAIL')
        
        if not all([sender_email, sender_password, recipient_email]):
            logger.error("Email configuration missing")
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Medical Research Analyzer Error - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        An error occurred in the Medical Research Analyzer:
        
        {error_msg}
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logger.info("Error notification email sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send error notification email: {str(e)}")

def handle_error(error_msg):
    """Central error handling function"""
    logger.error(error_msg)
    
    # Log to file
    with open('error_log.txt', 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {error_msg}\n")
    
    # Send email notification
    send_error_email(error_msg)
