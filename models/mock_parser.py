"""
Mock Receipt Parser
Fallback parser when AI models fail
"""

from typing import Dict, Any
from PIL import Image
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser


class MockReceiptParser(BaseReceiptParser):
    """
    Mock parser that returns sample data.
    Used as fallback when AI models fail.
    """
    
    def __init__(self):
        super().__init__("mock-parser")
        self.is_loaded = True
    
    def load_model(self) -> None:
        """No model to load for mock parser"""
        self.is_loaded = True
        print("Mock parser ready (no model loading needed)")
    
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Return sample receipt data based on the Jifa Mart receipt.
        
        Args:
            image: PIL Image object (not used in mock)
            
        Returns:
            Sample receipt data
        """
        print("Using mock parser - returning sample data")
        
        # Sample data based on Jifa Mart receipt
        # Subtotal: 34,000
        # Diskon: -34,000 (Grand Total di struk asli)
        # Tunai: 50,000
        # Kembali: 16,000
        # Jadi Total yang dibayar = 34,000 (setelah diskon)
        
        return {
            "items": [
                {
                    "name": "DIPLOMAT MILD BERRY",
                    "quantity": 1,
                    "price": 26500.0,
                    "total": 26500.0
                },
                {
                    "name": "POCARI 500ML",
                    "quantity": 1,
                    "price": 7500.0,
                    "total": 7500.0
                }
            ],
            "subtotal": 34000.0,
            "additional_charges": [],  # Tidak ada biaya tambahan
            "total": 34000.0,  # Total = Subtotal (tidak ada pajak/service)
            "model_name": "mock-parser",
            "note": "Sample data - AI parsing failed, using mock data for demonstration"
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get mock parser info"""
        info = super().get_model_info()
        info["model_type"] = "Mock Parser (Fallback)"
        info["note"] = "Returns sample data when AI fails"
        return info


# Test function
def test_mock_parser():
    """Test mock parser"""
    print("=" * 60)
    print("Testing Mock Receipt Parser")
    print("=" * 60)
    
    parser = MockReceiptParser()
    parser.load_model()
    
    # Create dummy image
    dummy_image = Image.new('RGB', (100, 100), color='white')
    
    result = parser.parse_receipt(dummy_image)
    
    print("\nSample Receipt Data:")
    print(f"Items: {len(result['items'])}")
    for item in result['items']:
        print(f"  - {item['name']}: Rp {item['total']:,.0f}")
    print(f"Subtotal: Rp {result['subtotal']:,.0f}")
    print(f"Total: Rp {result['total']:,.0f}")
    
    print("\n✓ Mock parser test completed!")


if __name__ == "__main__":
    test_mock_parser()
