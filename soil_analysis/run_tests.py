#!/usr/bin/env python3
"""
Test runner script for the soil analysis backend
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests and display results"""
    print("🧪 Running Soil Analysis Backend Tests...")
    print("=" * 50)
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-v", "--tb=short", "--color=yes"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
