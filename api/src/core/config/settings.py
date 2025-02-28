import os
from pathlib import Path
import yaml
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.config_dir = self.base_dir / "config"
        self.load_config()

    def load_config(self):
        # 加载默认配置
        self.config = {
            "llm": {
                "providers": {
                    "ollama": {
                        "base_url": "http://localhost:11434",
                        "default_model": "llama3",
                        "models": {}  # 将从 yaml 文件加载
                    },
                    "openai": {
                        "api_key": None,  # 将从环境变量加载
                        "default_model": "gpt-3.5-turbo"
                    }
                }
            }
        }

        # 加载自定义配置
        config_file = self.config_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                custom_config = yaml.safe_load(f)
                if custom_config:
                    self._merge_config(self.config, custom_config)

        # 从环境变量加载配置
        self._load_from_env()

    def _merge_config(self, base: Dict, update: Dict):
        """递归合并配置字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _load_from_env(self):
        """从环境变量加载配置"""
        env_mappings = {
            "OLLAMA_API_URL": ("llm.providers.ollama.base_url", str),
            "OLLAMA_DEFAULT_MODEL": ("llm.providers.ollama.default_model", str),
            "OPENAI_API_KEY": ("llm.providers.openai.api_key", str),
        }

        for env_key, (config_path, type_cast) in env_mappings.items():
            if env_value := os.getenv(env_key):
                self._set_nested(self.config, config_path.split("."), type_cast(env_value))

    def _set_nested(self, d: Dict, keys: list, value: Any):
        """设置嵌套字典的值"""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(k, default)
            if value is None:
                return default
        return value

settings = Settings() 