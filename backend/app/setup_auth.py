# backend/app/setup_auth.py
"""
Setup script for authentication system
Run this after applying database migrations
"""
import os
import sys
import getpass
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, '/app/app')

from sqlalchemy.orm import Session
from models.database import SessionLocal, create_tables
from models.auth import User, Invite, UserTier
from core.security import get_password_hash, generate_invite_code, validate_password

def create_admin_user(db: Session):
    """Create the initial admin user"""
    print("\n=== Creating Admin User ===")
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.is_admin == True).first()
    if existing_admin:
        print(f"Admin user already exists: {existing_admin.email}")
        return existing_admin
    
    # Get admin email
    while True:
        email = input("Enter admin email: ").strip().lower()
        if '@' in email and '.' in email:
            # Check if email already exists
            if db.query(User).filter(User.email == email).first():
                print("This email is already registered!")
                continue
            break
        print("Invalid email format!")
    
    # Get admin password
    while True:
        password = getpass.getpass("Enter admin password (min 8 chars, 1 number, 1 special char): ")
        is_valid, error_msg = validate_password(password)
        if is_valid:
            password_confirm = getpass.getpass("Confirm password: ")
            if password == password_confirm:
                break
            else:
                print("Passwords don't match!")
        else:
            print(f"Invalid password: {error_msg}")
    
    # Create admin user
    admin_user = User(
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
        is_admin=True,
        email_verified=True,
        email_verified_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.flush()
    
    # Create admin tier
    admin_tier = UserTier(
        user_id=admin_user.id,
        tier="enterprise",
        features={
            "scans_per_day": "unlimited",
            "screener_filters": "unlimited",
            "watchlist_size": 1000,
            "saved_presets": "unlimited",
            "api_calls_per_hour": "unlimited",
            "export_csv": True,
            "real_time_updates": True,
            "advanced_indicators": True,
            "pattern_recognition": True,
            "backtesting": True,
            "admin_panel": True
        }
    )
    db.add(admin_tier)
    
    db.commit()
    print(f"✅ Admin user created: {email}")
    return admin_user

def create_initial_invites(db: Session, admin_user: User, count: int = 5):
    """Create initial invite codes"""
    print(f"\n=== Creating {count} Initial Invite Codes ===")
    
    invites = []
    for i in range(count):
        code = generate_invite_code()
        while db.query(Invite).filter(Invite.code == code).first():
            code = generate_invite_code()
        
        invite = Invite(
            code=code,
            created_by=admin_user.id,
            expires_at=datetime.utcnow() + timedelta(days=30),  # 30 days validity
            notes=f"Initial invite #{i+1}"
        )
        db.add(invite)
        invites.append(code)
    
    db.commit()
    
    print("\n📨 Invite Codes (valid for 30 days):")
    print("-" * 40)
    for code in invites:
        print(f"  {code}")
    print("-" * 40)
    print("\nShare these codes with users you want to invite.")
    print("You can create more invites from the admin panel.")

def setup_email_config():
    """Help user set up email configuration"""
    print("\n=== Email Configuration ===")
    print("To send invitation emails, you need to set up Gmail SMTP.")
    print("\nAdd these to your .env file:")
    print("-" * 40)
    print("# Email Configuration (Gmail SMTP)")
    print("SMTP_HOST=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USER=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-specific-password")
    print("FROM_EMAIL=your-email@gmail.com")
    print("FROM_NAME=Trading Intelligence")
    print("APP_URL=http://localhost:3000")
    print("-" * 40)
    print("\nTo get an app-specific password:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-factor authentication")
    print("3. Go to 'App passwords'")
    print("4. Generate a password for 'Mail'")
    print("5. Use that password as SMTP_PASSWORD")

def main():
    """Main setup function"""
    print("🔐 Authentication System Setup")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create admin user
        admin_user = create_admin_user(db)
        
        # Create initial invites
        create_initial_invites(db, admin_user)
        
        # Show email setup instructions
        setup_email_config()
        
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Update your .env file with email settings")
        print("2. Update backend/app/core/security.py SECRET_KEY")
        print("3. Restart the backend: docker-compose restart backend")
        print("4. Share invite codes with users")
        print(f"5. Login as admin: {admin_user.email}")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()