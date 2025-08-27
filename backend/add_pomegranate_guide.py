import os
import psycopg2
from dotenv import load_dotenv
import json
import requests

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

def add_pomegranate_guide():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # The pomegranate application guide content
    content = """How to Use Navyakosh: Application Guide for Fruits & Vegetables

POMEGRANATE

Application (For Mature Trees):
• Method: Dig a ring around the stem, apply the fertilizer, and then cover it with soil
• Dosage: 1-2 kg of Navyakosh Organic Fertilizer per tree

Note (For Seedlings):
• Apply 500 grams of fertilizer per plant at the base during seedling transplantation

Mechanism of Action:
Active microorganisms in the fertilizer get activated and help plants absorb and utilize all macro and micronutrients throughout the crop cycle.

Key Microorganisms: Mycorrhiza (VAM), Phosphate Solubilizing Bacteria (PSB), Azospirillum, Potassium Mobilizing Biofertilizer (KMB), Pseudomonas, etc."""
    
    # Comprehensive metadata for pomegranate guide
    metadata = {
        "product_name": "Navyakosh",
        "category": "organic_fertilizer",
        "type": "application_guide",
        "company": "LCB Fertilizers",
        "content_type": "usage_instructions",
        "crop_category": "pomegranate_specific",
        "crops_covered": ["pomegranate"],
        "application_method": "ring_around_stem",
        "dosage_information": {
            "mature_trees": "1-2 kg per tree",
            "seedlings": "500 grams per plant",
            "application_timing": "during seedling transplantation"
        },
        "application_details": {
            "method_mature": "dig ring around stem and cover with soil",
            "method_seedlings": "base application during transplantation",
            "tree_stage": ["mature_trees", "seedlings"]
        },
        "microorganisms": [
            "Mycorrhiza (VAM)",
            "Phosphate Solubilizing Bacteria (PSB)",
            "Azospirillum",
            "Potassium Mobilizing Biofertilizer (KMB)",
            "Pseudomonas"
        ],
        "crop_type": "fruit_tree",
        "fruit_category": "pomegranate",
        "application_frequency": "single_dose_system",
        "special_instructions": [
            "ring_method_for_mature_trees",
            "base_application_for_seedlings",
            "cover_with_soil_after_application"
        ],
        "tags": [
            "pomegranate",
            "fruit_tree",
            "ring_application",
            "mature_trees",
            "seedlings",
            "transplantation",
            "navyakosh",
            "organic_fertilizer",
            "fertilizer_application",
            "dosage_guide",
            "fruits_vegetables"
        ]
    }
    
    try:
        # Generate embedding for the content
        print("🔄 Generating embedding for pomegranate guide...")
        headers = {
            'Authorization': f'Bearer {HUGGINGFACE_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5',
            headers=headers,
            json={'inputs': content, 'options': {'wait_for_model': True}}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to generate embedding: {response.status_code} - {response.text}")
            return
        
        embedding = response.json()
        print("✅ Embedding generated successfully")
        
        # Add the pomegranate guide to documents table with embedding
        cursor.execute("""
            INSERT INTO documents (title, content, metadata, embedding) 
            VALUES (%s, %s, %s, %s)
        """, ("Navyakosh Pomegranate Application Guide", content, json.dumps(metadata), json.dumps(embedding)))
        
        conn.commit()
        
        # Verify the insertion with similarity search test
        test_query = "How to fertilize pomegranate trees"
        test_response = requests.post(
            'https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5',
            headers=headers,
            json={'inputs': test_query, 'options': {'wait_for_model': True}}
        )
        
        if test_response.status_code == 200:
            test_embedding = test_response.json()
            cursor.execute("""
                SELECT title, (embedding <=> %s::vector) as distance
                FROM documents 
                WHERE content ILIKE %s
                ORDER BY distance ASC
                LIMIT 1
            """, (json.dumps(test_embedding), '%pomegranate%'))
            
            result = cursor.fetchone()
            if result:
                print(f"🔍 Similarity test - Distance: {result[1]:.4f} for '{result[0]}'")
        
        print("✅ Successfully added Navyakosh pomegranate application guide to database")
        print(f"📄 Content length: {len(content)} characters")
        print(f"🏷️  Tags: {', '.join(metadata['tags'])}")
        print(f"🍎 Crop: {metadata['crops_covered'][0]}")
        print(f"📦 Dosage - Mature trees: {metadata['dosage_information']['mature_trees']}")
        print(f"🌱 Dosage - Seedlings: {metadata['dosage_information']['seedlings']}")
        print(f"🔬 Microorganisms: {len(metadata['microorganisms'])} types included")
        print(f"🎯 Application method: {metadata['application_method']}")
        
    except Exception as e:
        print(f"❌ Error adding pomegranate guide: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_pomegranate_guide()
