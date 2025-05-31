# backend/app/services/email_service.py
"""
Email service using Gmail SMTP
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Gmail SMTP settings
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")  # Your Gmail address
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")  # App-specific password
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Trading App")
        
        # App settings
        self.app_name = "Trading Intelligence"
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")
        
    def _get_smtp_connection(self):
        """Create SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text version
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_invite_email(self, to_email: str, invite_code: str, invited_by: str) -> bool:
        """Send invitation email"""
        subject = f"You're invited to {self.app_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .code {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; color: #1976d2; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.app_name}</h1>
                    <p>Professional Stock Market Scanner & AI Recommendations</p>
                </div>
                <div class="content">
                    <h2>You're Invited! 🎉</h2>
                    <p>Hi there!</p>
                    <p><strong>{invited_by}</strong> has invited you to join {self.app_name}, an exclusive platform for intelligent stock market analysis.</p>
                    
                    <p>Your invitation code is:</p>
                    <div class="code">{invite_code}</div>
                    
                    <p>Click the button below to create your account:</p>
                    <div style="text-align: center;">
                        <a href="{self.app_url}/register?code={invite_code}" class="button">Create Account</a>
                    </div>
                    
                    <p><strong>What you'll get access to:</strong></p>
                    <ul>
                        <li>🔍 Professional market scanner analyzing 8,000+ stocks</li>
                        <li>🤖 AI-powered trading recommendations</li>
                        <li>📊 Advanced technical indicators and filters</li>
                        <li>📈 Real-time market opportunities</li>
                        <li>💾 Save and share your custom screeners</li>
                    </ul>
                    
                    <p><em>Note: This invitation expires in 7 days and can only be used once.</em></p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                    <p>This is an invite-only platform. Please do not share your invitation code.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        You're Invited to {self.app_name}!
        
        {invited_by} has invited you to join {self.app_name}.
        
        Your invitation code is: {invite_code}
        
        Visit {self.app_url}/register?code={invite_code} to create your account.
        
        This invitation expires in 7 days and can only be used once.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email after registration"""
        subject = f"Welcome to {self.app_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {self.app_name}!</h1>
                </div>
                <div class="content">
                    <h2>Your account is ready! 🚀</h2>
                    <p>Hi {user_name},</p>
                    <p>Welcome to our exclusive trading intelligence platform. Your account has been successfully created.</p>
                    
                    <h3>Getting Started:</h3>
                    <ol>
                        <li><strong>Explore Market Scanner:</strong> Find opportunities across 8,000+ stocks</li>
                        <li><strong>Build Your Watchlist:</strong> Add stocks you want to monitor</li>
                        <li><strong>Get AI Recommendations:</strong> Analyze your watchlist for trading signals</li>
                        <li><strong>Save Screener Presets:</strong> Create custom filters for repeated use</li>
                    </ol>
                    
                    <div style="text-align: center;">
                        <a href="{self.app_url}/dashboard" class="button">Go to Dashboard</a>
                    </div>
                    
                    <p><strong>Pro Tips:</strong></p>
                    <ul>
                        <li>Use "All Stocks" mode with filters to discover hidden gems</li>
                        <li>Lower confidence threshold to 20-30% for more AI signals</li>
                        <li>Check the scanner during market hours for best results</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {self.app_name}!
        
        Hi {user_name},
        
        Your account has been successfully created.
        
        Get started at: {self.app_url}/dashboard
        
        Happy trading!
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = f"Password Reset - {self.app_name}"
        reset_url = f"{self.app_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #dc2626; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi,</p>
                    <p>We received a request to reset your password for {self.app_name}.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This link expires in 1 hour</li>
                        <li>If you didn't request this, please ignore this email</li>
                        <li>Your password won't change until you create a new one</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        We received a request to reset your password for {self.app_name}.
        
        Visit this link to reset your password: {reset_url}
        
        This link expires in 1 hour.
        
        If you didn't request this, please ignore this email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Global email service instance
email_service = EmailService()