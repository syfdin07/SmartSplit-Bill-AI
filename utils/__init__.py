"""
Utilities Package
Helper functions and utilities for the application
"""

# Import only what's needed to avoid circular dependencies
# and heavy model dependencies

__all__ = [
    'BillSplitter', 
    'validate_image', 
    'validate_names', 
    'validate_receipt_data',
    'ReceiptProcessor'
]

# Lazy imports to avoid loading heavy dependencies
def __getattr__(name):
    if name == 'BillSplitter':
        from .bill_splitter import BillSplitter
        return BillSplitter
    elif name == 'validate_image':
        from .validators import validate_image
        return validate_image
    elif name == 'validate_names':
        from .validators import validate_names
        return validate_names
    elif name == 'validate_receipt_data':
        from .validators import validate_receipt_data
        return validate_receipt_data
    elif name == 'ReceiptProcessor':
        from .receipt_processor import ReceiptProcessor
        return ReceiptProcessor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
