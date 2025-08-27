import os
import psycopg2
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def add_walnut_guide():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # The walnut application guide content
    content = """How to Use Navyakosh: Application Guide for Other Crops

WALNUT

Application (For Mature Trees):
• Method: Dig a ring around the stem, apply the fertilizer, and then cover it with soil
• Dosage: 2-5 kg of Navyakosh Organic Fertilizer per tree

Note (For Seedlings):
• Apply 500 grams of fertilizer per plant at the base during seedling transplantation

Mechanism of Action:
Active microorganisms in the fertilizer (Mycorrhiza (VAM), Phosphate Solubilizing Bacteria, Azospirillum, Potassium Mobilizing Biofertilizer (KMB), Pseudomonas, etc.) get activated and help plants to get and utilize all macro and micronutrients throughout the crop cycle."""
    
    # Comprehensive metadata for walnut guide
    metadata = {
        "product_name": "Navyakosh",
        "category": "organic_fertilizer",
        "type": "application_guide",
        "company": "LCB Fertilizers",
        "content_type": "usage_instructions",
        "crop_category": "walnut_specific",
        "crops_covered": [
            "walnut"
        ],
        "application_method": "ring_around_stem",
        "dosage_information": {
            "mature_trees": "2-5 kg per tree",
            "seedlings": "500 grams per plant",
            "application_timing": "during seedling transplantation"
        },
        "application_details": {
            "method_mature": "dig ring around stem and cover with soil",
            "method_seedlings": "base application during transplantation",
            "tree_stage": [
                "mature_trees",
                "seedlings"
            ]
        },
        "microorganisms": [
            "Mycorrhiza (VAM)",
            "Phosphate Solubilizing Bacteria",
            "Azospirillum",
            "Potassium Mobilizing Biofertilizer (KMB)",
            "Pseudomonas"
        ],
        "crop_type": "tree_nut",
        "application_frequency": "single_dose_system",
        "special_instructions": [
            "ring_method_for_mature_trees",
            "base_application_for_seedlings",
            "cover_with_soil_after_application"
        ],
        "tags": [
            "walnut",
            "tree_nut",
            "ring_application",
            "mature_trees",
            "seedlings",
            "transplantation",
            "tree_crop"
        ]
    }
    
    try:
        # Add the walnut guide to documents table
        cursor.execute("""
            INSERT INTO documents (title, content, metadata) 
            VALUES (%s, %s, %s)
        """, ("Navyakosh Walnut Application Guide", content, json.dumps(metadata)))
        
        conn.commit()
        print("✅ Successfully added Navyakosh walnut application guide to database")
        print(f"📄 Content length: {len(content)} characters")
        print(f"🏷️  Tags: {', '.join(metadata['tags'])}")
        print(f"🌰 Crop: {metadata['crops_covered'][0]}")
        print(f"📦 Dosage - Mature trees: {metadata['dosage_information']['mature_trees']}")
        print(f"🌱 Dosage - Seedlings: {metadata['dosage_information']['seedlings']}")
        print(f"🔬 Microorganisms: {len(metadata['microorganisms'])} types included")
        
    except Exception as e:
        print(f"❌ Error adding walnut guide: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_walnut_guide()
