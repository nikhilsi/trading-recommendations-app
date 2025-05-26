# backend/app/cleanup_codebase.py
"""
Script to clean up temporary, test, and backup files from the codebase
"""
import os
import glob

def remove_file_if_exists(filepath):
    """Remove file if it exists and print result"""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"✅ Removed: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error removing {filepath}: {e}")
            return False
    else:
        print(f"⚪ Not found: {filepath}")
        return False

def cleanup_codebase():
    """Clean up all temporary and test files"""
    print("🧹 Starting codebase cleanup...")
    print("=" * 50)
    
    # Files to remove
    files_to_remove = [
        # Backup and temporary main files
        '/app/app/main_simple.py',
        '/app/app/main_simple_backup.py', 
        '/app/app/main_complex.py',
        
        # Test files
        '/app/app/test_api.py',
        '/app/simple_test.py',
        '/app/working_test.py',
        '/app/quick_test.py',
        '/app/test_recommendations.py',
        
        # Setup and utility scripts
        '/app/app/create_missing_files.py',
        #'/app/app/cleanup_codebase.py',  # This script itself
        
        # Old service files (if they exist)
        '/app/app/services/recommendation_engine.py',
        
        # Any .pyc files
        '/app/app/__pycache__',
        '/app/app/api/__pycache__',
        '/app/app/models/__pycache__',
        '/app/app/schemas/__pycache__',
        '/app/app/services/__pycache__',
    ]
    
    removed_count = 0
    
    for filepath in files_to_remove:
        if filepath.endswith('__pycache__'):
            # Handle pycache directories
            if os.path.exists(filepath):
                try:
                    import shutil
                    shutil.rmtree(filepath)
                    print(f"✅ Removed directory: {filepath}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing directory {filepath}: {e}")
        else:
            # Handle regular files
            if remove_file_if_exists(filepath):
                removed_count += 1
    
    # Find and remove any other backup files
    backup_patterns = [
        '/app/app/*backup*',
        '/app/app/*temp*',
        '/app/app/*old*',
        '/app/*simple*',
        '/app/*test*.py'
    ]
    
    for pattern in backup_patterns:
        matching_files = glob.glob(pattern)
        for filepath in matching_files:
            if os.path.basename(filepath) not in ['test_recommendations.py']:  # Keep if needed
                if remove_file_if_exists(filepath):
                    removed_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Cleanup complete! Removed {removed_count} files")
    
    # Show final clean structure
    print("\n📁 Final clean structure:")
    print("backend/app/")
    
    for root, dirs, files in os.walk('/app/app'):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        level = root.replace('/app/app', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files):
            if file.endswith('.py') and not file.endswith('.pyc'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    cleanup_codebase()