from typing import Dict, TypedDict

class ModelConfig(TypedDict):
    context_length: int
    temperature: float

# 默认模型配置
DEFAULT_MODEL_CONFIGS: Dict[str, ModelConfig] = {
    "llama3": {
        "context_length": 4096,
        "temperature": 0.7
    },
    "deepseek-r1": {
        "context_length": 8192,
        "temperature": 0.7
    }
} 