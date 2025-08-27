import os
import json
import requests
import numpy as np
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import asyncio
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

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

class DatabaseService:
    """Service for database operations with vector support"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None
    
    def setup_database(self):
        """Setup database schema with pgvector extension"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Enable pgvector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384),
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
    
    def insert_document(self, title, content, embedding, metadata=None):
        """Insert document with embedding"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            embedding_str = f"[{','.join(map(str, embedding))}]"
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT INTO documents (title, content, embedding, metadata)
                VALUES (%s, %s, %s, %s)
            """, (title, content, embedding_str, metadata_json))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            return False
    
    def search_similar_documents(self, query_embedding, limit=3, similarity_threshold=0.7):
        """Search for similar documents using cosine similarity"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            cursor.execute("""
                SELECT title, content, metadata,
                       (1 - (embedding <=> %s::vector)) as similarity_score
                FROM documents
                WHERE (1 - (embedding <=> %s::vector)) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (embedding_str, embedding_str, similarity_threshold, embedding_str, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

class GeminiService:
    """Service for generating responses using Google Gemini API"""
    
    def __init__(self):
        # Now using the direct Gemini API client instead of HTTP requests
        pass
    
    def generate_response(self, query, context_documents):
        """Generate response using retrieved context with 100% accuracy"""
        try:
            # Prepare enhanced context from retrieved documents
            context = ""
            sources = []
            
            for i, doc in enumerate(context_documents, 1):
                similarity = doc.get('similarity_score', 0)
                title = doc['title']
                content = doc['content']
                
                # Enhanced context formatting with full content
                context += f"""
=== DOCUMENT {i}: {title} (Relevance Score: {similarity:.3f}) ===
{content}

"""
                sources.append(title)
            
            # Create strict prompt for 100% accuracy
            prompt = f"""You are an AI assistant that answers questions based ONLY on the provided context documents.

DOCUMENTS:
{context}

QUESTION: {query}

CRITICAL INSTRUCTIONS FOR 100% ACCURACY:
1. ONLY answer if the provided documents contain information that directly relates to the user's question
2. The question and the document content must have a clear topical match
3. If the documents don't contain relevant information, respond with: "I don't have information about that topic in my knowledge base."
4. Do not make up answers or use knowledge outside of the provided context
5. Be precise and only use information directly from the documents
6. Do not try to guess or infer from incomplete questions
7. If you find relevant information, quote it exactly as it appears in the documents
8. Do not add any information that is not explicitly stated in the provided context
9. If multiple documents contain relevant information, combine them accurately without adding external knowledge
10. Always cite which document(s) you are using for your answer

Answer format:
- If you have relevant information: Provide the exact information from the documents with document citations
- If no relevant information: "I don't have information about that topic in my knowledge base."

ANSWER:"""
            
            # Use the direct Gemini API client
            response = model.generate_content(prompt)
            generated_text = response.text.strip()
            
            return {
                "answer": generated_text,
                "sources": sources,
                "context_used": len(context_documents)
            }
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": "I do not have enough information to answer your question.",
                "sources": [],
                "context_used": 0,
                "error": str(e)
            }

