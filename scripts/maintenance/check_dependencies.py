# scripts/maintenance/check_dependencies.py
"""
Check for outdated dependencies and security issues
"""
import subprocess
import sys

def check_python_dependencies():
    """Check Python package dependencies"""
    print("🐍 Checking Python Dependencies")
    print("=" * 35)
    
    try:
        # Check for outdated packages
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("📦 Outdated Python packages:")
            print(result.stdout)
        else:
            print("✅ All Python packages are up to date")
            
    except Exception as e:
        print(f"❌ Error checking Python dependencies: {e}")

def check_node_dependencies():
    """Check Node.js dependencies"""
    print("\n📦 Checking Node.js Dependencies")
    print("=" * 35)
    
    if os.path.exists('frontend/package.json'):
        try:
            result = subprocess.run(['npm', 'outdated'], 
                                  cwd='frontend', capture_output=True, text=True)
            
            if result.stdout.strip():
                print("📦 Outdated Node packages:")
                print(result.stdout)
            else:
                print("✅ All Node packages are up to date")
                
        except Exception as e:
            print(f"❌ Error checking Node dependencies: {e}")
    else:
        print("⚠️ frontend/package.json not found")

def security_audit():
    """Run security audit"""
    print("\n🔒 Security Audit")
    print("=" * 20)
    
    # Python security check (if safety is installed)
    try:
        subprocess.run(['safety', 'check'], check=True)
        print("✅ Python packages security check passed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Safety not installed or security issues found")
        print("   Install with: pip install safety")
    
    # Node security check
    if os.path.exists('frontend/package.json'):
        try:
            subprocess.run(['npm', 'audit'], cwd='frontend', check=True)
            print("✅ Node packages security check passed")
        except subprocess.CalledProcessError:
            print("⚠️ Node security issues found - run 'npm audit fix'")

if __name__ == "__main__":
    check_python_dependencies()
    check_node_dependencies()
    security_audit()
    