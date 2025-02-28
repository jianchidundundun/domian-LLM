from typing import Dict, Any, Optional, List, TypedDict, cast
import aiohttp
from src.core.providers.base_provider import BaseLLMProvider
from src.core.config.settings import settings

class ModelConfig(TypedDict):
    context_length: int
    temperature: float

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        # Load settings from configuration
        self.base_url = settings.get("llm.providers.ollama.base_url", "http://localhost:11434")
        self.default_model = settings.get("llm.providers.ollama.default_model", "llama3")
        self.available_models = settings.get("llm.providers.ollama.models", {})
        
    def _get_model_config(self, model_name: str) -> ModelConfig:
        """Get model configuration"""
        return self.available_models.get(model_name, self.available_models.get(self.default_model, {
            "context_length": 4096,
            "temperature": 0.7
        }))
        
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        model_name = str(kwargs.get("model", self.default_model))
        model_config = self._get_model_config(model_name)
        
        # Merge default configuration and user configuration
        request_config = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            **model_config,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=request_config
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")
                result = await response.json()
                return cast(str, result["response"])
                
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        # Convert message list to single prompt string
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return await self.generate(prompt, context, **kwargs)

    async def list_models(self) -> List[str]:
        """Get available model list"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")
                result = await response.json()
                return [str(model["name"]) for model in result["models"]] 