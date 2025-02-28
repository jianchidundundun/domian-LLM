from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from .document_store import BaseDocumentStore, Document
from sentence_transformers import SentenceTransformer
import os

class FAISSDocumentStore(BaseDocumentStore):
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        index_type: str = "l2",
        cache_dir: Optional[str] = None
    ):
        # 设置模型缓存目录
        if cache_dir:
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
        
        try:
            # 尝试离线加载
            self.embedding_model = SentenceTransformer(
                embedding_model,
                device='cpu',  # 默认使用CPU
                cache_folder=cache_dir
            )
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            # 使用备用的小型模型
            self.embedding_model = SentenceTransformer(
                'paraphrase-MiniLM-L3-v2',
                device='cpu'
            )
        
        self.dimension = dimension
        
        # 初始化FAISS索引
        if index_type == "l2":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "ip":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            raise ValueError(f"不支持的索引类型: {index_type}")
            
        # 存储文档和ID映射
        self.documents: List[Document] = []
        self.doc_ids: Dict[int, int] = {}  # 文档ID到索引位置的映射
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """获取文本的嵌入向量"""
        return self.embedding_model.encode(text, convert_to_tensor=False)
        
    async def add_documents(self, documents: List[Document]) -> None:
        """添加文档到存储"""
        if not documents:
            return
            
        # 生成文档嵌入
        embeddings = []
        for doc in documents:
            if doc.embedding is None:
                embedding = self._get_embedding(doc.content)
                doc.embedding = embedding.tolist()
            embeddings.append(np.array(doc.embedding))
            
        embeddings_array = np.array(embeddings).astype('float32')
        
        # 添加到FAISS索引
        start_id = len(self.documents)
        self.index.add(embeddings_array)
        
        # 更新文档存储和ID映射
        for i, doc in enumerate(documents):
            doc_id = start_id + i
            self.doc_ids[doc_id] = len(self.documents)
            self.documents.append(doc)
            
    async def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Document]:
        """搜索相似文档"""
        # 获取查询的嵌入向量
        query_embedding = self._get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # 执行相似度搜索
        distances, indices = self.index.search(query_embedding, top_k)
        
        # 获取结果文档
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and distances[0][i] < threshold:
                results.append(self.documents[self.doc_ids[idx]])
                
        return results
        
    async def delete_documents(self, filter: Dict[str, Any]) -> None:
        """删除文档（注意：FAISS不支持直接删除，这里只是从文档列表中移除）"""
        # 找到要删除的文档
        docs_to_keep = []
        embeddings_to_keep = []
        
        for i, doc in enumerate(self.documents):
            if not all(doc.metadata.get(k) == v for k, v in filter.items()):
                docs_to_keep.append(doc)
                embeddings_to_keep.append(np.array(doc.embedding))
                
        # 重建索引
        if len(docs_to_keep) < len(self.documents):
            self.documents = docs_to_keep
            self.doc_ids = {i: i for i in range(len(docs_to_keep))}
            
            if index_type == "l2":
                self.index = faiss.IndexFlatL2(self.dimension)
            else:
                self.index = faiss.IndexFlatIP(self.dimension)
                
            if embeddings_to_keep:
                embeddings_array = np.array(embeddings_to_keep).astype('float32')
                self.index.add(embeddings_array)

    def save_index(self, file_path: str) -> None:
        """保存FAISS索引到文件"""
        faiss.write_index(self.index, file_path)
        
    def load_index(self, file_path: str) -> None:
        """从文件加载FAISS索引"""
        self.index = faiss.read_index(file_path) 