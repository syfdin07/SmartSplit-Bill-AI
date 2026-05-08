"""
Donut Receipt Parser
Implementation of receipt parsing using Donut model
"""

import time
from typing import Dict, Any, List
from PIL import Image
import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel
import re
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser


class DonutReceiptParser(BaseReceiptParser):
    """
    Receipt parser using Donut (Document Understanding Transformer) model.
    Pre-trained on CORD dataset for receipt understanding.
    """
    
    def __init__(self, model_name: str = "naver-clova-ix/donut-base-finetuned-cord-v2"):
        """
        Initialize Donut parser
        
        Args:
            model_name: Hugging Face model identifier
        """
        super().__init__(model_name)
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self) -> None:
        """
        Load Donut model and processor from Hugging Face.
        This will download the model on first run (~500MB).
        """
        print(f"Loading Donut model: {self.model_name}")
        print(f"Using device: {self.device}")
        
        try:
            # Load processor and model
            self.processor = DonutProcessor.from_pretrained(self.model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            print("✅ Donut model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading Donut model: {str(e)}")
            raise
    
    def parse_receipt(self, image: Image.Image) -> Dict[str, Any]:
        """
        Parse receipt image using Donut model.
        
        Args:
            image: PIL Image object of the receipt
            
        Returns:
            Dictionary containing parsed receipt data
        """
        if not self.is_loaded:
            self.load_model()
        
        start_time = time.time()
        
        try:
            # Prepare image
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generate output
            task_prompt = "<s_cord-v2>"
            decoder_input_ids = self.processor.tokenizer(
                task_prompt, 
                add_special_tokens=False, 
                return_tensors="pt"
            ).input_ids
            decoder_input_ids = decoder_input_ids.to(self.device)
            
            # Run inference
            outputs = self.model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=self.model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
            
            # Decode output
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(
                self.processor.tokenizer.pad_token, ""
            )
            sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()
            
            # Parse JSON output
            try:
                parsed_json = json.loads(sequence)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract manually
                parsed_json = self._extract_manual(sequence)
            
            # Convert to our standard format
            result = self._convert_to_standard_format(parsed_json)
            
            inference_time = time.time() - start_time
            result["inference_time"] = inference_time
            result["raw_output"] = sequence
            
            print(f"✅ Donut inference completed in {inference_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during Donut inference: {str(e)}")
            raise
    
    def _extract_manual(self, text: str) -> Dict[str, Any]:
        """
        Manual extraction if JSON parsing fails.
        
        Args:
            text: Raw text output from model
            
        Returns:
            Dictionary with extracted data
        """
        # This is a fallback method
        # Try to extract key information using regex
        result = {
            "menu": [],
            "total": {}
        }
        
        # Try to find total
        total_match = re.search(r'total["\s:]+(\d+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            result["total"]["total_price"] = total_match.group(1)
        
        return result
    
    def _convert_to_standard_format(self, donut_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Donut output format to our standard format.
        
        Args:
            donut_output: Raw output from Donut model
            
        Returns:
            Standardized receipt data
        """
        items = []
        subtotal = 0.0
        additional_charges = []
        total = 0.0
        
        # Extract menu items
        if "menu" in donut_output:
            for item in donut_output["menu"]:
                try:
                    name = item.get("nm", "Unknown Item")
                    quantity = int(item.get("cnt", 1))
                    price = float(item.get("unitprice", 0))
                    item_total = float(item.get("price", price * quantity))
                    
                    items.append({
                        "name": name,
                        "quantity": quantity,
                        "price": price,
                        "total": item_total
                    })
                    
                    subtotal += item_total
                    
                except (ValueError, KeyError) as e:
                    print(f"⚠️ Warning: Could not parse item: {item}")
                    continue
        
        # Extract total information
        if "total" in donut_output:
            total_info = donut_output["total"]
            
            # Get total price
            if "total_price" in total_info:
                try:
                    total = float(total_info["total_price"])
                except ValueError:
                    total = subtotal
            
            # Extract additional charges (tax, service, etc.)
            if "service_price" in total_info:
                try:
                    service = float(total_info["service_price"])
                    if service > 0:
                        additional_charges.append({
                            "name": "Service Charge",
                            "amount": service
                        })
                except ValueError:
                    pass
            
            if "tax_price" in total_info:
                try:
                    tax = float(total_info["tax_price"])
                    if tax > 0:
                        additional_charges.append({
                            "name": "Tax",
                            "amount": tax
                        })
                except ValueError:
                    pass
        
        # If total is 0, calculate from subtotal + charges
        if total == 0:
            total = subtotal + sum(charge["amount"] for charge in additional_charges)
        
        # If subtotal is 0 but we have items, calculate it
        if subtotal == 0 and items:
            subtotal = sum(item["total"] for item in items)
        
        return {
            "items": items,
            "subtotal": subtotal,
            "additional_charges": additional_charges,
            "total": total,
            "model_name": self.model_name,
            "device": self.device
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the Donut model.
        
        Returns:
            Dictionary with model information
        """
        info = super().get_model_info()
        info["device"] = self.device
        info["model_type"] = "Donut (Document Understanding Transformer)"
        info["pretrained_on"] = "CORD dataset (receipts)"
        return info


# Test function
def test_donut_parser():
    """Test function for Donut parser"""
    print("=" * 50)
    print("Testing Donut Receipt Parser")
    print("=" * 50)
    
    # Initialize parser
    parser = DonutReceiptParser()
    
    # Load model
    parser.load_model()
    
    # Get model info
    info = parser.get_model_info()
    print("\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Donut parser test completed!")
    print("Ready to parse receipts.")


if __name__ == "__main__":
    test_donut_parser()
