#!/usr/bin/env python3
"""
Interactive Setup Wizard for Hybrid RAG
Helps you configure API keys step-by-step
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print styled header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(number, title):
    """Print step header"""
    print(f"\n{'='*60}")
    print(f"🔹 Step {number}: {title}")
    print(f"{'='*60}\n")

def get_input(prompt, default="", required=True, masked=False):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not required or user_input:
            return user_input
        print("❌ This field is required. Please try again.")

def validate_gemini_key(key):
    """Validate Gemini API key format"""
    return key.startswith("AIzaSy") and len(key) > 30

def validate_pinecone_key(key):
    """Validate Pinecone API key format"""
    return key.startswith("pcsk_") or key.startswith("pc-")

def main():
    print_header("🧠 Hybrid RAG - Interactive Setup Wizard")
    print("This wizard will help you configure all required API keys.")
    print("Press Ctrl+C at any time to cancel.\n")
    
    input("Press Enter to start the setup... ")
    
    # Dictionary to store all config
    config = {}
    
    # ========================================
    # STEP 1: Google Gemini
    # ========================================
    print_step(1, "Google Gemini API Key")
    print("📍 Visit: https://makersuite.google.com/app/apikey")
    print("   1. Sign in with your Google account")
    print("   2. Click 'Create API Key'")
    print("   3. Copy the key (starts with AIzaSy...)")
    print()
    
    while True:
        gemini_key = get_input("Paste your Gemini API key")
        if validate_gemini_key(gemini_key):
            config['GEMINI_API_KEY'] = gemini_key
            print("✅ Gemini API key validated!")
            break
        else:
            print("❌ Invalid key format. Should start with 'AIzaSy' and be ~39 chars.")
            retry = get_input("Try again? (y/n)", "y", required=False)
            if retry.lower() != 'y':
                break
    
    # ========================================
    # STEP 2: Pinecone
    # ========================================
    print_step(2, "Pinecone Vector Database")
    print("📍 Visit: https://app.pinecone.io/")
    print("   1. Sign up/login")
    print("   2. Create index: name='hybridrag-index', dimensions=768, metric=cosine")
    print("   3. Go to 'API Keys' and copy your key")
    print()
    
    while True:
        pinecone_key = get_input("Paste your Pinecone API key")
        if validate_pinecone_key(pinecone_key):
            config['PINECONE_API_KEY'] = pinecone_key
            print("✅ Pinecone API key validated!")
            break
        else:
            print("❌ Invalid key format. Should start with 'pcsk_' or 'pc-'")
            retry = get_input("Try again? (y/n)", "y", required=False)
            if retry.lower() != 'y':
                break
    
    config['PINECONE_INDEX'] = get_input("Pinecone index name", "hybridrag-index")
    config['PINECONE_CLOUD'] = get_input("Pinecone cloud provider", "gcp-starter")
    config['PINECONE_REGION'] = get_input("Pinecone region", "us-east-1")
    
    # ========================================
    # STEP 3: Supabase/PostgreSQL
    # ========================================
    print_step(3, "Supabase PostgreSQL Database")
    print("📍 Visit: https://supabase.com/dashboard")
    print("   1. Create new project")
    print("   2. Go to Settings > Database")
    print("   3. Find 'Connection Pooler' section")
    print("   4. Copy connection details")
    print()
    
    config['DATABASE_HOST'] = get_input("Database host (e.g., aws-0-us-east-1.pooler.supabase.com)")
    config['DATABASE_PORT'] = get_input("Database port", "6543")
    config['DATABASE_NAME'] = get_input("Database name", "postgres")
    config['DATABASE_USER'] = get_input("Database user (postgres.xxxxx)")
    config['DATABASE_PASSWORD'] = get_input("Database password")
    
    # ========================================
    # STEP 4: Server Configuration
    # ========================================
    print_step(4, "Server Configuration")
    config['PORT'] = get_input("Backend port", "8010")
    config['HOST'] = get_input("Backend host", "0.0.0.0")
    config['DEBUG'] = get_input("Debug mode", "True")
    config['ENDPOINT'] = get_input("Frontend endpoint", f"http://localhost:{config['PORT']}")
    config['LOG_LEVEL'] = get_input("Log level", "INFO")
    
    # ========================================
    # Generate .env file
    # ========================================
    print_step(5, "Generating .env File")
    
    env_content = f"""# =============================================================================
# HYBRID RAG - ENVIRONMENT CONFIGURATION
# Generated by setup_wizard.py
# =============================================================================

# =============================================================================
# GOOGLE GEMINI AI
# =============================================================================
GEMINI_API_KEY={config.get('GEMINI_API_KEY', 'YOUR_KEY_HERE')}

# =============================================================================
# PINECONE VECTOR DATABASE
# =============================================================================
PINECONE_API_KEY={config.get('PINECONE_API_KEY', 'YOUR_KEY_HERE')}
PINECONE_INDEX={config.get('PINECONE_INDEX', 'hybridrag-index')}
PINECONE_CLOUD={config.get('PINECONE_CLOUD', 'gcp-starter')}
PINECONE_REGION={config.get('PINECONE_REGION', 'us-east-1')}

# =============================================================================
# SUPABASE POSTGRESQL DATABASE
# =============================================================================
DATABASE_HOST={config.get('DATABASE_HOST', 'your-host.supabase.com')}
DATABASE_PORT={config.get('DATABASE_PORT', '6543')}
DATABASE_NAME={config.get('DATABASE_NAME', 'postgres')}
DATABASE_USER={config.get('DATABASE_USER', 'postgres.xxxxxxxxxx')}
DATABASE_PASSWORD={config.get('DATABASE_PASSWORD', 'your_password')}

# =============================================================================
# FASTAPI SERVER
# =============================================================================
PORT={config.get('PORT', '8010')}
HOST={config.get('HOST', '0.0.0.0')}
DEBUG={config.get('DEBUG', 'True')}

# =============================================================================
# STREAMLIT FRONTEND
# =============================================================================
ENDPOINT={config.get('ENDPOINT', 'http://localhost:8010')}

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL={config.get('LOG_LEVEL', 'INFO')}
"""
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists!")
        backup = get_input("Create backup? (y/n)", "y")
        if backup.lower() == 'y':
            import shutil
            backup_path = ".env.backup"
            shutil.copy(".env", backup_path)
            print(f"✅ Backup created: {backup_path}")
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    
    # ========================================
    # Verification
    # ========================================
    print_step(6, "Verification")
    print("Testing configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test each key
        tests = {
            "Gemini API Key": os.getenv('GEMINI_API_KEY'),
            "Pinecone API Key": os.getenv('PINECONE_API_KEY'),
            "Database Host": os.getenv('DATABASE_HOST'),
            "Endpoint": os.getenv('ENDPOINT'),
        }
        
        print()
        for name, value in tests.items():
            if value and value not in ['YOUR_KEY_HERE', 'your-host.supabase.com']:
                print(f"✅ {name}: Configured")
            else:
                print(f"❌ {name}: Not configured")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    # ========================================
    # Next Steps
    # ========================================
    print_header("🎉 Setup Complete!")
    print("Next steps:")
    print()
    print("1. Test backend:")
    print("   source venv/bin/activate")
    print("   python app.py")
    print()
    print("2. Test frontend (new terminal):")
    print("   source venv/bin/activate")
    print("   streamlit run src/frontend/streamlit_app.py")
    print()
    print("3. Access the app:")
    print("   Frontend: http://localhost:8501")
    print("   Backend:  http://localhost:8010/health")
    print()
    print("📚 Need help? Check API_SETUP_GUIDE.md for detailed instructions")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


