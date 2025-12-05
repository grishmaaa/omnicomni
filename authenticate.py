"""
Quick Authentication Helper
Streamlines the Hugging Face authentication process
"""

import subprocess
import sys
from pathlib import Path


def check_huggingface_cli():
    """Check if huggingface-cli is installed"""
    try:
        result = subprocess.run(
            ["huggingface-cli", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_huggingface_cli():
    """Install huggingface-hub package"""
    print("\n" + "="*70)
    print("Installing huggingface-hub...")
    print("="*70 + "\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface-hub"],
            check=True
        )
        print("\n✓ huggingface-hub installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed to install huggingface-hub: {e}")
        return False


def run_login():
    """Run huggingface-cli login"""
    print("\n" + "="*70)
    print("HUGGING FACE LOGIN")
    print("="*70)
    print("\nYou'll need a Hugging Face token.")
    print("Get one here: https://huggingface.co/settings/tokens")
    print("\nPress Enter to continue...")
    input()
    
    try:
        subprocess.run(["huggingface-cli", "login"], check=True)
        print("\n✓ Login successful!")
        return True
    except subprocess.CalledProcessError:
        print("\n✗ Login failed")
        return False
    except KeyboardInterrupt:
        print("\n\nLogin cancelled")
        return False


def check_token():
    """Check if token exists"""
    token_file = Path.home() / ".huggingface" / "token"
    return token_file.exists()


def print_model_access_instructions():
    """Print instructions for requesting model access"""
    print("\n" + "="*70)
    print("REQUEST MODEL ACCESS")
    print("="*70)
    print("\nYou need to request access to Llama-3.2-3B:")
    print("\n1. Visit: https://huggingface.co/meta-llama/Llama-3.2-3B")
    print("2. Click the 'Request Access' button")
    print("3. Wait for approval (usually instant)")
    print("\nAfter approval, you can run the pipeline!")
    print("="*70 + "\n")


def main():
    """Main authentication flow"""
    print("\n" + "="*70)
    print(" "*15 + "HUGGING FACE AUTHENTICATION")
    print("="*70)
    
    # Check if already authenticated
    if check_token():
        print("\n✓ You're already logged in!")
        print("\nToken found at:", Path.home() / ".huggingface" / "token")
        
        response = input("\nDo you want to login again? (y/N): ").strip().lower()
        if response != 'y':
            print("\nSkipping login.")
            print_model_access_instructions()
            return
    
    # Check if huggingface-cli is installed
    if not check_huggingface_cli():
        print("\n⚠ huggingface-cli not found")
        response = input("Install it now? (Y/n): ").strip().lower()
        
        if response == 'n':
            print("\nYou can install it manually:")
            print("  pip install huggingface-hub")
            return
        
        if not install_huggingface_cli():
            return
    
    # Run login
    if run_login():
        print_model_access_instructions()
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Request model access (see above)")
        print("2. Run: python setup_check.py")
        print("3. Run: python pipeline.py \"Your topic\"")
        print("\n" + "="*70 + "\n")
    else:
        print("\nAuthentication incomplete.")
        print("Try again by running: python authenticate.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAuthentication cancelled.")
        sys.exit(0)
