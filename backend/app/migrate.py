# backend/app/migrate.py
"""
Migration script to safely transition to modular structure
"""
import os
import shutil
from datetime import datetime

def backup_current_files():
    """Backup current files before migration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup main.py
    if os.path.exists("main.py"):
        shutil.copy2("main.py", f"{backup_dir}/main.old.py")
        print(f"✅ Backed up main.py to {backup_dir}/main.old.py")
    
    return backup_dir

def verify_imports():
    """Verify all required modules exist"""
    required_files = [
        "core/__init__.py",
        "core/config.py",
        "core/middleware.py",
        "core/exceptions.py",
        "api/health.py",
        "api/market.py",
        "api/watchlist.py",
        "api/recommendations.py"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ Missing files:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

if __name__ == "__main__":
    print("🔄 Migration Check")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: Run this from the app directory")
        exit(1)
    
    # Verify all files exist
    if not verify_imports():
        print("\n⚠️  Create missing files before proceeding")
        exit(1)
    
    # Backup current files
    backup_dir = backup_current_files()
    
    print(f"\n✅ Ready to migrate!")
    print(f"   Backup created in: {backup_dir}")
    print("\n📝 Next steps:")
    print("   1. Replace main.py with the new simplified version")
    print("   2. Restart the backend: docker-compose restart backend")
    print("   3. Test all endpoints")
    print("   4. If issues, restore: cp {}/main.old.py main.py".format(backup_dir))