"""
Simple Test Runner (No Model Dependencies)
Run tests that don't require AI model dependencies
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_bill_splitter_basic():
    """Test basic bill splitter functionality"""
    print("\n" + "=" * 60)
    print("Test: Bill Splitter - Basic Functionality")
    print("=" * 60)
    
    # Import here to avoid model dependencies
    from utils.bill_splitter import BillSplitter
    
    splitter = BillSplitter()
    
    # Set people
    people = ["Alice", "Bob"]
    splitter.set_people(people)
    
    # Set items
    items = [
        {"name": "Pizza", "quantity": 1, "price": 20.0, "total": 20.0},
        {"name": "Coke", "quantity": 2, "price": 3.0, "total": 6.0}
    ]
    splitter.set_items(items)
    
    # Set charges
    charges = [{"name": "Tax", "amount": 2.6}]
    splitter.set_additional_charges(charges)
    
    # Set total
    total = 28.6
    splitter.set_total(total)
    
    # Assign items
    splitter.assign_item(0, ["Alice", "Bob"])
    splitter.assign_item(1, ["Bob"])
    
    # Calculate
    result = splitter.calculate_split()
    is_valid = splitter.validate_split(result)
    
    print(f"\n[OK] Split valid: {is_valid}")
    print(f"Alice pays: ${result['Alice']['total']:.2f}")
    print(f"Bob pays: ${result['Bob']['total']:.2f}")
    
    assert is_valid, "Split should be valid"
    print("\n[OK] Test passed!")
    return True


def test_validators():
    """Test validator functions"""
    print("\n" + "=" * 60)
    print("Test: Validators")
    print("=" * 60)
    
    from PIL import Image
    from utils.validators import validate_image, validate_names, validate_receipt_data
    
    # Test image validation
    valid_image = Image.new('RGB', (800, 600), color='white')
    is_valid, _ = validate_image(valid_image)
    assert is_valid, "Should accept valid image"
    print("[OK] Image validation works")
    
    # Test names validation
    valid_names = ["Alice", "Bob"]
    is_valid, _ = validate_names(valid_names)
    assert is_valid, "Should accept valid names"
    print("[OK] Names validation works")
    
    # Test receipt data validation
    valid_data = {
        "items": [{"name": "Item1", "quantity": 1, "price": 10.0, "total": 10.0}],
        "subtotal": 10.0,
        "total": 10.0
    }
    is_valid, _ = validate_receipt_data(valid_data)
    assert is_valid, "Should accept valid data"
    print("[OK] Receipt data validation works")
    
    print("\n[OK] Test passed!")
    return True


def main():
    """Run all simple tests"""
    print("\n" + "=" * 70)
    print(" " * 15 + "SMARTSPLIT BILL AI - SIMPLE TEST SUITE")
    print("=" * 70)
    print("\nNote: These tests don't require AI model dependencies")
    print("For full testing, install dependencies: pip install -r requirements.txt")
    
    tests = [
        ("Bill Splitter", test_bill_splitter_basic),
        ("Validators", test_validators)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_name} failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_name} error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Final summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    if failed == 0:
        print("[OK] ALL TESTS PASSED!")
    else:
        print("[FAIL] SOME TESTS FAILED!")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
