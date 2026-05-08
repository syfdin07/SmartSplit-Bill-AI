"""
Validators
Input validation utilities
"""

from PIL import Image
from typing import List, Tuple


def validate_image(image: Image.Image) -> Tuple[bool, str]:
    """
    Validate uploaded image.
    
    Args:
        image: PIL Image object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if image is valid
        if image is None:
            return False, "Image is None"
        
        # Check image size
        width, height = image.size
        if width < 100 or height < 100:
            return False, "Image too small (minimum 100x100 pixels)"
        
        if width > 10000 or height > 10000:
            return False, "Image too large (maximum 10000x10000 pixels)"
        
        # Check image mode
        if image.mode not in ['RGB', 'RGBA', 'L']:
            return False, f"Unsupported image mode: {image.mode}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error validating image: {str(e)}"


def validate_names(names: List[str]) -> Tuple[bool, str]:
    """
    Validate list of person names.
    
    Args:
        names: List of person names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not names:
        return False, "No names provided"
    
    if len(names) < 2:
        return False, "At least 2 people required for bill splitting"
    
    # Check for empty names
    for name in names:
        if not name or not name.strip():
            return False, "Empty name found"
    
    # Check for duplicate names
    if len(names) != len(set(names)):
        return False, "Duplicate names found"
    
    # Check name length
    for name in names:
        if len(name) > 50:
            return False, f"Name too long: {name}"
    
    return True, ""


def validate_receipt_data(data: dict) -> Tuple[bool, str]:
    """
    Validate parsed receipt data structure.
    
    Args:
        data: Parsed receipt data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ["items", "subtotal", "total"]
    
    # Check required keys
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
    
    # Validate items
    if not isinstance(data["items"], list):
        return False, "Items must be a list"
    
    if len(data["items"]) == 0:
        return False, "No items found in receipt"
    
    # Validate each item
    for idx, item in enumerate(data["items"]):
        required_item_keys = ["name", "quantity", "price", "total"]
        for key in required_item_keys:
            if key not in item:
                return False, f"Item {idx} missing key: {key}"
        
        # Validate numeric values
        try:
            quantity = float(item["quantity"])
            price = float(item["price"])
            total = float(item["total"])
            
            if quantity <= 0:
                return False, f"Item {idx} has invalid quantity: {quantity}"
            if price < 0:
                return False, f"Item {idx} has invalid price: {price}"
            if total < 0:
                return False, f"Item {idx} has invalid total: {total}"
                
        except (ValueError, TypeError):
            return False, f"Item {idx} has non-numeric values"
    
    # Validate subtotal and total
    try:
        subtotal = float(data["subtotal"])
        total = float(data["total"])
        
        if subtotal < 0:
            return False, f"Invalid subtotal: {subtotal}"
        if total < 0:
            return False, f"Invalid total: {total}"
        if total < subtotal:
            return False, "Total cannot be less than subtotal"
            
    except (ValueError, TypeError):
        return False, "Subtotal or total is not numeric"
    
    return True, ""
