"""
Setup and Authentication Helper
Helps with Hugging Face authentication and model access
"""

import os
from pathlib import Path


def check_hf_token():
    """Check if Hugging Face token is configured"""
    token_file = Path.home() / ".huggingface" / "token"
    
    if token_file.exists():
        print("✓ Hugging Face token found")
        return True
    
    if os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN"):
        print("✓ Hugging Face token found in environment")
        return True
    
    print("✗ No Hugging Face token found")
    return False


def setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*70)
    print("HUGGING FACE AUTHENTICATION REQUIRED")
    print("="*70)
    print("\nThe Llama-3.2-3B model requires authentication.")
    print("\nOption 1: Login via CLI (Recommended)")
    print("-" * 70)
    print("Run this command:")
    print("  huggingface-cli login")
    print("\nThen paste your token from: https://huggingface.co/settings/tokens")
    
    print("\nOption 2: Set Environment Variable")
    print("-" * 70)
    print("Set your token as an environment variable:")
    print("  $env:HF_TOKEN = 'your_token_here'  # PowerShell")
    print("  set HF_TOKEN=your_token_here       # CMD")
    
    print("\nOption 3: Request Access to Model")
    print("-" * 70)
    print("1. Go to: https://huggingface.co/meta-llama/Llama-3.2-3B")
    print("2. Click 'Request Access'")
    print("3. Wait for approval (usually instant)")
    print("4. Then run: huggingface-cli login")
    
    print("\n" + "="*70)
    print("\nAfter authentication, run the pipeline again:")
    print("  python pipeline.py \"Your topic here\"")
    print("="*70 + "\n")


def test_imports():
    """Test if all required packages are installed"""
    print("\n" + "="*70)
    print("TESTING PACKAGE INSTALLATIONS")
    print("="*70 + "\n")
    
    packages = {
        "transformers": "transformers",
        "bitsandbytes": "bitsandbytes",
        "accelerate": "accelerate",
        "edge_tts": "edge-tts",
        "torch": "torch"
    }
    
    all_ok = True
    
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False
    
    print("\n" + "="*70)
    
    if all_ok:
        print("✓ All packages installed successfully!")
    else:
        print("✗ Some packages are missing. Run:")
        print("  pip install -r requirements.txt")
    
    print("="*70 + "\n")
    
    return all_ok


def test_edge_tts():
    """Test edge-tts functionality"""
    print("\n" + "="*70)
    print("TESTING EDGE-TTS")
    print("="*70 + "\n")
    
    try:
        import edge_tts
        import asyncio
        
        async def test_tts():
            text = "This is a test of the text to speech system."
            voice = "en-US-ChristopherNeural"
            output_file = "test_audio.mp3"
            
            print(f"Generating test audio: {output_file}")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            
            if Path(output_file).exists():
                size = Path(output_file).stat().st_size
                print(f"✓ Audio generated successfully ({size} bytes)")
                
                # Clean up
                Path(output_file).unlink()
                print("✓ Test file cleaned up")
                return True
            else:
                print("✗ Audio file not created")
                return False
        
        result = asyncio.run(test_tts())
        
        print("\n" + "="*70)
        if result:
            print("✓ edge-tts is working correctly!")
        else:
            print("✗ edge-tts test failed")
        print("="*70 + "\n")
        
        return result
        
    except Exception as e:
        print(f"✗ Error testing edge-tts: {e}")
        print("\n" + "="*70)
        print("✗ edge-tts test failed")
        print("="*70 + "\n")
        return False


def main():
    """Run all setup checks"""
    print("\n" + "="*70)
    print(" "*20 + "SETUP VERIFICATION")
    print("="*70)
    
    # Test imports
    packages_ok = test_imports()
    
    if not packages_ok:
        return
    
    # Test edge-tts
    edge_tts_ok = test_edge_tts()
    
    # Check HF authentication
    hf_ok = check_hf_token()
    
    if not hf_ok:
        setup_instructions()
    else:
        print("\n" + "="*70)
        print("✓ ALL CHECKS PASSED!")
        print("="*70)
        print("\nYou're ready to use the pipeline:")
        print("  python pipeline.py \"Your topic here\"")
        print("\nOr run in interactive mode:")
        print("  python pipeline.py")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
# 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