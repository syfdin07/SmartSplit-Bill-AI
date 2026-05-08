"""
Receipt Processor Service
High-level service for processing receipts end-to-end
"""

from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.model_manager import get_model_manager, ModelType
from utils.bill_splitter import BillSplitter
from utils.validators import validate_image, validate_names, validate_receipt_data


class ReceiptProcessor:
    """
    High-level service for processing receipts.
    Handles the complete workflow from image to split bill.
    """
    
    def __init__(self, model_type: Optional[ModelType] = None):
        """
        Initialize receipt processor.
        
        Args:
            model_type: Type of model to use (None = auto-select)
        """
        self.model_manager = get_model_manager()
        self.model_type = model_type
        self.parser = None
        self.bill_splitter = BillSplitter()
        
        # Processing state
        self.current_receipt_data = None
        self.current_image = None
        self.processing_time = 0.0
    
    def process_receipt_image(
        self, 
        image: Image.Image,
        preload_model: bool = True,
        use_mock_on_failure: bool = True
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process receipt image and extract data.
        
        Args:
            image: PIL Image object
            preload_model: Whether to preload model before processing
            use_mock_on_failure: Use mock parser if AI fails
            
        Returns:
            Tuple of (success, message, receipt_data)
        """
        start_time = time.time()
        
        # Validate image
        is_valid, error_msg = validate_image(image)
        if not is_valid:
            return False, f"Invalid image: {error_msg}", None
        
        self.current_image = image
        
        try:
            # Get parser
            if self.parser is None:
                self.parser = self.model_manager.get_parser(model_type=self.model_type)
            
            # Load model if needed
            if not self.parser.is_loaded:
                if preload_model:
                    print("Loading model...")
                self.parser.load_model()
            
            # Parse receipt
            print("Processing receipt...")
            receipt_data = self.parser.parse_receipt(image)
            
            # Validate result
            is_valid, error_msg = validate_receipt_data(receipt_data)
            if not is_valid:
                # Try mock parser as fallback
                if use_mock_on_failure:
                    print(f"⚠️ AI parsing failed: {error_msg}")
                    print("🔄 Using mock parser as fallback...")
                    
                    from models.mock_parser import MockReceiptParser
                    mock_parser = MockReceiptParser()
                    receipt_data = mock_parser.parse_receipt(image)
                    
                    # Validate mock data
                    is_valid, error_msg = validate_receipt_data(receipt_data)
                    if is_valid:
                        self.current_receipt_data = receipt_data
                        self.processing_time = time.time() - start_time
                        receipt_data["processing_time"] = self.processing_time
                        
                        return True, "⚠️ AI parsing failed - using sample data for demonstration", receipt_data
                
                return False, f"Invalid receipt data: {error_msg}", receipt_data
            
            # Store result
            self.current_receipt_data = receipt_data
            self.processing_time = time.time() - start_time
            
            # Add processing metadata
            receipt_data["processing_time"] = self.processing_time
            receipt_data["model_used"] = self.parser.model_name
            
            return True, "Receipt processed successfully", receipt_data
            
        except Exception as e:
            # Try mock parser as fallback
            if use_mock_on_failure:
                print(f"⚠️ Error: {str(e)}")
                print("🔄 Using mock parser as fallback...")
                
                try:
                    from models.mock_parser import MockReceiptParser
                    mock_parser = MockReceiptParser()
                    receipt_data = mock_parser.parse_receipt(image)
                    
                    self.current_receipt_data = receipt_data
                    self.processing_time = time.time() - start_time
                    receipt_data["processing_time"] = self.processing_time
                    
                    return True, "⚠️ AI processing error - using sample data for demonstration", receipt_data
                except Exception as mock_error:
                    error_msg = f"Error with mock parser: {str(mock_error)}"
                    print(f"❌ {error_msg}")
                    return False, error_msg, None
            
            error_msg = f"Error processing receipt: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg, None
    
    def setup_bill_split(
        self,
        people_names: List[str],
        receipt_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Setup bill splitting with people names.
        
        Args:
            people_names: List of person names
            receipt_data: Receipt data (uses current if None)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate names
        is_valid, error_msg = validate_names(people_names)
        if not is_valid:
            return False, f"Invalid names: {error_msg}"
        
        # Use provided or current receipt data
        if receipt_data is None:
            receipt_data = self.current_receipt_data
        
        if receipt_data is None:
            return False, "No receipt data available. Process a receipt first."
        
        try:
            # Setup bill splitter
            self.bill_splitter.set_people(people_names)
            self.bill_splitter.set_items(receipt_data["items"])
            self.bill_splitter.set_additional_charges(
                receipt_data.get("additional_charges", [])
            )
            self.bill_splitter.set_total(receipt_data["total"])
            
            return True, f"Bill split setup for {len(people_names)} people"
            
        except Exception as e:
            error_msg = f"Error setting up bill split: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def assign_item_to_people(
        self,
        item_index: int,
        person_names: List[str]
    ) -> Tuple[bool, str]:
        """
        Assign an item to one or more people.
        
        Args:
            item_index: Index of the item
            person_names: List of person names
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.bill_splitter.assign_item(item_index, person_names)
            return True, f"Item {item_index} assigned to {', '.join(person_names)}"
            
        except Exception as e:
            error_msg = f"Error assigning item: {str(e)}"
            return False, error_msg
    
    def calculate_split(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Calculate the bill split.
        
        Returns:
            Tuple of (success, message, split_result)
        """
        try:
            # Calculate split
            split_result = self.bill_splitter.calculate_split()
            
            # Validate split
            is_valid = self.bill_splitter.validate_split(split_result)
            
            if not is_valid:
                summary = self.bill_splitter.get_summary(split_result)
                return False, (
                    f"Split validation failed! "
                    f"Calculated total: ${summary['calculated_total']:.2f}, "
                    f"Bill total: ${summary['bill_total']:.2f}, "
                    f"Difference: ${summary['difference']:.2f}"
                ), split_result
            
            # Get summary
            summary = self.bill_splitter.get_summary(split_result)
            
            return True, "Bill split calculated successfully", {
                "split": split_result,
                "summary": summary
            }
            
        except Exception as e:
            error_msg = f"Error calculating split: {str(e)}"
            return False, error_msg, None
    
    def process_complete_workflow(
        self,
        image: Image.Image,
        people_names: List[str],
        item_assignments: Dict[int, List[str]]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process complete workflow from image to split result.
        
        Args:
            image: Receipt image
            people_names: List of person names
            item_assignments: Dict mapping item_index to list of person names
            
        Returns:
            Tuple of (success, message, result)
        """
        # Step 1: Process receipt
        success, msg, receipt_data = self.process_receipt_image(image)
        if not success:
            return False, msg, None
        
        # Step 2: Setup bill split
        success, msg = self.setup_bill_split(people_names, receipt_data)
        if not success:
            return False, msg, None
        
        # Step 3: Assign items
        for item_idx, assigned_people in item_assignments.items():
            success, msg = self.assign_item_to_people(item_idx, assigned_people)
            if not success:
                return False, msg, None
        
        # Step 4: Calculate split
        success, msg, split_data = self.calculate_split()
        if not success:
            return False, msg, None
        
        # Combine all data
        result = {
            "receipt_data": receipt_data,
            "split_data": split_data,
            "processing_time": self.processing_time
        }
        
        return True, "Complete workflow processed successfully", result
    
    def get_receipt_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary of current receipt.
        
        Returns:
            Summary dictionary or None
        """
        if self.current_receipt_data is None:
            return None
        
        return {
            "num_items": len(self.current_receipt_data.get("items", [])),
            "subtotal": self.current_receipt_data.get("subtotal", 0),
            "total": self.current_receipt_data.get("total", 0),
            "num_charges": len(self.current_receipt_data.get("additional_charges", [])),
            "model_used": self.current_receipt_data.get("model_used", "Unknown"),
            "processing_time": self.processing_time
        }
    
    def reset(self) -> None:
        """Reset processor state"""
        self.current_receipt_data = None
        self.current_image = None
        self.processing_time = 0.0
        self.bill_splitter = BillSplitter()


# Test function
def test_receipt_processor():
    """Test function for ReceiptProcessor"""
    print("=" * 60)
    print("Testing Receipt Processor")
    print("=" * 60)
    
    # Initialize processor
    processor = ReceiptProcessor()
    
    print("\n✅ Receipt Processor initialized")
    print(f"Default model: {processor.model_manager.get_default_model_type().value}")
    
    # Test with mock data (since we don't have actual receipt image yet)
    print("\n📝 Note: Full testing requires actual receipt images")
    print("Add receipt images to data/ directory and run experiments/run_experiment.py")
    
    # Show available models
    print("\n📋 Available Models:")
    models = processor.model_manager.get_available_models()
    for model_id, info in models.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {info['name']}: {info['description']}")
    
    print("\n✅ Receipt Processor test completed!")


if __name__ == "__main__":
    test_receipt_processor()
