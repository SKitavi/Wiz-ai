from app.services.rag_service import RAGService
from typing import Dict, List

async def get_user_context(user_id: int, query: str = None) -> str:
    """Retrieve and format user context for LLM"""
    rag = RAGService()
    
    # Get relevant documents
    if query:
        results = rag.query(user_id, query, top_k=5)
    else:
        # Get recent context
        results = rag.collection.query(
            query_embeddings=None,
            where={"user_id": user_id},
            n_results=10
        )
    
    # Format context
    context_parts = []
    for result in results:
        context_parts.append(f"- {result['text']} (relevance: {1 - result['distance']:.2f})")
    
    return "\n".join(context_parts)
