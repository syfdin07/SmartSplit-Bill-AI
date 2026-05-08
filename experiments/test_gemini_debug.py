"""
Debug script to test Gemini Vision with actual image
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PIL import Image
from models.gemini_vision_parser import GeminiVisionParser
import json

def test_with_image(image_path: str):
    """Test Gemini Vision with actual image"""
    
    print("=" * 60)
    print("Testing Gemini Vision with Real Image")
    print("=" * 60)
    
    # Load image
    print(f"\n1. Loading image: {image_path}")
    try:
        image = Image.open(image_path)
        print(f"   Image size: {image.size[0]}x{image.size[1]}")
        print(f"   Image mode: {image.mode}")
    except Exception as e:
        print(f"   Error loading image: {e}")
        return
    
    # Initialize parser
    print("\n2. Initializing Gemini Vision parser...")
    try:
        parser = GeminiVisionParser()
        parser.load_model()
        print("   Parser initialized successfully")
    except Exception as e:
        print(f"   Error initializing parser: {e}")
        return
    
    # Parse receipt
    print("\n3. Parsing receipt...")
    try:
        result = parser.parse_receipt(image)
        
        print("\n4. Results:")
        print(f"   Model: {result.get('model_name', 'Unknown')}")
        print(f"   Inference time: {result.get('inference_time', 0):.2f}s")
        print(f"   Items found: {len(result.get('items', []))}")
        
        print("\n5. Extracted Data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n6. Items Detail:")
        for idx, item in enumerate(result.get('items', []), 1):
            print(f"   {idx}. {item.get('name', 'Unknown')}")
            print(f"      Qty: {item.get('quantity', 0)} x ${item.get('price', 0):.2f} = ${item.get('total', 0):.2f}")
        
        print(f"\n7. Summary:")
        print(f"   Subtotal: ${result.get('subtotal', 0):.2f}")
        print(f"   Additional charges: {len(result.get('additional_charges', []))}")
        print(f"   Total: ${result.get('total', 0):.2f}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"   Error parsing receipt: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_gemini_debug.py <image_path>")
        print("\nExample:")
        print("  python experiments/test_gemini_debug.py data/receipt1.jpg")
    else:
        image_path = sys.argv[1]
        test_with_image(image_path)
