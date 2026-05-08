"""
AIGateway AI Universal Parser
Works with any vision-capable model through aigateway API gateway
"""

import time
import base64
import io
from typing import Dict, Any, List, Optional
from PIL import Image
import json
import os
import requests
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser


class aigatewayParser(BaseReceiptParser):
    """
    Universal receipt parser using aigateway API gateway.
    Supports: gemini, GPT, Gemini, and other vision models.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: str = None):
        """
        Initialize AIGateway AI parser
        
        Args:
            model_name: Model to use (gemini-2.5-flash, gpt-5.5, gemini-2.5-flash, etc.)
            api_key: AIGateway API key (if None, will try to get from command)
        """
        super().__init__(model_name)
        
        # Load environment variables
        load_dotenv()
        
        # API configuration - prioritize environment variable
        self.api_base = os.getenv("aigateway_API_BASE")
        if not self.api_base:
            self.api_base = "http://localhost:1430/v1"  # Fallback default
            
        self.api_key = api_key or self._get_api_key()
        self.model_name = model_name
        
        if not self.api_key:
            print("Warning: No AIGateway API key found!")
            print("Run: aigateway apikey")
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from aigateway command or environment"""
        # Try environment variable first
        api_key = os.getenv("aigateway_API_KEY")
        if api_key:
            return api_key
        
        # Try to get from aigateway command
        try:
            import subprocess
            result = subprocess.run(
                ["aigateway", "apikey"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
        
    def load_model(self) -> None:
        """
        No model loading needed for API-based parser.
        Just verify API connection.
        """
        if not self.api_key:
            raise ValueError("AIGateway API key not found!")
        
        self.is_loaded = True
        print(f"AIGateway AI parser ready (model: {self.model_name})")
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Parse receipt image using AIGateway AI API.
        
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
            image_base64 = self._image_to_base64(image)
            
            # Create prompt
            prompt = self._create_prompt()
            
            # Prepare request based on model type
            # Note: geminiapi.jtdev.my.id only supports 0penAI format
            response = self._call_openai_format(prompt, image_base64)
            
            # Parse response
            result = self._parse_response(response)
            
            inference_time = time.time() - start_time
            result["inference_time"] = inference_time
            result["model_name"] = self.model_name
            result["raw_output"] = response
            
            print(f"AIGateway AI ({self.model_name}) completed in {inference_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"Error during AIGateway AI inference: {str(e)}")
            raise
    
    def _call_openai_format(self, prompt: str, image_base64: str) -> str:
        """Call API using 0penAI format"""
        url = f"{self.api_base}/chat/completions"
        
        # Try with Authorization Bearer header
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
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
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            # If Bearer fails, try with x-api-key
            if e.response.status_code == 401:
                print("Bearer auth failed, trying x-api-key...")
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key
                }
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            raise
    
    def _call_gemini_format(self, prompt: str, image_base64: str) -> str:
        """Call API using Anthropic/gemini format"""
        url = f"{self.api_base}/messages"
        
        # Try different header formats
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data["content"][0]["text"]
            
        except requests.exceptions.HTTPError as e:
            # If Anthropic format fails, try OpenAI format
            if e.response.status_code == 401:
                print("Anthropic format failed, trying OpenAI format...")
                return self._call_openai_format(prompt, image_base64)
            raise
    
    def _create_prompt(self) -> str:
        """Create prompt for receipt extraction"""
        return """Analyze this receipt image and extract the following information in JSON format:

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

IMPORTANT INSTRUCTIONS:
1. Extract ALL items with names, quantities, unit prices, and totals
2. Calculate subtotal (sum of all item totals BEFORE any charges)
3. Extract additional charges (tax, service, delivery) - ONLY charges that ADD to total
4. Do NOT include discounts as additional charges
5. Extract final total amount
6. Use numbers only (no currency symbols like Rp, $)
7. If quantity not shown, assume 1
8. For Indonesian receipts: convert "Rp" amounts to plain numbers
9. Return ONLY valid JSON, no markdown, no explanation

Be precise and accurate. Double-check all numbers match the receipt."""
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse API response to extract JSON"""
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
            
            # Find JSON in response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Validate and fill missing fields
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
                print(f"Warning: No JSON found in response")
                print(f"Raw response: {content[:200]}...")
                
                # Return empty structure instead of raising error
                return {
                    "items": [],
                    "subtotal": 0.0,
                    "additional_charges": [],
                    "total": 0.0,
                    "error": "No JSON found in response",
                    "raw_response": content
                }
                
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON: {str(e)}")
            print(f"Raw response: {content}")
            
            return {
                "items": [],
                "subtotal": 0.0,
                "additional_charges": [],
                "total": 0.0,
                "error": "Failed to parse response",
                "raw_response": content
            }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information"""
        info = super().get_model_info()
        info["model_type"] = f"AIGateway AI ({self.model_name})"
        info["api_based"] = "Yes"
        info["api_gateway"] = self.api_base
        info["requires_internet"] = "Yes (local gateway)"
        return info


# Test function
def test_aigateway_parser():
    """Test AIGateway AI parser"""
    print("=" * 60)
    print("Testing AIGateway AI Parser")
    print("=" * 60)
    
    # Test with different models
    models = [
        "gemini-2.5-flash",
        "gemini-3.1-pro",
        "gpt-5.5",
        "gemini-2.5-flash"
    ]
    
    print("\nAvailable models:")
    for model in models:
        print(f"  - {model}")
    
    # Initialize with default model
    model = "gemini-2.5-flash"
    print(f"\nTesting with: {model}")
    
    try:
        parser = aigatewayParser(model_name=model)
        parser.load_model()
        
        info = parser.get_model_info()
        print("\nModel Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\nParser ready!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure:")
        print("1. aigateway is running (aigateway serve)")
        print("2. API key is available (aigateway apikey)")


if __name__ == "__main__":
    test_aigateway_parser()
