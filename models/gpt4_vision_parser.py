"""
GPT-4 Vision Receipt Parser
Implementation of receipt parsing using 0penAI GPT-4 Vision API
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
    from openai import OpenAI
except ImportError:
    print("⚠️ Warning: openai package not installed. Run: pip install openai")
    OpenAI = None

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser


class GPT4VisionParser(BaseReceiptParser):
    """
    Receipt parser using 0penAI GPT-4 Vision API.
    Requires 0penAI API key.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize GPT-4 Vision parser
        
        Args:
            api_key: 0penAI API key (if None, will try to load from .env)
        """
        super().__init__("gpt-4-vision-preview")
        
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            print("⚠️ Warning: No 0penAI API key provided!")
            print("Set OPENAI_API_KEY in .env file or pass as parameter")
        
        self.client = None
        
    def load_model(self) -> None:
        """
        Initialize 0penAI client.
        No actual model loading needed for API.
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        if not self.api_key:
            raise ValueError("0penAI API key not provided!")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.is_loaded = True
            print("✅ GPT-4 Vision client initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing 0penAI client: {str(e)}")
            raise
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Parse receipt image using GPT-4 Vision API.
        
        Args:
            image: PIL Image object of the receipt
            
        Returns:
            Dictionary containing parsed receipt data
        """
        if not self.is_loaded:
            self.load_model()
        
        start_time = time.time()
        
        try:
            # Convert image to base64
            base64_image = self._image_to_base64(image)
            
            # Create prompt for GPT-4 Vision
            prompt = self._create_prompt()
            
            # Call API
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Parse JSON from response
            result = self._parse_response(content)
            
            inference_time = time.time() - start_time
            result["inference_time"] = inference_time
            result["raw_output"] = content
            result["model_name"] = self.model_name
            
            print(f"✅ GPT-4 Vision inference completed in {inference_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during GPT-4 Vision inference: {str(e)}")
            raise
    
    def _create_prompt(self) -> str:
        """
        Create prompt for GPT-4 Vision to extract receipt data.
        
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
3. Extract any additional charges (tax, service charge, delivery fee, etc.)
4. Extract the final total amount
5. Use numbers only (no currency symbols)
6. If quantity is not shown, assume 1
7. Return ONLY the JSON, no additional text

Be precise and accurate. Double-check all numbers."""
        
        return prompt
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse GPT-4 Vision response to extract JSON.
        
        Args:
            content: Response content from API
            
        Returns:
            Parsed receipt data
        """
        try:
            # Try to find JSON in the response
            # Sometimes GPT-4 adds explanation before/after JSON
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
        Get information about the GPT-4 Vision model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        info["model_type"] = "GPT-4 Vision (0penAI API)"
        info["api_based"] = "Yes"
        info["requires_internet"] = "Yes"
        info["cost_per_image"] = "~$0.01-0.03"
        return info


# Test function
def test_gpt4_vision_parser():
    """Test function for GPT-4 Vision parser"""
    print("=" * 50)
    print("Testing GPT-4 Vision Receipt Parser")
    print("=" * 50)
    
    # Check if API key is available
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("\n⚠️ No 0penAI API key found!")
        print("To test GPT-4 Vision:")
        print("1. Create a .env file in project root")
        print("2. Add: OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize parser
    parser = GPT4VisionParser()
    
    # Load model (initialize client)
    parser.load_model()
    
    # Get model info
    info = parser.get_model_info()
    print("\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ GPT-4 Vision parser test completed!")
    print("Ready to parse receipts.")


if __name__ == "__main__":
    test_gpt4_vision_parser()
