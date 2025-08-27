#!/usr/bin/env python3
"""
Test script for the RAG Chatbot
This script demonstrates how to use the RAG response functions
"""

import asyncio
import os
from dotenv import load_dotenv
from rag_response import get_rag_response, get_enhanced_rag_response
from search import setup_database, add_document_to_knowledge_base

# Load environment variables
load_dotenv()

# Mock database session for testing
class MockDBSession:
    """Mock database session for testing purposes"""
    pass

async def test_rag_chatbot():
    """Test the RAG chatbot functionality"""
    
    print("🚀 Testing RAG Chatbot...")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What are the benefits of organic farming?",
        "How to grow tomatoes?",
        "What is NPK fertilizer?",
        "Soil preparation techniques",
        "Pest control methods"
    ]
    
    # Mock database session
    db = MockDBSession()
    
    print("\n📝 Testing RAG Response Function:")
    print("-" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        try:
            # Test simple RAG response
            response = await get_rag_response(query, db)
            print(f"   Response: {response[:100]}...")
            
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    print("\n🔍 Testing Enhanced RAG Response Function:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries[:3], 1):  # Test first 3 queries
        print(f"\n{i}. Query: {query}")
        
        try:
            # Test enhanced RAG response
            enhanced_response = await get_enhanced_rag_response(query, db)
            print(f"   Answer: {enhanced_response.get('answer', 'No answer')[:100]}...")
            print(f"   Confidence: {enhanced_response.get('confidence', 0):.2f}")
            print(f"   Documents Used: {enhanced_response.get('documents_used', 0)}")
            
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    print("\n✅ RAG Chatbot testing completed!")

async def test_database_operations():
    """Test database operations"""
    
    print("\n🗄️ Testing Database Operations:")
    print("-" * 30)
    
    try:
        # Test database setup
        print("Setting up database...")
        success = setup_database()
        if success:
            print("✅ Database setup successful")
        else:
            print("❌ Database setup failed")
        
        # Test adding a sample document
        print("\nAdding sample document...")
        sample_title = "Organic Farming Guide"
        sample_content = """
        Organic farming is a method of crop and livestock production that involves much more than choosing not to use pesticides, 
        fertilizers, genetically modified organisms, antibiotics and growth hormones. Organic farming is a production system 
        that sustains the health of soils, ecosystems and people. It relies on ecological processes, biodiversity and cycles 
        adapted to local conditions, rather than the use of inputs with adverse effects.
        
        Key benefits of organic farming include:
        - Improved soil health and fertility
        - Reduced environmental pollution
        - Better water quality
        - Enhanced biodiversity
        - Healthier food products
        """
        
        success = add_document_to_knowledge_base(sample_title, sample_content, {"category": "farming", "type": "guide"})
        if success:
            print("✅ Sample document added successfully")
        else:
            print("❌ Failed to add sample document")
            
    except Exception as e:
        print(f"❌ Database operation error: {str(e)}")

def check_environment():
    """Check if required environment variables are set"""
    
    print("🔧 Environment Check:")
    print("-" * 20)
    
    required_vars = [
        'GEMINI_API_KEY',
        'HUGGINGFACE_API_TOKEN',
        'DATABASE_URL'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    if not all_set:
        print("\n⚠️  Warning: Some required environment variables are not set.")
        print("Please check your .env file or environment configuration.")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

async def main():
    """Main test function"""
    
    print("🧪 RAG Chatbot Test Suite")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Cannot proceed without proper environment configuration.")
        return
    
    # Test database operations
    await test_database_operations()
    
    # Test RAG chatbot functionality
    await test_rag_chatbot()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
