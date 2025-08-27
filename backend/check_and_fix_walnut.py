import os
import psycopg2
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def check_and_fix_walnut():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Check current database content
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]
        print(f"📊 Total documents in database: {total_docs}")
        
        # Check for walnut content
        cursor.execute("SELECT id, title FROM documents WHERE content ILIKE %s", ('%walnut%',))
        walnut_docs = cursor.fetchall()
        print(f"🌰 Documents containing 'walnut': {len(walnut_docs)}")
        
        for doc in walnut_docs:
            print(f"  - ID: {doc[0]}, Title: {doc[1]}")
        
        # Check recent entries
        cursor.execute("SELECT id, title, LEFT(content, 80) FROM documents ORDER BY created_at DESC LIMIT 3")
        recent_docs = cursor.fetchall()
        print(f"\n📝 Recent documents:")
        for doc in recent_docs:
            print(f"  - ID: {doc[0]}, Title: {doc[1]}")
            print(f"    Content: {doc[2]}...")
        
        # Remove any existing walnut guides to avoid duplicates
        cursor.execute("DELETE FROM documents WHERE title LIKE %s", ('%Walnut%',))
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"🗑️ Removed {deleted} existing walnut documents")
        
        # Add the comprehensive walnut guide
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
            "crops_covered": ["walnut"],
            "application_method": "ring_around_stem",
            "dosage_information": {
                "mature_trees": "2-5 kg per tree",
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
                "walnut", "tree_nut", "ring_application", "mature_trees",
                "seedlings", "transplantation", "tree_crop", "navyakosh",
                "organic_fertilizer", "fertilizer_application", "dosage_guide"
            ]
        }
        
        # Insert the walnut guide
        cursor.execute("""
            INSERT INTO documents (title, content, metadata) 
            VALUES (%s, %s, %s)
        """, ("Navyakosh Walnut Application Guide", content, json.dumps(metadata)))
        
        conn.commit()
        
        # Verify the insertion
        cursor.execute("SELECT COUNT(*) FROM documents WHERE content ILIKE %s", ('%walnut%',))
        final_walnut_count = cursor.fetchone()[0]
        
        print(f"\n✅ Successfully added walnut guide to database")
        print(f"📄 Content length: {len(content)} characters") 
        print(f"🏷️ Tags: {len(metadata['tags'])} tags added")
        print(f"🌰 Final walnut documents count: {final_walnut_count}")
        print(f"🔬 Microorganisms included: {len(metadata['microorganisms'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_and_fix_walnut()
