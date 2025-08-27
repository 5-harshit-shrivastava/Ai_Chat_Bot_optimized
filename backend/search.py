import os
import json
import requests
import numpy as np
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings using HuggingFace API"""
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"
        token = os.getenv('HUGGINGFACE_API_TOKEN', '').strip()
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.embedding_dim = 1024  # BAAI/bge-large-en-v1.5 dimensions
    
    def generate_embedding(self, text):
        """Generate embedding for given text"""
        try:
            payload = {
                "inputs": text,
                "options": {"wait_for_model": True}
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            # Check for different error types
            if response.status_code == 401:
                logger.error("HuggingFace API authentication failed. Check your token.")
                return None
            elif response.status_code == 503:
                logger.warning("Model is loading, waiting...")
                # Model might be loading, try again after a short wait
                import time
                time.sleep(5)
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                # Check if it's a nested list (batch response)
                if isinstance(result[0], list):
                    return result[0]  # First embedding in batch
                else:
                    return result  # Direct embedding
            elif isinstance(result, dict) and 'error' in result:
                logger.error(f"HuggingFace API error: {result['error']}")
                return None
            else:
                logger.error(f"Unexpected response format: {result}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("HuggingFace API timeout")
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

class Document:
    """Simple document class to represent search results"""
    def __init__(self, title, content, similarity_score=0.0, metadata=None):
        self.title = title
        self.content = content
        self.similarity_score = similarity_score
        self.metadata = metadata or {}

def search_similar_documents(query: str, db: Session, top_k: int = 5, similarity_threshold: float = 0.3):
    """
    Search for similar documents using vector similarity search.
    
    Args:
        query: The search query string
        db: Database session (not used in this implementation, kept for compatibility)
        top_k: Maximum number of documents to return
        similarity_threshold: Minimum similarity score (0.0 to 1.0)
    
    Returns:
        List of tuples: (Document, similarity_score)
    """
    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()
        
        # Generate embedding for the query
        query_embedding = embedding_service.generate_embedding(query)
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []
        
        # Get database connection
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL environment variable not set")
            return []
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Search for similar documents using cosine similarity
        cursor.execute("""
            SELECT title, content, metadata,
                   (1 - (embedding <=> %s::vector)) as similarity_score
            FROM documents
            WHERE (1 - (embedding <=> %s::vector)) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (embedding_str, embedding_str, similarity_threshold, embedding_str, top_k))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert results to Document objects with similarity scores
        documents = []
        for row in results:
            doc = Document(
                title=row['title'],
                content=row['content'],
                similarity_score=float(row['similarity_score']),
                metadata=row.get('metadata', {})
            )
            documents.append((doc, doc.similarity_score))
        
        # Sort by similarity score (highest first)
        documents.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(documents)} similar documents for query: {query}")
        return documents
        
    except Exception as e:
        logger.error(f"Error searching similar documents: {str(e)}")
        return []

def add_document_to_knowledge_base(title: str, content: str, metadata: dict = None):
    """
    Add a document to the knowledge base with automatic embedding generation.
    
    Args:
        title: Document title
        content: Document content
        metadata: Optional metadata dictionary
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()
        
        # Generate embedding for the document
        embedding = embedding_service.generate_embedding(content)
        if embedding is None:
            logger.error("Failed to generate document embedding")
            return False
        
        # Get database connection
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = f"[{','.join(map(str, embedding))}]"
        metadata_json = json.dumps(metadata or {})
        
        # Insert document with embedding
        cursor.execute("""
            INSERT INTO documents (title, content, embedding, metadata)
            VALUES (%s, %s, %s, %s)
        """, (title, content, embedding_str, metadata_json))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully added document: {title}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding document to knowledge base: {str(e)}")
        return False

def setup_database():
    """Setup database schema with pgvector extension"""
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding vector(1024),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index for vector similarity search
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
        return False
