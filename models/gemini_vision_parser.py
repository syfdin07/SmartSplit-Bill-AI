"""
Google Gemini Vision Receipt Parser
Implementation of receipt parsing using Google Gemini Vision API
"""

import time
import base64
import io
from typing import Dict, Any, List
from PIL import Image
import json
import os
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ Warning: google-generativeai package not installed. Run: pip install google-generativeai")
    genai = None

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser


class GeminiVisionParser(BaseReceiptParser):
    """
    Receipt parser using Google Gemini Vision API.
    Requires Google API key.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini Vision parser
        
        Args:
            api_key: Google API key (if None, will try to load from .env)
        """
        super().__init__("gemini-pro-vision")
        
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            print("⚠️ Warning: No Google API key provided!")
            print("Set GOOGLE_API_KEY in .env file or pass as parameter")
        
        self.model = None
        
    def load_model(self) -> None:
        """
        Initialize Gemini client.
        """
        if genai is None:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        if not self.api_key:
            raise ValueError("Google API key not provided!")
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Use gemini-pro-vision for image understanding
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            self.is_loaded = True
            print("✓ Gemini Vision client initialized successfully!")
            
        except Exception as e:
            print(f"✗ Error initializing Gemini client: {str(e)}")
            raise
    
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Parse receipt image using Gemini Vision API.
        
        Args:
            image: PIL Image object of the receipt
            
        Returns:
            Dictionary containing parsed receipt data
        """
        if not self.is_loaded:
            self.load_model()
        
        start_time = time.time()
        
        try:
            # Create prompt for Gemini
            prompt = self._create_prompt()
            
            # Call API with image
            response = self.model.generate_content([prompt, image])
            
            # Extract response text
            content = response.text
            
            # Parse JSON from response
            result = self._parse_response(content)
            
            inference_time = time.time() - start_time
            result["inference_time"] = inference_time
            result["raw_output"] = content
            result["model_name"] = self.model_name
            
            print(f"✓ Gemini Vision inference completed in {inference_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"✗ Error during Gemini Vision inference: {str(e)}")
            raise
    
    def _create_prompt(self) -> str:
        """
        Create prompt for Gemini Vision to extract receipt data.
        
        Returns:
            Prompt string
        """
        prompt = """Analyze this receipt image and extract the following information in JSON format:

{
  "items": [
    {
      "name": "item name",
      "quantity": 1,
      "price": 10.00,
      "total": 10.00
    }
  ],
  "subtotal": 100.00,
  "additional_charges": [
    {
      "name": "Tax/Service/etc",
      "amount": 10.00
    }
  ],
  "total": 110.00
}

Instructions:
1. Extract ALL items with their names, quantities, unit prices, and totals
2. Calculate subtotal (sum of all item totals before charges)
3. Extract any additional charges (tax, service charge, delivery fee, etc.) - ONLY if they ADD to the total
4. Do NOT include discounts as additional charges (discounts reduce the total)
5. Extract the final total amount
6. Use numbers only (no currency symbols like Rp, $, etc.)
7. If quantity is not shown, assume 1
8. Return ONLY the JSON, no additional text or explanation
9. For Indonesian receipts: convert "Rp" amounts to numbers

Be precise and accurate. Double-check all numbers."""
        
        return prompt
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse Gemini Vision response to extract JSON.
        
        Args:
            content: Response content from API
            
        Returns:
            Parsed receipt data
        """
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Validate and ensure all required fields exist
                if "items" not in data:
                    data["items"] = []
                if "subtotal" not in data:
                    data["subtotal"] = sum(item.get("total", 0) for item in data["items"])
                if "additional_charges" not in data:
                    data["additional_charges"] = []
                if "total" not in data:
                    data["total"] = data["subtotal"] + sum(
                        charge.get("amount", 0) for charge in data["additional_charges"]
                    )
                
                return data
            else:
                raise ValueError("No JSON found in response")
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Warning: Could not parse JSON from response: {str(e)}")
            print(f"Raw response: {content}")
            
            # Return empty structure
            return {
                "items": [],
                "subtotal": 0.0,
                "additional_charges": [],
                "total": 0.0,
                "error": "Failed to parse response",
                "raw_response": content
            }
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the Gemini Vision model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        info["model_type"] = "Google Gemini Vision (API)"
        info["api_based"] = "Yes"
        info["requires_internet"] = "Yes"
        info["cost_per_image"] = "Free tier available"
        return info


# Test function
def test_gemini_vision_parser():
    """Test function for Gemini Vision parser"""
    print("=" * 60)
    print("Testing Gemini Vision Receipt Parser")
    print("=" * 60)
    
    # Check if API key is available
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("\n⚠️ No Google API key found!")
        print("To test Gemini Vision:")
        print("1. Create a .env file in project root")
        print("2. Add: GOOGLE_API_KEY=your_api_key_here")
        return
    
    # Initialize parser
    parser = GeminiVisionParser()
    
    # Load model (initialize client)
    try:
        parser.load_model()
        
        # Get model info
        info = parser.get_model_info()
        print("\nModel Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n✓ Gemini Vision parser test completed!")
        print("Ready to parse receipts.")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    test_gemini_vision_parser()
