#!/usr/bin/env python3
"""
Production Authentication Setup Script
Comprehensive setup script for production-ready authentication system.
"""

import os
import sys
import subprocess
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description=""):
    """Run a command and return success status"""
    try:
        logger.info(f"Running: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ Success: {description or command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description or command}")
        logger.error(f"Error: {e.stderr}")
        return False, e.stderr

def install_dependencies():
    """Install all required dependencies"""
    logger.info("📦 Installing dependencies...")
    
    dependencies = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.1",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "redis>=5.0.0",
        "aioredis>=2.0.0",
        "PyJWT>=2.8.0",
        "passlib[bcrypt]>=1.7.4",
        "python-jose[cryptography]>=3.3.0",
        "cryptography>=41.0.0",
        "bcrypt>=4.0.0",
        "argon2-cffi>=25.0.0",
        "pydantic[email]>=2.0.0",
        "pydantic-settings>=2.0.0",
        "email-validator>=2.0.0"
    ]
    
    for dep in dependencies:
        success, output = run_command(f"pip install {dep}", f"Install {dep}")
        if not success:
            logger.warning(f"Failed to install {dep}, continuing...")
    
    logger.info("✅ Dependencies installation completed")

def create_env_file():
    """Create environment configuration file"""
    logger.info("🔧 Creating environment configuration...")
    
    env_content = """# Production Environment Configuration
# Copy this file to .env and update the values

# Database Configuration
DATABASE_URL=sqlite:///./ifake_auth.db
# For PostgreSQL: postgresql://user:password@localhost:5432/ifake_auth
# For MySQL: mysql://user:password@localhost:3306/ifake_auth

# Fallback Database (optional)
FALLBACK_DATABASE_URL=postgresql://postgres:password@localhost:5432/ifake_auth

# Redis Configuration
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Configuration
BCRYPT_ROUNDS=12
ARGON2_MEMORY_COST=65536
ARGON2_TIME_COST=3
ARGON2_PARALLELISM=4

# Rate Limiting
RATE_LIMIT_LOGIN=5
RATE_LIMIT_REGISTER=3
RATE_LIMIT_PASSWORD_RESET=3

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://ifake.com
CORS_ALLOW_CREDENTIALS=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Security Headers
SECURE_HEADERS=true
TRUSTED_HOSTS=localhost,127.0.0.1,*.ifake.com
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    logger.info("✅ Environment configuration created: .env.example")

async def test_authentication_system():
    """Test the authentication system"""
    logger.info("🧪 Testing authentication system...")
    
    try:
        from fastapi import FastAPI
        from backend.app.auth.integration import initialize_authentication
        
        app = FastAPI()
        await initialize_authentication(app, "sqlite:///./test_auth.db")
        
        if hasattr(app.state, 'auth_core') and app.state.auth_core:
            logger.info("✅ Authentication system test passed")
            return True
        else:
            logger.error("❌ Authentication system test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Authentication system test failed: {str(e)}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Starting production authentication setup...")
    
    try:
        # Install dependencies
        install_dependencies()
        
        # Create configuration files
        create_env_file()
        
        # Test authentication system
        test_passed = await test_authentication_system()
        
        if test_passed:
            logger.info("✅ Production authentication setup completed successfully!")
            logger.info("🔧 Edit .env.example and rename to .env for configuration")
            logger.info("🚀 Run: python backend/app/main_production.py")
        else:
            logger.error("❌ Setup completed but authentication system test failed")
            logger.error("Please check the logs and fix any issues")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())