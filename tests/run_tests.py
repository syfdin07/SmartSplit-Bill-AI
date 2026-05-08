"""
Test Runner
Run all unit tests
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_bill_splitter import run_all_tests as run_bill_splitter_tests
from tests.test_validators import run_all_tests as run_validator_tests


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print(" " * 20 + "SMARTSPLIT BILL AI - TEST SUITE")
    print("=" * 70)
    
    all_passed = True
    
    # Run validator tests
    print("\n📋 Running Validator Tests...")
    if not run_validator_tests():
        all_passed = False
    
    # Run bill splitter tests
    print("\n📋 Running Bill Splitter Tests...")
    if not run_bill_splitter_tests():
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
