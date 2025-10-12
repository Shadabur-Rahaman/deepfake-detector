#!/usr/bin/env python3
"""
Update Backend IP Address
========================
This script helps you update the frontend configuration to connect to your Linux backend.
"""

import os
import re
import socket

def find_local_ip():
    """Find the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def update_api_config(backend_ip):
    """Update the API configuration file"""
    config_file = "frontend/src/config/api.ts"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        # Read the current configuration
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update the REMOTE URL
        new_remote_url = f"http://{backend_ip}:8000/api"
        content = re.sub(
            r"REMOTE: 'http://YOUR_BACKEND_IP:8000/api'",
            f"REMOTE: '{new_remote_url}'",
            content
        )
        
        # Write the updated configuration
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated API configuration to use: {new_remote_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def main():
    print("🔧 Backend IP Configuration Tool")
    print("=" * 50)
    
    # Find local IP
    local_ip = find_local_ip()
    print(f"📍 Your machine's IP address: {local_ip}")
    
    print("\n📋 Instructions:")
    print("1. On your Linux machine (where backend is running), run:")
    print("   ip addr show")
    print("   # or")
    print("   hostname -I")
    print("\n2. Find the IP address that starts with 192.168.x.x or 10.x.x.x")
    print("3. Enter that IP address below")
    
    # Get backend IP from user
    backend_ip = input(f"\n🌐 Enter your Linux backend IP address: ").strip()
    
    if not backend_ip:
        print("❌ No IP address provided")
        return
    
    # Validate IP format
    try:
        socket.inet_aton(backend_ip)
    except socket.error:
        print("❌ Invalid IP address format")
        return
    
    # Update configuration
    if update_api_config(backend_ip):
        print(f"\n🎉 Configuration updated successfully!")
        print(f"Frontend will now connect to: http://{backend_ip}:8000/api")
        print("\n📝 Next steps:")
        print("1. Restart your frontend development server")
        print("2. Try signing in again")
        print("3. Check browser console for connection logs")
    else:
        print("\n❌ Failed to update configuration")

if __name__ == "__main__":
    main()
