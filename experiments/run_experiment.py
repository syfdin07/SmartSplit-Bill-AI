"""
Receipt Parser Experiment Script
Compare Donut and GPT-4 Vision models for receipt parsing
"""

import sys
from pathlib import Path
import time
from PIL import Image
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.donut_parser import DonutReceiptParser
from models.gpt4_vision_parser import GPT4VisionParser


def print_separator(title=""):
    """Print a separator line"""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
    else:
        print('-' * 60)


def print_receipt_data(data: dict, model_name: str):
    """Pretty print receipt data"""
    print(f"\n📊 Results from {model_name}:")
    print_separator()
    
    # Items
    print("\n🛒 Items:")
    if data.get("items"):
        for idx, item in enumerate(data["items"], 1):
            print(f"  {idx}. {item['name']}")
            print(f"     Qty: {item['quantity']} x ${item['price']:.2f} = ${item['total']:.2f}")
    else:
        print("  No items found")
    
    # Subtotal
    print(f"\n💵 Subtotal: ${data.get('subtotal', 0):.2f}")
    
    # Additional charges
    if data.get("additional_charges"):
        print("\n📝 Additional Charges:")
        for charge in data["additional_charges"]:
            print(f"  - {charge['name']}: ${charge['amount']:.2f}")
    
    # Total
    print(f"\n💰 Total: ${data.get('total', 0):.2f}")
    
    # Performance
    if "inference_time" in data:
        print(f"\n⏱️  Inference Time: {data['inference_time']:.2f}s")
    
    print_separator()


def compare_results(donut_result: dict, gpt4_result: dict):
    """Compare results from both models"""
    print_separator("COMPARISON")
    
    print("\n📊 Accuracy Comparison:")
    print(f"  Donut - Items found: {len(donut_result.get('items', []))}")
    print(f"  GPT-4 - Items found: {len(gpt4_result.get('items', []))}")
    
    print(f"\n  Donut - Total: ${donut_result.get('total', 0):.2f}")
    print(f"  GPT-4 - Total: ${gpt4_result.get('total', 0):.2f}")
    
    print("\n⏱️  Speed Comparison:")
    donut_time = donut_result.get('inference_time', 0)
    gpt4_time = gpt4_result.get('inference_time', 0)
    print(f"  Donut: {donut_time:.2f}s")
    print(f"  GPT-4: {gpt4_time:.2f}s")
    
    if donut_time > 0 and gpt4_time > 0:
        if donut_time < gpt4_time:
            print(f"  ✅ Donut is {gpt4_time/donut_time:.2f}x faster")
        else:
            print(f"  ✅ GPT-4 is {donut_time/gpt4_time:.2f}x faster")
    
    print_separator()


def save_results(receipt_name: str, donut_result: dict, gpt4_result: dict):
    """Save experiment results to JSON file"""
    results = {
        "receipt_name": receipt_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "donut": donut_result,
        "gpt4_vision": gpt4_result
    }
    
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{receipt_name}_results.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")


def run_experiment(image_path: str, receipt_name: str, use_donut: bool = True, use_gpt4: bool = True):
    """
    Run experiment with both models on a receipt image
    
    Args:
        image_path: Path to receipt image
        receipt_name: Name identifier for the receipt
        use_donut: Whether to test Donut model
        use_gpt4: Whether to test GPT-4 Vision
    """
    print_separator(f"EXPERIMENT: {receipt_name}")
    
    # Load image
    print(f"\n📸 Loading image: {image_path}")
    try:
        image = Image.open(image_path)
        print(f"✅ Image loaded: {image.size[0]}x{image.size[1]} pixels")
    except Exception as e:
        print(f"❌ Error loading image: {str(e)}")
        return
    
    donut_result = None
    gpt4_result = None
    
    # Test Donut
    if use_donut:
        print_separator("Testing Donut Model")
        try:
            donut_parser = DonutReceiptParser()
            donut_parser.load_model()
            donut_result = donut_parser.parse_receipt(image)
            print_receipt_data(donut_result, "Donut")
        except Exception as e:
            print(f"❌ Donut error: {str(e)}")
            donut_result = {"error": str(e)}
    
    # Test GPT-4 Vision
    if use_gpt4:
        print_separator("Testing GPT-4 Vision Model")
        try:
            gpt4_parser = GPT4VisionParser()
            gpt4_parser.load_model()
            gpt4_result = gpt4_parser.parse_receipt(image)
            print_receipt_data(gpt4_result, "GPT-4 Vision")
        except Exception as e:
            print(f"❌ GPT-4 Vision error: {str(e)}")
            gpt4_result = {"error": str(e)}
    
    # Compare results
    if donut_result and gpt4_result and "error" not in donut_result and "error" not in gpt4_result:
        compare_results(donut_result, gpt4_result)
    
    # Save results
    if donut_result or gpt4_result:
        save_results(receipt_name, donut_result or {}, gpt4_result or {})
    
    print("\n✅ Experiment completed!")


def main():
    """Main experiment runner"""
    print_separator("RECEIPT PARSER EXPERIMENT")
    print("\nThis script will test both Donut and GPT-4 Vision models")
    print("on receipt images and compare their performance.")
    
    # Check for sample receipts
    data_dir = Path(__file__).parent.parent / "data"
    
    print(f"\n📁 Looking for receipts in: {data_dir}")
    
    if not data_dir.exists():
        print("⚠️  Data directory not found. Creating it...")
        data_dir.mkdir(exist_ok=True)
    
    # Find receipt images
    receipt_files = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.png")) + list(data_dir.glob("*.jpeg"))
    
    if not receipt_files:
        print("\n⚠️  No receipt images found in data/ directory!")
        print("\nTo run experiments:")
        print("1. Add receipt images to the data/ directory")
        print("2. Supported formats: .jpg, .jpeg, .png")
        print("3. Run this script again")
        return
    
    print(f"\n✅ Found {len(receipt_files)} receipt image(s):")
    for idx, file in enumerate(receipt_files, 1):
        print(f"  {idx}. {file.name}")
    
    # Ask user which models to use
    print("\n" + "=" * 60)
    print("Which models do you want to test?")
    print("1. Donut only")
    print("2. GPT-4 Vision only")
    print("3. Both models (recommended)")
    
    choice = input("\nEnter choice (1-3) [default: 3]: ").strip() or "3"
    
    use_donut = choice in ["1", "3"]
    use_gpt4 = choice in ["2", "3"]
    
    # Run experiments
    for idx, receipt_file in enumerate(receipt_files, 1):
        receipt_name = receipt_file.stem
        
        print(f"\n\n{'#' * 60}")
        print(f"# Receipt {idx}/{len(receipt_files)}: {receipt_name}")
        print('#' * 60)
        
        run_experiment(
            str(receipt_file),
            receipt_name,
            use_donut=use_donut,
            use_gpt4=use_gpt4
        )
        
        # Pause between receipts if multiple
        if idx < len(receipt_files):
            input("\nPress Enter to continue to next receipt...")
    
    print_separator("ALL EXPERIMENTS COMPLETED")
    print("\n✅ Check the experiments/results/ directory for detailed JSON results")


if __name__ == "__main__":
    main()