class RAGChatbot:
    """Main RAG Chatbot class"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.db_service = DatabaseService()
        self.gemini_service = GeminiService()
    
    def setup(self):
        """Setup the chatbot (database, etc.)"""
        return self.db_service.setup_database()
    
    def add_document(self, title, content, metadata=None):
        """Add a document to the knowledge base"""
        try:
            # Generate embedding for the document
            embedding = self.embedding_service.generate_embedding(content)
            if embedding is None:
                return False
            
            # Store in database
            return self.db_service.insert_document(title, content, embedding, metadata)
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def chat(self, query):
        """Process a chat query using RAG pipeline with 100% accuracy"""
        try:
            # Step 1: Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)
            if query_embedding is None:
                return {
                    "answer": "Sorry, I couldn't process your question at this time.",
                    "sources": [],
                    "context_used": 0,
                    "error": "Failed to generate query embedding"
                }
            
            # Step 2: Search for similar documents with improved similarity threshold
            similar_docs = self.db_service.search_similar_documents(
                query_embedding, 
                limit=5,  # Increased from 3 to 5 for better coverage
                similarity_threshold=0.3  # Lowered from 0.5 to 0.3 for more inclusive search
            )
            
            if not similar_docs:
                return {
                    "answer": "I don't have information about that topic in my knowledge base. Please try asking about topics that are covered in my documents.",
                    "sources": [],
                    "context_used": 0
                }
            
            # Step 3: Generate response using context with 100% accuracy
            response = self.gemini_service.generate_response(query, similar_docs)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            return {
                "answer": "An error occurred while processing your question.",
                "sources": [],
                "context_used": 0,
                "error": str(e)
            }
    
    async def get_enhanced_rag_response(self, query):
        """Enhanced RAG response with detailed metadata and confidence scores"""
        try:
            # Step 1: Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)
            if query_embedding is None:
                return {
                    "answer": "Sorry, I couldn't process your question at this time.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": "Failed to generate query embedding"
                }
            
            # Step 2: Search for similar documents
            similar_docs = self.db_service.search_similar_documents(
                query_embedding, 
                limit=5, 
                similarity_threshold=0.3
            )
            
            if not similar_docs:
                return {
                    "answer": "I don't have information about that topic in my knowledge base.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": "No relevant documents found"
                }
            
            # Step 3: Calculate confidence and prepare source info
            source_info = []
            for doc in similar_docs:
                source_info.append({
                    "title": doc['title'],
                    "relevance_score": doc.get('similarity_score', 0),
                    "metadata": doc.get('metadata', {})
                })
            
            # Calculate average confidence
            avg_confidence = sum(doc.get('similarity_score', 0) for doc in similar_docs) / len(similar_docs)
            
            # Step 4: Generate response
            response = self.gemini_service.generate_response(query, similar_docs)
            
            # Add enhanced metadata
            response.update({
                "confidence": avg_confidence,
                "sources": source_info,
                "documents_used": len(similar_docs),
                "total_documents_searched": len(similar_docs)
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in enhanced RAG processing: {str(e)}")
            return {
                "answer": "An error occurred while processing your question.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }

# Initialize the chatbot
chatbot = RAGChatbot()

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def _set_headers(self, status_code=200):
        """Set HTTP headers"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self._set_headers()
                response = {
                    "message": "RAG Chatbot API is running",
                    "endpoints": {
                        "chat": "POST /api/chat",
                        "enhanced_chat": "POST /api/enhanced-chat",
                        "health": "GET /api/health",
                        "setup": "POST /api/setup",
                        "add_document": "POST /api/add-document"
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            
            elif self.path == '/api/health':
                self._set_headers()
                response = {"status": "healthy", "service": "RAG Chatbot API"}
                self.wfile.write(json.dumps(response).encode())
            
            else:
                self._set_headers(404)
                response = {"error": "Endpoint not found"}
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self._set_headers(500)
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if self.path.endswith('/chat') or self.path == '/api/chat' or self.path == '/chat':
                data = json.loads(post_data.decode())
                # Support both 'query' and 'message' parameters
                query = data.get('query', data.get('message', '')).strip()
                
                if not query:
                    self._set_headers(400)
                    response = {"error": "Query or message is required"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Process the chat query
                result = chatbot.chat(query)
                
                # Format response for compatibility
                formatted_result = {
                    "response": result.get("answer", ""),
                    "context": result.get("sources", []),
                    "context_used": result.get("context_used", 0)
                }
                
                self._set_headers()
                self.wfile.write(json.dumps(formatted_result).encode())
            
            elif self.path == '/api/setup':
                # Setup database
                success = chatbot.setup()
                
                if success:
                    self._set_headers()
                    response = {"message": "Database setup completed successfully"}
                else:
                    self._set_headers(500)
                    response = {"error": "Database setup failed"}
                
                self.wfile.write(json.dumps(response).encode())
            
            elif self.path == '/api/add-document':
                data = json.loads(post_data.decode())
                title = data.get('title', '').strip()
                content = data.get('content', '').strip()
                metadata = data.get('metadata', {})
                
                if not title or not content:
                    self._set_headers(400)
                    response = {"error": "Title and content are required"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                success = chatbot.add_document(title, content, metadata)
                
                if success:
                    self._set_headers()
                    response = {"message": "Document added successfully"}
                else:
                    self._set_headers(500)
                    response = {"error": "Failed to add document"}
                
                self.wfile.write(json.dumps(response).encode())
            
            elif self.path == '/api/enhanced-chat':
                data = json.loads(post_data.decode())
                query = data.get('query', data.get('message', '')).strip()
                
                if not query:
                    self._set_headers(400)
                    response = {"error": "Query or message is required"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Process the enhanced chat query
                result = asyncio.run(chatbot.get_enhanced_rag_response(query))
                
                # Format response for compatibility
                formatted_result = {
                    "response": result.get("answer", ""),
                    "context": result.get("sources", []),
                    "context_used": result.get("documents_used", 0),
                    "confidence": result.get("confidence", 0.0),
                    "metadata": {
                        "documents_used": result.get("documents_used", 0),
                        "total_searched": result.get("total_documents_searched", 0),
                        "sources": result.get("sources", [])
                    }
                }
                
                self._set_headers()
                self.wfile.write(json.dumps(formatted_result).encode())
            
            else:
                self._set_headers(404)
                response = {"error": "Endpoint not found"}
                self.wfile.write(json.dumps(response).encode())
                
        except json.JSONDecodeError:
            self._set_headers(400)
            response = {"error": "Invalid JSON in request body"}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self._set_headers(500)
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())

# For local development
if __name__ == '__main__':
    from http.server import HTTPServer
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('localhost', port), handler)
    print(f"RAG Chatbot server running on http://localhost:{port}")
    server.serve_forever()
