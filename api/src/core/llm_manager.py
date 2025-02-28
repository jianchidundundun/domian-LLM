from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import os
from src.core.providers.base_provider import BaseLLMProvider
from src.core.providers.openai_provider import OpenAIProvider
from src.core.providers.ollama_provider import OllamaProvider
from .rag.faiss_document_store import FAISSDocumentStore
from .rag.rag_manager import RAGManager
from .prompt.prompt_manager import PromptManager
from .context.context_manager import ContextManager
from .intent.intent_analyzer import IntentAnalyzer
import logging
import json

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        load_dotenv()
        self.providers: Dict[str, BaseLLMProvider] = {}
        
        # Initialize OpenAI provider
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.providers["openai"] = OpenAIProvider(openai_api_key)
            
        # Initialize Ollama provider
        self.providers["ollama"] = OllamaProvider()
        
        # Set default provider
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        
        # Initialize components
        self.document_store = FAISSDocumentStore(
            embedding_model="paraphrase-MiniLM-L3-v2",
            dimension=384,
            index_type="l2"
        )
        self.prompt_manager = PromptManager()
        self.context_manager = ContextManager()
        self.intent_analyzer = IntentAnalyzer(self.prompt_manager)
        self.rag_manager = RAGManager(
            self.document_store,
            self.prompt_manager,
            self.context_manager
        )
        
    async def process_query(
        self,
        query: str,
        session_id: str,
        domain: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 1. Analyze intent
        intent = await self.intent_analyzer.analyze_intent(query, context or {})
        
        # 2. Process query using RAG
        response = await self.rag_manager.process_query(
            query,
            session_id,
            domain
        )
        
        return {
            "response": response,
            "intent": intent.dict(),
            "context": self.context_manager.get_context(session_id)
        }
            
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        try:
            # Use specified provider or default provider
            provider_name = provider or self.default_provider
            llm_provider = self.providers.get(provider_name)
            
            if not llm_provider:
                raise ValueError(f"Provider {provider_name} not found")
            
            # Call provider's chat method
            response = await llm_provider.chat(messages, context, **kwargs)
            
            if not response:
                raise ValueError("Empty response from LLM provider")
            
            return response
        
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise
            
    async def generate_execution_plan(
        self,
        query: str,
        services: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> Dict:
        """Generate execution plan"""
        try:
            # Build system prompt
            system_prompt = """You are a professional execution plan generator. Your task is to generate an execution plan based on user queries and available services.
You must and can only return a valid JSON object, do not include any other explanations or comments.
The JSON object must strictly follow this format:
{
    "plan": [
        {
            "service": "service name",
            "method": "method name",
            "parameters": {
                "parameter name": "parameter value"
            },
            "description": "step description"
        }
    ]
}
Note:
1. All strings must use double quotes
2. Do not add comments in JSON
3. Do not add any extra explanatory text
4. Ensure the JSON object is complete and correctly formatted"""

            # Build user prompt
            services_info = json.dumps(services, indent=2, ensure_ascii=False)
            context_info = f"\nContext information:\n{context}" if context else ""
            user_prompt = f"""Query: {query}

Available services:
{services_info}
{context_info}

Please generate an execution plan. Remember:
1. Only return JSON object
2. Only use listed services and methods
3. Parameters must match method definitions
4. Do not add any explanations or comments"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Get response
            response = await self.chat(messages)
            
            # Try to parse JSON
            try:
                if isinstance(response, str):
                    # Clean response text, keep only JSON part
                    response = response.strip()
                    # Extract JSON part
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start == -1 or end == 0:
                        raise ValueError("No valid JSON structure found in response")
                    json_str = response[start:end]
                    
                    plan_data = json.loads(json_str)
                else:
                    plan_data = response
                    
                # Validate plan format
                if not isinstance(plan_data, dict):
                    plan_data = {"plan": [plan_data]}
                elif "plan" not in plan_data:
                    if any(key in plan_data for key in ["service", "method", "parameters"]):
                        plan_data = {"plan": [plan_data]}
                    else:
                        raise ValueError("Execution plan must contain 'plan' field")
                
                if not isinstance(plan_data["plan"], list):
                    plan_data["plan"] = [plan_data["plan"]]
                
                # Validate each step
                for step in plan_data["plan"]:
                    required_fields = ["service", "method", "parameters"]
                    missing_fields = [f for f in required_fields if f not in step]
                    if missing_fields:
                        raise ValueError(f"Step missing required fields: {', '.join(missing_fields)}")
                    
                    # Validate if service and method exist
                    service_names = [s["name"] for s in services]
                    if step["service"] not in service_names:
                        raise ValueError(f"Unknown service: {step['service']}")
                    
                    service = next(s for s in services if s["name"] == step["service"])
                    if step["method"] not in service.get("methods", {}):
                        raise ValueError(f"Service {step['service']} does not support method: {step['method']}")
                
                return plan_data
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}\nOriginal response: {response}")
                raise ValueError("Generated response is not valid JSON format")
            except Exception as e:
                logger.error(f"Execution plan generation failed: {str(e)}\nOriginal response: {response}")
                raise ValueError(f"Execution plan generation failed: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to generate execution plan: {str(e)}")
            raise 