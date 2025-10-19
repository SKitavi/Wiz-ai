import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

class RAGService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="user_context",
            metadata={"description": "User tasks, plans, and preferences"}
        )
        
        logger.info("RAG service initialized with ChromaDB")
    def add_document(
        self,
        user_id: int,
        text: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """Add document to vector database"""
        if not doc_id:
            doc_id = f"user_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Generate embedding
        embedding = self.embedding_model.encode(text).tolist()
        
        # Add to collection
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                **metadata
            }],
            ids=[doc_id]
        )
        
        logger.info(f"Added document {doc_id} for user {user_id}")
        return doc_id
    def query(
        self,
        user_id: int,
        query_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Semantic search for relevant context"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        # Prepare filter (user-specific)
        where_filter = {"user_id": user_id}
        if filter_metadata:
            where_filter.update(filter_metadata)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
# Format results with relevance scores
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]  # Lower is better
            })
        
        logger.info(f"Retrieved {len(formatted_results)} results for user {user_id}")
        return formatted_results
    
    def update_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """Update existing document"""
        embedding = self.embedding_model.encode(text).tolist()
        
        self.collection.update(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        
        logger.info(f"Updated document {doc_id}")
    
    def delete_document(self, doc_id: str):
        """Remove document from vector DB"""
        self.collection.delete(ids=[doc_id])
        logger.info(f"Deleted document {doc_id}")
    def add_task_to_context(self, user_id: int, task: Dict[str, Any]):
        """Add task to user's context"""
        text = f"Task: {task['title']}. Deadline: {task['deadline']}. Course: {task.get('course', 'N/A')}. Description: {task.get('description', '')}"
        metadata = {
            "type": "task",
            "task_id": task['id'],
            "deadline": task['deadline'],
            "priority": task.get('priority', 'medium')
        }
        return self.add_document(user_id, text, metadata, doc_id=f"task_{task['id']}")
    
    def add_plan_to_context(self, user_id: int, plan: Dict[str, Any]):
        """Add daily plan to context"""
        text = f"Daily plan for {plan['date']}. Schedule: {plan['schedule_summary']}"
        metadata = {
            "type": "plan",
            "plan_id": plan['id'],
            "date": plan['date']
        }
        return self.add_document(user_id, text, metadata, doc_id=f"plan_{plan['id']}")

