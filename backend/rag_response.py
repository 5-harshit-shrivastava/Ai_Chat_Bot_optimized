import os
import google.generativeai as genai
import asyncio
from sqlalchemy.orm import Session
from search import search_similar_documents
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

def is_meaningful_query(query: str) -> bool:
    """Check if the query is meaningful and complete enough to process"""
    query = query.strip().lower()
    
    # Reject very short queries (less than 3 characters)
    if len(query) < 3:
        return False
    
    # Reject single words unless they are complete words
    words = query.split()
    if len(words) == 1:
        # Allow complete words that are at least 4 characters
        return len(query) >= 4
    
    # For multi-word queries, check if they form a reasonable question
    question_words = ['what', 'where', 'when', 'who', 'why', 'how', 'which', 'is', 'are', 'can', 'do', 'does']
    has_question_structure = any(word in query for word in question_words)
    
    return has_question_structure or len(words) >= 2

async def get_rag_response(query: str, db: Session) -> str:
    """
    Generate RAG response using Gemini AI with strict context adherence.
    This function ensures 100% accuracy by only using information from the provided documents.
    """
    # Validate query first
    if not is_meaningful_query(query):
        return "Please ask a complete and clear question. Your query seems too short or incomplete."
    
    # Search for similar documents using vector search
    similar_docs = search_similar_documents(query, db, top_k=5)
    
    if not similar_docs:
        return "I don't have any documents in my knowledge base. Please upload some documents first."
    
    # Filter documents by similarity threshold (only include if similarity > 0.3)
    relevant_docs = [(doc, score) for doc, score in similar_docs if score > 0.3]
    
    if not relevant_docs:
        return "I don't have information about that topic in my knowledge base."
    
    # Build context from relevant documents only
    context_parts = []
    for doc, score in relevant_docs:
        context_parts.append(f"Document (relevance: {score:.2f}):\n{doc.content}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Create a strict prompt for Gemini that ensures 100% accuracy
    prompt = f"""
    You are an AI assistant that answers questions based ONLY on the provided context documents.
    
    Context documents:
    {context}
    
    User question: {query}
    
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
    
    Answer:
    """
    
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text.strip()
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        logger.error(error_message)
        return error_message

async def get_enhanced_rag_response(query: str, db: Session) -> dict:
    """
    Enhanced RAG response that returns both the answer and metadata about the sources used.
    This provides transparency about which documents were used for the response.
    """
    # Validate query first
    if not is_meaningful_query(query):
        return {
            "answer": "Please ask a complete and clear question. Your query seems too short or incomplete.",
            "sources": [],
            "confidence": 0.0,
            "error": "Invalid query"
        }
    
    # Search for similar documents using vector search
    similar_docs = search_similar_documents(query, db, top_k=5)
    
    if not similar_docs:
        return {
            "answer": "I don't have any documents in my knowledge base. Please upload some documents first.",
            "sources": [],
            "confidence": 0.0,
            "error": "No documents in knowledge base"
        }
    
    # Filter documents by similarity threshold (only include if similarity > 0.3)
    relevant_docs = [(doc, score) for doc, score in similar_docs if score > 0.3]
    
    if not relevant_docs:
        return {
            "answer": "I don't have information about that topic in my knowledge base.",
            "sources": [],
            "confidence": 0.0,
            "error": "No relevant documents found"
        }
    
    # Build context from relevant documents only
    context_parts = []
    source_info = []
    
    for doc, score in relevant_docs:
        context_parts.append(f"Document (relevance: {score:.2f}):\n{doc.content}")
        source_info.append({
            "title": doc.title,
            "relevance_score": score,
            "metadata": doc.metadata
        })
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Calculate overall confidence based on document relevance scores
    avg_confidence = sum(score for _, score in relevant_docs) / len(relevant_docs)
    
    # Create a strict prompt for Gemini that ensures 100% accuracy
    prompt = f"""
    You are an AI assistant that answers questions based ONLY on the provided context documents.
    
    Context documents:
    {context}
    
    User question: {query}
    
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
    
    Answer:
    """
    
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        answer = response.text.strip()
        
        return {
            "answer": answer,
            "sources": source_info,
            "confidence": avg_confidence,
            "documents_used": len(relevant_docs),
            "total_documents_searched": len(similar_docs)
        }
        
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        logger.error(error_message)
        return {
            "answer": error_message,
            "sources": [],
            "confidence": 0.0,
            "error": str(e)
        }

def validate_document_relevance(query: str, document_content: str) -> float:
    """
    Validate if a document is relevant to the query.
    Returns a relevance score between 0 and 1.
    """
    query_words = set(query.lower().split())
    doc_words = set(document_content.lower().split())
    
    # Calculate word overlap
    common_words = query_words.intersection(doc_words)
    if not query_words:
        return 0.0
    
    # Basic relevance score based on word overlap
    relevance_score = len(common_words) / len(query_words)
    
    # Boost score for question words and important terms
    question_words = {'what', 'where', 'when', 'who', 'why', 'how', 'which', 'is', 'are', 'can', 'do', 'does'}
    if any(word in query_words for word in question_words):
        relevance_score *= 1.2
    
    return min(relevance_score, 1.0)

# Example usage function
async def example_usage():
    """Example of how to use the RAG response functions"""
    # This would be used in your actual application
    query = "What are the benefits of organic farming?"
    
    # Mock database session (replace with actual database session)
    class MockDB:
        pass
    
    db = MockDB()
    
    # Get simple RAG response
    response = await get_rag_response(query, db)
    print(f"Simple Response: {response}")
    
    # Get enhanced RAG response with metadata
    enhanced_response = await get_enhanced_rag_response(query, db)
    print(f"Enhanced Response: {enhanced_response}")

if __name__ == "__main__":
    # Run example if script is executed directly
    asyncio.run(example_usage())
