import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict
import os

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "/app/data/chroma"):
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        try:
            self.collection = self.client.get_or_create_collection(
                name="shl_assessments",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB collection initialized with {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def add_assessments(self, assessments: List[Dict], embeddings: List[List[float]]):
        """Add assessments to vector store"""
        try:
            if not assessments or not embeddings:
                logger.warning("No assessments or embeddings to add")
                return
            
            # Prepare data
            ids = [f"assessment_{i}" for i in range(len(assessments))]
            documents = [self._create_document(a) for a in assessments]
            metadatas = [self._create_metadata(a) for a in assessments]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(assessments)} assessments to vector store")
            
        except Exception as e:
            logger.error(f"Error adding assessments to vector store: {str(e)}")
            raise
    
    def search(self, query_embedding: List[float], n_results: int = 10) -> List[Dict]:
        """Search for similar assessments"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count())
            )
            
            # Format results
            assessments = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    assessments.append({
                        'name': metadata['name'],
                        'url': metadata['url'],
                        'description': metadata['description'],
                        'duration': metadata['duration'],
                        'test_type': eval(metadata['test_type']),
                        'adaptive_support': metadata['adaptive_support'],
                        'remote_support': metadata['remote_support'],
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return assessments
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def _create_document(self, assessment: Dict) -> str:
        """Create searchable document from assessment"""
        return f"{assessment['name']} {assessment['description']} {' '.join(assessment['test_type'])}"
    
    def _create_metadata(self, assessment: Dict) -> Dict:
        """Create metadata for assessment"""
        return {
            'name': assessment['name'],
            'url': assessment['url'],
            'description': assessment['description'],
            'duration': str(assessment['duration']),
            'test_type': str(assessment['test_type']),
            'adaptive_support': assessment['adaptive_support'],
            'remote_support': assessment['remote_support']
        }
    
    def clear(self):
        """Clear all data from vector store"""
        try:
            self.client.delete_collection("shl_assessments")
            self.collection = self.client.create_collection(
                name="shl_assessments",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
    
    def count(self) -> int:
        """Get count of documents in vector store"""
        return self.collection.count()
