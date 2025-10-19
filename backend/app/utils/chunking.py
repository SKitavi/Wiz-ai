from typing import List
import re

class TextChunker:
    @staticmethod
    def chunk_by_sentences(text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into semantic chunks"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def chunk_with_overlap(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Create overlapping chunks for better context"""
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += (chunk_size - overlap)
        
        return chunks
