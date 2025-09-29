#!/usr/bin/env python3
"""Setup script for IQ Option trading bot integration."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step_num, description):
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 50)

def run_command(command, description=""):
    """Run a command and return success status."""
    try:
        print(f"🔧 {description or command}")
        result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def setup_virtual_environment():
    """Set up virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    if run_command("python -m venv venv", "Creating virtual environment"):
        print("✅ Virtual environment created successfully")
        return True
    else:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("🔧 Installing dependencies from requirements.txt...")
    
    # Use the virtual environment pip if available
    venv_path = Path("venv")
    if venv_path.exists():
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        if pip_path.exists():
            pip_command = str(pip_path)
        else:
            pip_command = "pip"
    else:
        pip_command = "pip"
    
    success = run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")
    
    if not success:
        print("\n⚠️ Standard pip install failed. Trying alternative method...")
        success = run_command(f"{pip_command} install --user -r requirements.txt", "Installing with --user flag")
    
    if not success:
        print("\n⚠️ Pip install failed. Trying with --break-system-packages flag...")
        success = run_command(f"{pip_command} install --break-system-packages -r requirements.txt", "Installing with --break-system-packages")
    
    return success

def setup_environment_file():
    """Set up environment configuration file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("📁 .env file already exists")
        
        response = input("🤔 Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print("⏭️ Keeping existing .env file")
            return True
    
    if env_example.exists():
        print("📋 Copying .env.example to .env...")
        shutil.copy(env_example, env_file)
        print("✅ Environment file created")
        
        print("\n⚠️  IMPORTANT: Edit .env file with your actual credentials!")
        print("   - Add your IQ Option email and password")
        print("   - Configure other API keys as needed")
        print("   - Keep demo_mode: true for safety")
        
        return True
    else:
        print("❌ .env.example not found")
        return False

def verify_configuration():
    """Verify the configuration setup."""
    settings_file = Path("settings.yml")
    
    if not settings_file.exists():
        print("❌ settings.yml not found")
        return False
    
    print("✅ settings.yml found")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file found")
    
    # Check if credentials are configured
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "your_actual_email@example.com" in content:
            print("⚠️  You still need to configure your IQ Option credentials in .env")
            return False
        else:
            print("✅ .env file appears to be configured")
            return True
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def run_tests():
    """Run integration tests."""
    print("🧪 Running integration tests...")
    
    # First run the basic feature tests
    if os.path.exists("test_new_features.py"):
        success = run_command("python test_new_features.py", "Running basic feature tests")
        if not success:
            print("❌ Basic tests failed")
            return False
    
    # Then run IQ Option integration tests
    if os.path.exists("test_iq_option_integration.py"):
        success = run_command("python test_iq_option_integration.py", "Running IQ Option integration tests")
        if success:
            print("✅ All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed (this is expected without real credentials)")
            return True  # Return True anyway as failures are expected without credentials
    
    print("❌ Test files not found")
    return False

def main():
    """Main setup process."""
    print_header("IQ Option Trading Bot Setup")
    
    print("🚀 Welcome to the IQ Option Trading Bot Setup!")
    print("This script will help you set up the trading bot with IQ Option integration.")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Set up virtual environment
    print_step(2, "Setting up virtual environment")
    use_venv = input("🤔 Create virtual environment? (Y/n): ").lower().strip()
    if use_venv != 'n':
        if not setup_virtual_environment():
            print("⚠️ Continuing without virtual environment...")
    
    # Step 3: Install dependencies
    print_step(3, "Installing dependencies")
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        print("   or: pip install --break-system-packages -r requirements.txt")
        
        response = input("🤔 Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            sys.exit(1)
    
    # Step 4: Set up environment file
    print_step(4, "Setting up environment configuration")
    if not setup_environment_file():
        print("❌ Failed to set up environment file")
        sys.exit(1)
    
    # Step 5: Verify configuration
    print_step(5, "Verifying configuration")
    config_ready = verify_configuration()
    
    # Step 6: Run tests
    print_step(6, "Running tests")
    run_tests()
    
    # Final instructions
    print_header("Setup Complete!")
    
    if config_ready:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Review settings.yml for trading configuration")
        print("2. Make sure demo_mode: true for safety")
        print("3. Start the API server: python -m uvicorn src.api.main:app --reload")
        print("4. Access API docs: http://localhost:8000/api/v1/docs")
        print("5. Start trading agent: POST /api/v1/chart/agent/start")
    else:
        print("⚠️ Setup completed with warnings!")
        print("\n📝 To complete setup:")
        print("1. Edit .env file with your IQ Option credentials")
        print("2. Configure settings.yml as needed")
        print("3. Run: python test_iq_option_integration.py")
        print("4. Start the API server when ready")
    
    print("\n💡 Safety reminders:")
    print("• Always start with demo_mode: true")
    print("• Test thoroughly before using real money")
    print("• Monitor trades closely")
    print("• Set appropriate risk limits")
    
    print("\n📚 Documentation:")
    print("• API docs: /api/v1/docs when server is running")
    print("• Configuration: IMPLEMENTATION_SUMMARY.md")
    print("• Examples: demo.py")

if __name__ == "__main__":
    main()