import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def check_matlab_server(self):
        """Check if MATLAB server is running"""
        try:
            async with self.session.get("http://localhost:8001/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"MATLAB server check failed: {str(e)}")
            return False
            
    async def create_domain(self):
        """Create signal processing domain"""
        data = {
            "name": "Signal Processing",
            "description": "Professional domain for signal processing and analysis"
        }
        async with self.session.post(f"{self.base_url}/domains", json=data) as response:
            result = await response.json()
            logger.info(f"Create domain result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
            
    async def register_service(self):
        """Register MATLAB service"""
        data = {
            "domain_name": "Signal Processing",
            "service_name": "matlab",
            "description": "MATLAB Signal Processing Service",
            "endpoint_url": "http://localhost:8001",
            "service_type": "matlab",
            "methods": {
                "filter": {
                    "description": "Apply digital filter",
                    "parameters": {
                        "x": "Input signal",
                        "b": "Filter coefficient b",
                        "a": "Filter coefficient a"
                    }
                },
                "fft": {
                    "description": "Calculate Fast Fourier Transform",
                    "parameters": {
                        "data": "Input data"
                    }
                }
            }
        }
        async with self.session.post(f"{self.base_url}/services/register", json=data) as response:
            result = await response.json()
            logger.info(f"Register service result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
            
    async def upload_document(self, domain_id: int):
        """Upload domain document"""
        # Create example document
        doc_content = """
Digital Filter Basics:

1. Low-pass Filter
- Purpose: Remove high-frequency noise, preserve low-frequency signals
- Applications: Data smoothing, noise removal
- Parameter settings:
  * Cutoff frequency: Determines the filter's cutoff point
  * Order: Affects the filter's steepness

2. High-pass Filter
- Purpose: Remove low-frequency interference, preserve high-frequency signals
- Applications: Edge detection, transient detection
- Parameter settings: Same as low-pass filter

3. Practical Application Examples
- ECG signal processing: Use bandpass filter to extract ECG signals in specific frequency ranges
- Audio processing: Use low-pass filter to remove high-frequency noise
- Image processing: Use high-pass filter for edge enhancement
"""
        doc_path = Path("temp_doc.txt")
        doc_path.write_text(doc_content, encoding='utf-8')
        
        data = aiohttp.FormData()
        data.add_field('file', 
                      open(doc_path, 'rb'),
                      filename='filter_concepts.txt',
                      content_type='text/plain')
        data.add_field('domain_id', str(domain_id))
        
        async with self.session.post(f"{self.base_url}/documents/upload", data=data) as response:
            result = await response.json()
            logger.info(f"Upload document result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        # Clean up temporary file
        doc_path.unlink()
        return result
        
    async def execute_query(self, query: str):
        """Execute query"""
        data = {
            "query": query,
            "domain_name": "Signal Processing"
        }
        async with self.session.post(f"{self.base_url}/llm/execute", json=data) as response:
            result = await response.json()
            logger.info(f"Execute query result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result

async def run_demo():
    """Run demonstration"""
    logger.info("Starting demonstration...")
    
    async with DemoClient() as client:
        # 1. Check MATLAB server
        logger.info("Checking MATLAB server...")
        if not await client.check_matlab_server():
            logger.error("MATLAB server is not running, please start the server first")
            return
        logger.info("MATLAB server is running normally")
        
        # 2. Create domain
        logger.info("\nCreating signal processing domain...")
        domain_result = await client.create_domain()
        domain_id = domain_result.get("domain_id")
        
        # 3. Register service
        logger.info("\nRegistering MATLAB service...")
        await client.register_service()
        
        # 4. Upload document
        logger.info("\nUploading domain document...")
        await client.upload_document(domain_id)
        
        # 5. Execute query examples
        logger.info("\nExecuting query examples...")
        queries = [
            "How to use a low-pass filter to remove noise from a signal?",
            "Perform Fourier transform on signal [1,2,3,4,5]",
            "Design a bandpass filter for ECG signal processing"
        ]
        
        for query in queries:
            logger.info(f"\nExecuting query: {query}")
            await client.execute_query(query)
            await asyncio.sleep(2)  # Wait a bit to avoid too frequent requests
            
        logger.info("\nDemonstration completed!")

if __name__ == "__main__":
    asyncio.run(run_demo()) 