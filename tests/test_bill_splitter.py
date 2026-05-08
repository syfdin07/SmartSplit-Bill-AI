"""
Unit Tests for Bill Splitter
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.bill_splitter import BillSplitter


def test_basic_split():
    """Test basic bill splitting"""
    print("\n" + "=" * 60)
    print("Test: Basic Bill Split")
    print("=" * 60)
    
    # Setup
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
    splitter.assign_item(0, ["Alice", "Bob"])  # Pizza split
    splitter.assign_item(1, ["Bob"])  # Coke for Bob only
    
    # Calculate
    result = splitter.calculate_split()
    
    # Validate
    is_valid = splitter.validate_split(result)
    summary = splitter.get_summary(result)
    
    # Print results
    print("\n📊 Results:")
    for person, data in result.items():
        print(f"\n{person}:")
        print(f"  Items: {len(data['items'])}")
        print(f"  Subtotal: ${data['subtotal']:.2f}")
        print(f"  Charges: ${data['additional_charges']:.2f}")
        print(f"  Total: ${data['total']:.2f}")
    
    print(f"\n✅ Valid: {is_valid}")
    print(f"Bill Total: ${summary['bill_total']:.2f}")
    print(f"Calculated Total: ${summary['calculated_total']:.2f}")
    print(f"Difference: ${summary['difference']:.2f}")
    
    assert is_valid, "Split should be valid"
    assert abs(summary['difference']) < 0.01, "Difference should be minimal"
    
    print("\n✅ Test passed!")


def test_equal_split():
    """Test equal split among all people"""
    print("\n" + "=" * 60)
    print("Test: Equal Split")
    print("=" * 60)
    
    splitter = BillSplitter()
    
    people = ["Alice", "Bob", "Charlie"]
    splitter.set_people(people)
    
    items = [
        {"name": "Dinner", "quantity": 1, "price": 90.0, "total": 90.0}
    ]
    splitter.set_items(items)
    
    charges = [{"name": "Service", "amount": 9.0}]
    splitter.set_additional_charges(charges)
    
    total = 99.0
    splitter.set_total(total)
    
    # Everyone shares the dinner
    splitter.assign_item(0, ["Alice", "Bob", "Charlie"])
    
    result = splitter.calculate_split()
    is_valid = splitter.validate_split(result)
    
    # Each person should pay 33.0
    for person, data in result.items():
        print(f"{person}: ${data['total']:.2f}")
        assert abs(data['total'] - 33.0) < 0.01, f"{person} should pay $33.00"
    
    assert is_valid, "Split should be valid"
    print("\n✅ Test passed!")


def test_unassigned_items():
    """Test with unassigned items"""
    print("\n" + "=" * 60)
    print("Test: Unassigned Items")
    print("=" * 60)
    
    splitter = BillSplitter()
    
    people = ["Alice", "Bob"]
    splitter.set_people(people)
    
    items = [
        {"name": "Item1", "quantity": 1, "price": 10.0, "total": 10.0},
        {"name": "Item2", "quantity": 1, "price": 20.0, "total": 20.0}
    ]
    splitter.set_items(items)
    
    charges = []
    splitter.set_additional_charges(charges)
    
    total = 30.0
    splitter.set_total(total)
    
    # Only assign first item
    splitter.assign_item(0, ["Alice"])
    # Item 1 is unassigned
    
    result = splitter.calculate_split()
    is_valid = splitter.validate_split(result)
    
    print(f"\nAlice: ${result['Alice']['total']:.2f}")
    print(f"Bob: ${result['Bob']['total']:.2f}")
    
    # Should not be valid because not all items assigned
    calculated_total = result['Alice']['total'] + result['Bob']['total']
    print(f"\nCalculated: ${calculated_total:.2f}, Expected: ${total:.2f}")
    
    assert not is_valid, "Split should be invalid with unassigned items"
    print("\n✅ Test passed!")


def test_single_person():
    """Test with single person (edge case)"""
    print("\n" + "=" * 60)
    print("Test: Single Person")
    print("=" * 60)
    
    splitter = BillSplitter()
    
    people = ["Alice"]
    splitter.set_people(people)
    
    items = [
        {"name": "Lunch", "quantity": 1, "price": 15.0, "total": 15.0}
    ]
    splitter.set_items(items)
    
    charges = [{"name": "Tax", "amount": 1.5}]
    splitter.set_additional_charges(charges)
    
    total = 16.5
    splitter.set_total(total)
    
    splitter.assign_item(0, ["Alice"])
    
    result = splitter.calculate_split()
    is_valid = splitter.validate_split(result)
    
    print(f"\nAlice: ${result['Alice']['total']:.2f}")
    
    assert is_valid, "Split should be valid"
    assert abs(result['Alice']['total'] - 16.5) < 0.01, "Alice should pay full amount"
    
    print("\n✅ Test passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RUNNING ALL BILL SPLITTER TESTS")
    print("=" * 60)
    
    tests = [
        test_basic_split,
        test_equal_split,
        test_unassigned_items,
        test_single_person
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
