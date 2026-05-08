"""
Test AIGateway AI with actual image
"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image
from models.aigateway_parser import aigatewayParser

# Create a simple test image with text
print("Creating test image...")
img = Image.new('RGB', (400, 200), color='white')

# Initialize parser
print("Initializing parser...")
parser = aigatewayParser()
parser.load_model()

print(f"\nAPI Base: {parser.api_base}")
print(f"Model: {parser.model_name}")

# Test parsing
print("\nTesting with simple image...")
try:
    result = parser.parse_receipt(img)
    
    print("\nResult:")
    print(f"  Items: {len(result.get('items', []))}")
    print(f"  Total: ${result.get('total', 0):.2f}")
    print(f"  Inference time: {result.get('inference_time', 0):.2f}s")
    
    if result.get('items'):
        print("\n  Items detail:")
        for item in result['items']:
            print(f"    - {item.get('name', 'Unknown')}: ${item.get('total', 0):.2f}")
    
    print("\nSUCCESS! Parser is working!")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
