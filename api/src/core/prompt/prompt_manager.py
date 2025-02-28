from typing import Dict, Any, List
from pydantic import BaseModel

class PromptTemplate(BaseModel):
    name: str
    template: str
    required_variables: List[str]

class PromptManager:
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        self.templates["domain_expert"] = PromptTemplate(
            name="domain_expert",
            template="""You are an expert in the {domain} domain. Based on the following context:
{context}
Please answer the user's question: {query}""",
            required_variables=["domain", "context", "query"]
        )
        
        self.templates["intent_analysis"] = PromptTemplate(
            name="intent_analysis",
            template="""Analyze the user's intent:
User input: {query}
Possible intent categories: {intent_categories}
Please identify the user's specific intent and required tools.""",
            required_variables=["query", "intent_categories"]
        )
        
        self.templates["signal_processing"] = PromptTemplate(
            name="signal_processing",
            template="""You are a signal processing expert. Based on the following context:
{context}

The user's question is: {query}

Please analyze the problem and provide a solution. If a filter is needed, please explain:
1. What type of filter to choose
2. Why choose this filter
3. Expected effects

If specific API calls are needed, use the following format:
POST /api/v1/signal/filter
{
    "data": [data array],
    "filter_type": "filter type",
    "parameters": {optional parameters}
}
""",
            required_variables=["context", "query"]
        )
    
    def get_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")
            
        template = self.templates[template_name]
        missing_vars = [
            var for var in template.required_variables 
            if var not in variables
        ]
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
            
        return template.template.format(**variables) 