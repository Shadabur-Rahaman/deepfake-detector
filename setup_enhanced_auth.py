#!/usr/bin/env python3
"""
Enhanced Authentication Setup Script for iFake Deepfake Detection Platform
Automates the setup of enterprise-grade authentication and security features.
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create .env file with secure defaults"""
    env_content = f"""# Enhanced Authentication Configuration
SECRET_KEY={generate_secret_key()}
DATABASE_URL=postgresql://ifake_user:secure_password@localhost:5432/ifake_db
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_RESET_EXPIRE_HOURS=1

# Security Features
ENABLE_2FA=true
ENABLE_RATE_LIMITING=true
ENABLE_CSRF_PROTECTION=true
ENABLE_AUDIT_LOGGING=true
ENABLE_SECURITY_MONITORING=true

# Password Policy
MIN_PASSWORD_LENGTH=12
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true
MAX_PASSWORD_AGE_DAYS=90

# Account Lockout Policy
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
LOCKOUT_ESCALATION=true

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_AUTH_ATTEMPTS_PER_15MIN=5

# Session Management
SESSION_TIMEOUT_MINUTES=30
MAX_CONCURRENT_SESSIONS=5
SESSION_EXTEND_ON_ACTIVITY=true

# 2FA Configuration
TOTP_ISSUER=iFake Deepfake Detection
TOTP_WINDOW=1
BACKUP_CODES_COUNT=10

# CSRF Protection
CSRF_TOKEN_EXPIRE_MINUTES=60

# Security Headers
ENABLE_SECURITY_HEADERS=true
ENABLE_CORS=true

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# Development Settings
DEBUG=false
TESTING=false
LOG_LEVEL=INFO

# Frontend Configuration
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure defaults")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing enhanced authentication dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_enhanced_auth.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True

def setup_database():
    """Setup database with authentication tables"""
    print("🗄️ Setting up database...")
    
    try:
        # Import and run database initialization
        sys.path.append('backend/app')
        from auth.database import init_db, create_admin_user
        
        init_db()
        create_admin_user()
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_encryption_key():
    """Create encryption key for sensitive data"""
    print("🔐 Creating encryption key...")
    
    try:
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        
        with open('encryption.key', 'wb') as f:
            f.write(key)
        
        # Set secure permissions
        os.chmod('encryption.key', 0o600)
        print("✅ Encryption key created")
        return True
    except Exception as e:
        print(f"❌ Failed to create encryption key: {e}")
        return False

def setup_redis():
    """Setup Redis for session management and caching"""
    print("🔴 Setting up Redis...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Please ensure Redis is installed and running:")
        print("   - Ubuntu/Debian: sudo apt install redis-server")
        print("   - macOS: brew install redis")
        print("   - Windows: Download from https://redis.io/download")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'backend/app/auth',
        'backend/app/logs',
        'backend/app/uploads',
        'frontend/src/contexts',
        'frontend/src/components/auth',
        'logs',
        'uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def update_frontend_env():
    """Update frontend environment variables"""
    print("🎨 Updating frontend environment...")
    
    frontend_env = """VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=iFake Deepfake Detection
VITE_APP_VERSION=2.0.0
"""
    
    with open('frontend/.env.local', 'w') as f:
        f.write(frontend_env)
    
    print("✅ Frontend environment updated")

def run_security_tests():
    """Run security tests"""
    print("🧪 Running security tests...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pytest", "tests/test_auth.py", "-v"
        ], check=True)
        print("✅ Security tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Security tests failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Enhanced Authentication Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Review and update .env file with your specific configuration")
    print("2. Ensure PostgreSQL and Redis are running")
    print("3. Start the backend server:")
    print("   cd backend && python -m uvicorn app.main_enhanced:app --reload")
    print("4. Start the frontend development server:")
    print("   cd frontend && npm run dev")
    print("5. Access the application at http://localhost:3000")
    print("\n🔐 Default Admin Credentials:")
    print("   Email: admin@ifake.com")
    print("   Password: AdminSecurePass123!")
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("- Change the default admin password immediately")
    print("- Update SECRET_KEY in .env file")
    print("- Configure proper database credentials")
    print("- Set up SSL/TLS certificates for production")
    print("- Enable firewall rules for database and Redis")
    print("\n📚 Documentation:")
    print("- Enhanced Authentication Guide: ENHANCED_AUTHENTICATION_README.md")
    print("- API Documentation: http://localhost:8000/api/docs")
    print("- Security Dashboard: Available after login")
    print("\n🆘 Support:")
    print("- Security Issues: security@ifake.com")
    print("- General Support: support@ifake.com")

def main():
    """Main setup function"""
    print("🚀 iFake Enhanced Authentication Setup")
    print("="*50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Create encryption key
    if not create_encryption_key():
        print("❌ Setup failed at encryption key creation")
        sys.exit(1)
    
    # Setup Redis
    if not setup_redis():
        print("⚠️  Redis setup failed - please install and start Redis")
        print("   Continuing with setup...")
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed at database setup")
        sys.exit(1)
    
    # Update frontend environment
    update_frontend_env()
    
    # Run security tests
    if not run_security_tests():
        print("⚠️  Security tests failed - please check configuration")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
