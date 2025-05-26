# scripts/maintenance/cleanup_codebase.py
"""
Enhanced codebase cleanup script
"""
import os
import glob
import shutil
from datetime import datetime

def cleanup_codebase():
    """Clean up all temporary and test files"""
    print("🧹 Enhanced Codebase Cleanup")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Files and patterns to remove
    cleanup_targets = {
        'backup_files': [
            '*backup*', '*_backup*', '*.bak',
            '*old*', '*_old*', '*.old'
        ],
        'temp_files': [
            '*.tmp', '*.temp', '*~', '*.swp', '*.swo'
        ],
        'python_cache': [
            '__pycache__/', '*.pyc', '*.pyo', '.pytest_cache/'
        ],
        'test_files': [
            'test_*.py', '*_test.py', 'quick_test.py', 'simple_test.py'
        ],
        'log_files': [
            '*.log', 'logs/*.log'
        ],
        'editor_files': [
            '.vscode/settings.json', '.idea/', '*.sublime-*'
        ]
    }
    
    removed_count = 0
    
    for category, patterns in cleanup_targets.items():
        print(f"\n🗂️  Cleaning {category.replace('_', ' ').title()}:")
        
        for pattern in patterns:
            if pattern.endswith('/'):
                # Directory pattern
                for dirpath in glob.glob(pattern, recursive=True):
                    if os.path.exists(dirpath):
                        try:
                            shutil.rmtree(dirpath)
                            print(f"  ✅ Removed directory: {dirpath}")
                            removed_count += 1
                        except Exception as e:
                            print(f"  ❌ Error removing {dirpath}: {e}")
            else:
                # File pattern
                for filepath in glob.glob(pattern, recursive=True):
                    try:
                        os.remove(filepath)
                        print(f"  ✅ Removed file: {filepath}")
                        removed_count += 1
                    except Exception as e:
                        print(f"  ❌ Error removing {filepath}: {e}")
    
    print(f"\n🎯 Cleanup Summary:")
    print(f"   Removed {removed_count} items")
    print(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return removed_count

if __name__ == "__main__":
    cleanup_codebase()
