"""
Model Manager
Factory pattern for managing different receipt parser models
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.base_parser import BaseReceiptParser
from models.donut_parser import DonutReceiptParser
from models.gpt4_vision_parser import GPT4VisionParser
from models.gemini_vision_parser import GeminiVisionParser
from models.aigateway_parser import aigatewayParser


class ModelType(Enum):
    """Enum for available model types"""
    DONUT = "donut"
    GPT4_VISION = "gpt4_vision"
    GEMINI_VISION = "gemini_vision"
    aigateway = "aigateway"  # Universal AIGateway AI gateway
    AUTO = "auto"  # Automatically select best available model


class ModelManager:
    """
    Factory class for creating and managing receipt parser models.
    Handles model selection, initialization, and caching.
    """
    
    def __init__(self):
        """Initialize model manager"""
        load_dotenv()
        self._cached_models: Dict[str, BaseReceiptParser] = {}
        self._default_model_type = self._determine_default_model()
    
    def _determine_default_model(self) -> ModelType:
        """
        Determine the best default model based on available resources.
        
        Returns:
            ModelType enum value
        """
        # Check environment variable for model preference
        model_pref = os.getenv("MODEL_TYPE", "").lower()
        
        # Check API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GOOGLE_API_KEY")
        aigateway_key = os.getenv("aigateway_API_KEY")
        
        # If user specified a preference, use it
        if model_pref == "aigateway" or model_pref == "AIGateway":
            return ModelType.aigateway
        elif model_pref == "gpt4_vision" and openai_key:
            return ModelType.GPT4_VISION
        elif model_pref == "gemini_vision" and gemini_key:
            return ModelType.GEMINI_VISION
        elif model_pref == "gemini" and gemini_key:
            return ModelType.GEMINI_VISION
        elif model_pref == "donut":
            return ModelType.DONUT
        elif model_pref == "local":
            return ModelType.DONUT
        
        # Auto-select: prefer AIGateway AI if available, then API models, then local
        if aigateway_key or self._check_aigateway_available():
            return ModelType.aigateway
        elif gemini_key:
            return ModelType.GEMINI_VISION
        elif openai_key:
            return ModelType.GPT4_VISION
        else:
            return ModelType.DONUT
    
    def _check_aigateway_available(self) -> bool:
        """Check if aigateway is available"""
        try:
            import subprocess
            result = subprocess.run(
                ["aigateway", "apikey"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_parser(
        self, 
        model_type: Optional[ModelType] = None,
        use_cache: bool = True
    ) -> BaseReceiptParser:
        """
        Get a receipt parser instance.
        
        Args:
            model_type: Type of model to use (None = use default)
            use_cache: Whether to use cached model instance
            
        Returns:
            BaseReceiptParser instance
            
        Raises:
            ValueError: If model type is invalid or unavailable
        """
        # Use default if not specified
        if model_type is None or model_type == ModelType.AUTO:
            model_type = self._default_model_type
        
        # Check cache
        cache_key = model_type.value
        if use_cache and cache_key in self._cached_models:
            return self._cached_models[cache_key]
        
        # Create new parser instance
        parser = self._create_parser(model_type)
        
        # Cache it
        if use_cache:
            self._cached_models[cache_key] = parser
        
        return parser
    
    def _create_parser(self, model_type: ModelType) -> BaseReceiptParser:
        """
        Create a new parser instance.
        
        Args:
            model_type: Type of model to create
            
        Returns:
            BaseReceiptParser instance
            
        Raises:
            ValueError: If model type is invalid or unavailable
        """
        if model_type == ModelType.DONUT:
            return DonutReceiptParser()
        
        elif model_type == ModelType.GPT4_VISION:
            # Check if API key is available
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GPT-4 Vision requires OPENAI_API_KEY in .env file. "
                    "Either add the API key or use Donut model instead."
                )
            return GPT4VisionParser(api_key=api_key)
        
        elif model_type == ModelType.GEMINI_VISION:
            # Check if API key is available
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Gemini Vision requires GOOGLE_API_KEY in .env file. "
                    "Either add the API key or use Donut model instead."
                )
            return GeminiVisionParser(api_key=api_key)
        
        elif model_type == ModelType.aigateway:
            # Get model name from env or use default
            model_name = os.getenv("aigateway_MODEL", "gemini-2.5-flash")
            return aigatewayParser(model_name=model_name)
        
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available models.
        
        Returns:
            Dictionary with model information
        """
        models = {}
        
        # Donut is always available
        models["donut"] = {
            "name": "Donut",
            "type": ModelType.DONUT.value,
            "available": True,
            "description": "Local OCR-free model, pre-trained on receipts",
            "requires_gpu": False,
            "requires_api_key": False,
            "cost": "Free",
            "speed": "Medium (CPU) / Fast (GPU)"
        }
        
        # GPT-4 Vision requires API key
        openai_key = os.getenv("OPENAI_API_KEY")
        models["gpt4_vision"] = {
            "name": "GPT-4 Vision",
            "type": ModelType.GPT4_VISION.value,
            "available": bool(openai_key),
            "description": "0penAI's multimodal LLM with vision capabilities",
            "requires_gpu": False,
            "requires_api_key": True,
            "cost": "~$0.01-0.03 per image",
            "speed": "Fast (depends on network)"
        }
        
        # Gemini Vision requires API key
        gemini_key = os.getenv("GOOGLE_API_KEY")
        models["gemini_vision"] = {
            "name": "Gemini Vision",
            "type": ModelType.GEMINI_VISION.value,
            "available": bool(gemini_key),
            "description": "Google's multimodal AI with vision capabilities",
            "requires_gpu": False,
            "requires_api_key": True,
            "cost": "Free tier available",
            "speed": "Fast (depends on network)"
        }
        
        return models
    
    def get_default_model_type(self) -> ModelType:
        """
        Get the default model type.
        
        Returns:
            ModelType enum value
        """
        return self._default_model_type
    
    def clear_cache(self) -> None:
        """Clear cached model instances"""
        self._cached_models.clear()
    
    def preload_model(self, model_type: Optional[ModelType] = None) -> None:
        """
        Preload a model to reduce first-inference latency.
        
        Args:
            model_type: Type of model to preload (None = default)
        """
        parser = self.get_parser(model_type=model_type, use_cache=True)
        if not parser.is_loaded:
            parser.load_model()
        print(f"✅ Model preloaded: {parser.model_name}")


# Singleton instance
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """
    Get the singleton ModelManager instance.
    
    Returns:
        ModelManager instance
    """
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance


# Test function
def test_model_manager():
    """Test function for ModelManager"""
    print("=" * 60)
    print("Testing Model Manager")
    print("=" * 60)
    
    manager = get_model_manager()
    
    # Get available models
    print("\n📋 Available Models:")
    models = manager.get_available_models()
    for model_id, info in models.items():
        status = "✅ Available" if info["available"] else "❌ Unavailable"
        print(f"\n{info['name']} ({status})")
        print(f"  Description: {info['description']}")
        print(f"  Cost: {info['cost']}")
        print(f"  Speed: {info['speed']}")
        print(f"  Requires API Key: {info['requires_api_key']}")
    
    # Get default model
    default_type = manager.get_default_model_type()
    print(f"\n🎯 Default Model: {default_type.value}")
    
    # Try to get parser
    print("\n🔧 Getting parser instance...")
    try:
        parser = manager.get_parser()
        print(f"✅ Parser created: {parser.model_name}")
        
        # Get model info
        info = parser.get_model_info()
        print("\nModel Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n✅ Model Manager test completed!")


if __name__ == "__main__":
    test_model_manager()
