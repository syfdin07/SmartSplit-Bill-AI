"""
Unit Tests for Validators
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image
from utils.validators import validate_image, validate_names, validate_receipt_data


def test_validate_image():
    """Test image validation"""
    print("\n" + "=" * 60)
    print("Test: Image Validation")
    print("=" * 60)
    
    # Test valid image
    valid_image = Image.new('RGB', (800, 600), color='white')
    is_valid, msg = validate_image(valid_image)
    print(f"\nValid image (800x600): {is_valid}")
    assert is_valid, "Should accept valid image"
    
    # Test too small image
    small_image = Image.new('RGB', (50, 50), color='white')
    is_valid, msg = validate_image(small_image)
    print(f"Small image (50x50): {is_valid} - {msg}")
    assert not is_valid, "Should reject too small image"
    
    # Test too large image
    large_image = Image.new('RGB', (15000, 15000), color='white')
    is_valid, msg = validate_image(large_image)
    print(f"Large image (15000x15000): {is_valid} - {msg}")
    assert not is_valid, "Should reject too large image"
    
    print("\n✅ Test passed!")


def test_validate_names():
    """Test names validation"""
    print("\n" + "=" * 60)
    print("Test: Names Validation")
    print("=" * 60)
    
    # Test valid names
    valid_names = ["Alice", "Bob", "Charlie"]
    is_valid, msg = validate_names(valid_names)
    print(f"\nValid names: {is_valid}")
    assert is_valid, "Should accept valid names"
    
    # Test empty list
    is_valid, msg = validate_names([])
    print(f"Empty list: {is_valid} - {msg}")
    assert not is_valid, "Should reject empty list"
    
    # Test single name
    is_valid, msg = validate_names(["Alice"])
    print(f"Single name: {is_valid} - {msg}")
    assert not is_valid, "Should reject single name (need at least 2)"
    
    # Test duplicate names
    is_valid, msg = validate_names(["Alice", "Bob", "Alice"])
    print(f"Duplicate names: {is_valid} - {msg}")
    assert not is_valid, "Should reject duplicate names"
    
    # Test empty name
    is_valid, msg = validate_names(["Alice", "", "Bob"])
    print(f"Empty name: {is_valid} - {msg}")
    assert not is_valid, "Should reject empty name"
    
    print("\n✅ Test passed!")


def test_validate_receipt_data():
    """Test receipt data validation"""
    print("\n" + "=" * 60)
    print("Test: Receipt Data Validation")
    print("=" * 60)
    
    # Test valid data
    valid_data = {
        "items": [
            {"name": "Item1", "quantity": 1, "price": 10.0, "total": 10.0},
            {"name": "Item2", "quantity": 2, "price": 5.0, "total": 10.0}
        ],
        "subtotal": 20.0,
        "additional_charges": [
            {"name": "Tax", "amount": 2.0}
        ],
        "total": 22.0
    }
    is_valid, msg = validate_receipt_data(valid_data)
    print(f"\nValid data: {is_valid}")
    assert is_valid, "Should accept valid data"
    
    # Test missing items
    invalid_data = {
        "subtotal": 20.0,
        "total": 22.0
    }
    is_valid, msg = validate_receipt_data(invalid_data)
    print(f"Missing items: {is_valid} - {msg}")
    assert not is_valid, "Should reject missing items"
    
    # Test empty items
    invalid_data = {
        "items": [],
        "subtotal": 0.0,
        "total": 0.0
    }
    is_valid, msg = validate_receipt_data(invalid_data)
    print(f"Empty items: {is_valid} - {msg}")
    assert not is_valid, "Should reject empty items"
    
    # Test invalid item structure
    invalid_data = {
        "items": [
            {"name": "Item1"}  # Missing required fields
        ],
        "subtotal": 10.0,
        "total": 10.0
    }
    is_valid, msg = validate_receipt_data(invalid_data)
    print(f"Invalid item structure: {is_valid} - {msg}")
    assert not is_valid, "Should reject invalid item structure"
    
    # Test negative values
    invalid_data = {
        "items": [
            {"name": "Item1", "quantity": 1, "price": -10.0, "total": -10.0}
        ],
        "subtotal": -10.0,
        "total": -10.0
    }
    is_valid, msg = validate_receipt_data(invalid_data)
    print(f"Negative values: {is_valid} - {msg}")
    assert not is_valid, "Should reject negative values"
    
    print("\n✅ Test passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING ALL VALIDATOR TESTS")
    print("=" * 60)
    
    tests = [
        test_validate_image,
        test_validate_names,
        test_validate_receipt_data
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ Test error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
