import os
import psycopg2
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

def get_embedding(text):
    """Generate embedding for the given text using HuggingFace API"""
    api_url = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    response = requests.post(api_url, headers=headers, json={"inputs": text})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting embedding: {response.status_code}, {response.text}")
        return None

def add_faq_14():
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if this FAQ already exists
    cursor.execute("SELECT COUNT(*) FROM documents WHERE title = 'FAQ 14: Can small-scale farmers benefit from Navyakosh'")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"FAQ 14 already exists ({existing_count} documents found). Skipping addition.")
        cursor.close()
        conn.close()
        return
    
    # FAQ content - exact text only
    title = "FAQ 14: Can small-scale farmers benefit from Navyakosh"
    
    content = """Can small-scale farmers benefit from Navyakosh?
Yes, it's designed for farmers of all scales. Smallholders appreciate its cost-effectiveness over time, ease of use, and ability to improve yields on limited land without heavy investments in chemicals"""

    # Generate embedding for the content
    embedding = get_embedding(content)
    
    if embedding is None:
        print("Failed to generate embedding. Exiting.")
        cursor.close()
        conn.close()
        return
    
    # Insert the document
    cursor.execute("""
        INSERT INTO documents (title, content, embedding, metadata)
        VALUES (%s, %s, %s, %s)
    """, (
        title,
        content,
        embedding,
        json.dumps({
            "type": "FAQ",
            "question_number": 14,
            "topic": "Benefits for small-scale farmers",
            "category": "Farmer Benefits",
            "keywords": ["small-scale farmers", "farmers of all scales", "smallholders", "cost-effectiveness", "ease of use", "improve yields", "limited land", "heavy investments", "chemicals"],
            "product": "Navyakosh Organic Fertilizer"
        })
    ))
    
    # Commit the transaction
    conn.commit()
    
    # Get the inserted document info
    cursor.execute("SELECT id FROM documents WHERE title = %s", (title,))
    doc_id = cursor.fetchone()[0]
    
    print(f"✅ Successfully added FAQ 14!")
    print(f"   Document ID: {doc_id}")
    print(f"   Title: {title}")
    print(f"   Content: Exact text as provided")
    
    # Close connections
    cursor.close()
    conn.close()

if __name__ == "__main__":
    add_faq_14()
