from typing import Dict, Any, List
from pydantic import BaseModel
from ..prompt.prompt_manager import PromptManager

class Intent(BaseModel):
    category: str
    confidence: float
    parameters: Dict[str, Any]
    required_tools: List[str]

class IntentAnalyzer:
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager
        self.intent_categories = [
            "data_analysis",
            "visualization",
            "model_training",
            "tool_operation",
            "information_query"
        ]
    
    async def analyze_intent(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Intent:
        prompt = self.prompt_manager.get_prompt(
            "intent_analysis",
            {
                "query": query,
                "intent_categories": ", ".join(self.intent_categories)
            }
        )
        
        # 这里应该调用LLM进行意图分析
        # 返回示例意图
        return Intent(
            category="data_analysis",
            confidence=0.9,
            parameters={"data_type": "numerical", "operation": "statistical"},
            required_tools=["pandas", "numpy"]
        ) 