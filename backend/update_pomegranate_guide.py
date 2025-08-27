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

def update_pomegranate_guide():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Enhanced pomegranate application guide content with better structure
    content = """How to Use Navyakosh: Application Guide for Fruits & Vegetables

POMEGRANATE FERTILIZER APPLICATION

Application for Mature Trees:
• Method: Dig a ring around the stem, apply the fertilizer, and then cover it with soil
• Dosage: 1-2 kg of Navyakosh Organic Fertilizer per tree

Application for Seedlings:
• Apply 500 grams of fertilizer per plant at the base during seedling transplantation

MECHANISM OF ACTION FOR POMEGRANATE:
Active microorganisms in Navyakosh fertilizer get activated and help pomegranate plants absorb and utilize all macro and micronutrients throughout the crop cycle.

KEY MICROORGANISMS IN NAVYAKOSH FOR POMEGRANATE:
• Mycorrhiza (VAM) - Enhances nutrient and water absorption
• Phosphate Solubilizing Bacteria (PSB) - Makes phosphorus available to plants
• Azospirillum - Fixes atmospheric nitrogen for plant use
• Potassium Mobilizing Biofertilizer (KMB) - Releases potassium for plant uptake
• Pseudomonas - Promotes plant growth and disease resistance

BENEFITS FOR POMEGRANATE CULTIVATION:
- Improved fruit quality and yield
- Enhanced root development
- Better nutrient utilization
- Increased disease resistance
- Sustainable organic nutrition"""
    
    # Enhanced metadata
    metadata = {
        "product_name": "Navyakosh",
        "category": "organic_fertilizer",
        "type": "application_guide",
        "company": "LCB Fertilizers",
        "content_type": "detailed_usage_instructions",
        "crop_category": "pomegranate_specific",
        "crops_covered": ["pomegranate"],
        "application_method": "ring_around_stem",
        "dosage_information": {
            "mature_trees": "1-2 kg per tree",
            "seedlings": "500 grams per plant",
            "application_timing": "during seedling transplantation"
        },
        "microorganisms_detailed": {
            "mycorrhiza_vam": "enhances nutrient and water absorption",
            "phosphate_solubilizing_bacteria": "makes phosphorus available",
            "azospirillum": "fixes atmospheric nitrogen",
            "potassium_mobilizing_biofertilizer": "releases potassium",
            "pseudomonas": "promotes growth and disease resistance"
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
        "benefits": [
            "improved_fruit_quality",
            "enhanced_root_development", 
            "better_nutrient_utilization",
            "increased_disease_resistance"
        ],
        "tags": [
            "pomegranate",
            "fruit_tree",
            "ring_application",
            "mature_trees",
            "seedlings",
            "mycorrhiza",
            "phosphate_solubilizing_bacteria",
            "azospirillum",
            "potassium_mobilizing",
            "pseudomonas",
            "navyakosh",
            "organic_fertilizer",
            "microorganisms"
        ]
    }
    
    try:
        # Generate new embedding for the enhanced content
        print("🔄 Generating new embedding for enhanced pomegranate guide...")
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
        print("✅ New embedding generated successfully")
        
        # Update the existing pomegranate guide
        cursor.execute("""
            UPDATE documents 
            SET content = %s, metadata = %s, embedding = %s, updated_at = CURRENT_TIMESTAMP
            WHERE title LIKE %s
        """, (content, json.dumps(metadata), json.dumps(embedding), '%Pomegranate%'))
        
        if cursor.rowcount == 0:
            print("No existing pomegranate document found, inserting new one...")
            cursor.execute("""
                INSERT INTO documents (title, content, metadata, embedding) 
                VALUES (%s, %s, %s, %s)
            """, ("Navyakosh Pomegranate Application Guide", content, json.dumps(metadata), json.dumps(embedding)))
        
        conn.commit()
        
        print("✅ Successfully updated Navyakosh pomegranate application guide")
        print(f"📄 Enhanced content length: {len(content)} characters")
        print(f"🔬 Microorganisms with details: {len(metadata['microorganisms_detailed'])} types")
        print(f"🏷️ Tags: {len(metadata['tags'])} tags")
        print(f"🍎 Benefits listed: {len(metadata['benefits'])}")
        
        # Test the microorganisms query
        test_query = "What are the key microorganisms in Navyakosh for pomegranate"
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
                print(f"🔍 Microorganisms query test - Distance: {result[1]:.4f}")
        
    except Exception as e:
        print(f"❌ Error updating pomegranate guide: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_pomegranate_guide()
