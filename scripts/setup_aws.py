"""
Quick AWS Credentials Setup for Windows
Run this script to set up AWS credentials via environment variables
"""

import os

def setup_aws_credentials():
    print("🔧 AWS Credentials Setup for Lipsync Video Generator")
    print("=" * 50)
    
    print("\nTo use AWS services, you need:")
    print("1. AWS Access Key ID")
    print("2. AWS Secret Access Key")
    print("3. AWS Region (recommended: us-east-1)")
    
    print("\n📋 Get your credentials from:")
    print("   - AWS Console → IAM → Users → [Your User] → Security Credentials")
    print("   - Or create new access keys if needed")
    
    # Get credentials from user
    access_key = input("\n🔑 Enter AWS Access Key ID: ").strip()
    secret_key = input("🗝️  Enter AWS Secret Access Key: ").strip()
    region = input("🌍 Enter AWS Region (default: us-east-1): ").strip() or "us-east-1"
    
    if not access_key or not secret_key:
        print("❌ Access Key ID and Secret Access Key are required!")
        return False
    
    # Set environment variables for current session
    os.environ['AWS_ACCESS_KEY_ID'] = access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
    os.environ['AWS_DEFAULT_REGION'] = region
    
    print(f"\n✅ AWS credentials set for current session!")
    print(f"   Region: {region}")
    print(f"   Access Key: {access_key[:8]}...")
    
    # Create batch file for future sessions
    batch_content = f"""@echo off
echo Setting AWS credentials...
set AWS_ACCESS_KEY_ID={access_key}
set AWS_SECRET_ACCESS_KEY={secret_key}
set AWS_DEFAULT_REGION={region}
echo AWS credentials set!
echo.
echo Starting Flask app...
python app.py
"""
    
    with open('run_with_aws.bat', 'w') as f:
        f.write(batch_content)
    
    print(f"\n📁 Created 'run_with_aws.bat' for future runs")
    print(f"   Just double-click this file to start the app with AWS credentials")
    
    return True

if __name__ == "__main__":
    setup_aws_credentials()