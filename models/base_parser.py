"""
Base Receipt Parser
Abstract base class for all receipt parsing models
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from PIL import Image


class BaseReceiptParser(ABC):
    """
    Abstract base class for receipt parsing models.
    All receipt parser implementations should inherit from this class.
    """
    
    def __init__(self, model_name: str):
        """
        Initialize the parser
        
        Args:
            model_name: Name of the model being used
        """
        self.model_name = model_name
        self.is_loaded = False
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load the AI model into memory.
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Parse receipt image and extract structured data.
        
        Args:
            image: PIL Image object of the receipt
            
        Returns:
            Dictionary containing parsed receipt data with structure:
            {
                "items": [
                    {
                        "name": str,
                        "quantity": int,
                        "price": float,
                        "total": float
                    }
                ],
                "subtotal": float,
                "additional_charges": [
                    {
                        "name": str,
                        "amount": float
                    }
                ],
                "total": float,
                "raw_text": str (optional)
            }
        """
        pass
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate the parsed result structure.
        
        Args:
            result: Parsed receipt data
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["items", "subtotal", "total"]
        
        if not all(key in result for key in required_keys):
            return False
        
        if not isinstance(result["items"], list):
            return False
        
        for item in result["items"]:
            if not all(key in item for key in ["name", "quantity", "price", "total"]):
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded
        }
