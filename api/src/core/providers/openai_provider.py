from typing import Dict, Any, Optional, List, cast
from openai import AsyncOpenAI, OpenAIError
from src.core.providers.base_provider import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, context, **kwargs)
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        try:
            model = kwargs.get("model", "gpt-3.5-turbo")
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            if response.choices and response.choices[0].message:
                return str(response.choices[0].message.content or "")
            return ""
        except Exception as e:
            raise OpenAIError(message=f"OpenAI API错误: {str(e)}")

    async def list_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            return [str(model.id) for model in models.data if model.id]
        except Exception as e:
            raise OpenAIError(message=f"获取模型列表失败: {str(e)}") 