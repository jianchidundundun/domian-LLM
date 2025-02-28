from typing import List, Dict, Any, Optional
from .document_store import BaseDocumentStore, Document
import os
import json

async def load_documents(
    document_store: BaseDocumentStore,
    docs_dir: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """从目录加载文档"""
    documents = []
    
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(('.txt', '.md', '.json')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                doc_metadata = {
                    "source": file_path,
                    "type": file.split('.')[-1],
                    **(metadata or {})
                }
                
                document = Document(
                    content=content,
                    metadata=doc_metadata,
                    embedding=None  # 将由文档存储生成
                )
                documents.append(document)
                
    await document_store.add_documents(documents) 