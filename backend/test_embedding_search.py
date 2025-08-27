import os
import psycopg2
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

def test_embedding_and_search():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Test 1: Check if walnut document exists
        print("🔍 Test 1: Checking walnut document in database...")
        cursor.execute("SELECT id, title, content FROM documents WHERE content ILIKE %s", ('%walnut%',))
        walnut_docs = cursor.fetchall()
        print(f"Found {len(walnut_docs)} walnut documents:")
        for doc in walnut_docs:
            print(f"  - ID: {doc[0]}, Title: {doc[1]}")
            print(f"    Content preview: {doc[2][:100]}...")
        
        if len(walnut_docs) == 0:
            print("❌ No walnut documents found!")
            return
        
        # Test 2: Check if documents have embeddings
        print("\n🔍 Test 2: Checking embeddings...")
        cursor.execute("SELECT id, title, embedding IS NOT NULL as has_embedding FROM documents")
        embedding_status = cursor.fetchall()
        print("Embedding status for all documents:")
        for doc in embedding_status:
            status = "✅ Has embedding" if doc[2] else "❌ No embedding"
            print(f"  - ID: {doc[0]}, Title: {doc[1][:50]}... - {status}")
        
        # Test 3: Generate embedding for walnut query
        print("\n🔍 Test 3: Testing embedding generation...")
        query = "How to apply fertilizer to walnut trees"
        
        headers = {
            'Authorization': f'Bearer {HUGGINGFACE_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'inputs': query,
            'options': {'wait_for_model': True}
        }
        
        response = requests.post(
            'https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            query_embedding = response.json()
            print(f"✅ Generated embedding for query (length: {len(query_embedding)})")
            
            # Test 4: Manual similarity search
            print("\n🔍 Test 4: Testing similarity search...")
            cursor.execute("""
                SELECT id, title, content, 
                       (embedding <=> %s::vector) as distance
                FROM documents 
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT 3
            """, (json.dumps(query_embedding),))
            
            results = cursor.fetchall()
            print("Similarity search results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. ID: {result[0]}, Distance: {result[3]:.4f}")
                print(f"     Title: {result[1]}")
                print(f"     Content: {result[2][:100]}...")
                print()
        else:
            print(f"❌ Embedding generation failed: {response.status_code} - {response.text}")
        
        # Test 5: Check for missing embeddings and generate them
        print("\n🔍 Test 5: Checking for documents without embeddings...")
        cursor.execute("SELECT id, title, content FROM documents WHERE embedding IS NULL")
        docs_without_embeddings = cursor.fetchall()
        
        if docs_without_embeddings:
            print(f"Found {len(docs_without_embeddings)} documents without embeddings:")
            for doc in docs_without_embeddings:
                print(f"  - ID: {doc[0]}, Title: {doc[1]}")
                
                # Generate embedding for this document
                payload = {
                    'inputs': doc[2][:1000],  # Limit content length
                    'options': {'wait_for_model': True}
                }
                
                response = requests.post(
                    'https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5',
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    embedding = response.json()
                    cursor.execute(
                        "UPDATE documents SET embedding = %s WHERE id = %s",
                        (json.dumps(embedding), doc[0])
                    )
                    print(f"    ✅ Generated and saved embedding for document {doc[0]}")
                else:
                    print(f"    ❌ Failed to generate embedding: {response.status_code}")
            
            conn.commit()
            print("\n✅ All missing embeddings have been generated!")
        else:
            print("✅ All documents have embeddings!")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_embedding_and_search()
