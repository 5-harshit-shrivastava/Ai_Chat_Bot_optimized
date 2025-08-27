import os
import json
from api.index import chatbot

def setup_sample_data():
    """Setup sample agricultural fertilizer documents"""
    
    sample_documents = [
        {
            "title": "NPK Fertilizers for Wheat",
            "content": "NPK fertilizers containing nitrogen (N), phosphorus (P), and potassium (K) are essential for wheat cultivation. For wheat crops, a balanced NPK ratio of 120:60:40 kg/ha is recommended. Apply nitrogen in split doses - 50% at sowing, 25% at tillering, and 25% at grain filling stage. Phosphorus should be applied as basal dose during sowing. Potassium can be applied basally or in split doses.",
            "metadata": {"crop": "wheat", "type": "NPK", "season": "rabi"}
        },
        {
            "title": "Organic Fertilizers for Soil Health",
            "content": "Organic fertilizers improve soil structure, water retention, and microbial activity. Farmyard manure (FYM) applied at 10-15 tonnes per hectare enhances soil organic matter. Compost provides slow-release nutrients and improves soil biology. Green manures like dhaincha and sunhemp fix nitrogen and add organic matter. Vermicompost contains beneficial microorganisms and provides balanced nutrition.",
            "metadata": {"type": "organic", "benefit": "soil_health"}
        },
        {
            "title": "Nitrogen Deficiency Symptoms and Management",
            "content": "Nitrogen deficiency appears as yellowing of older leaves (chlorosis), starting from leaf tips. Plants show stunted growth and reduced tillering. To correct nitrogen deficiency, apply urea at 50-75 kg/ha or use ammonium sulfate. Side-dress application during active growth periods is most effective. Foliar application of 2% urea solution can provide quick relief.",
            "metadata": {"nutrient": "nitrogen", "type": "deficiency_management"}
        },
        {
            "title": "Phosphorus for Root Development",
            "content": "Phosphorus is crucial for root development, flowering, and seed formation. Deficiency symptoms include purple discoloration of leaves and poor root growth. Single Super Phosphate (SSP) and Di-Ammonium Phosphate (DAP) are common phosphorus sources. Apply phosphorus fertilizers close to seed placement for better uptake. Rock phosphate is suitable for acidic soils.",
            "metadata": {"nutrient": "phosphorus", "function": "root_development"}
        },
        {
            "title": "Potassium for Disease Resistance",
            "content": "Potassium enhances disease resistance, water use efficiency, and grain quality. Symptoms of potassium deficiency include marginal leaf burn and weak stems. Muriate of Potash (MOP) and Sulfate of Potash (SOP) are primary potassium sources. SOP is preferred for chloride-sensitive crops. Apply potassium in multiple splits for better utilization.",
            "metadata": {"nutrient": "potassium", "benefit": "disease_resistance"}
        },
        {
            "title": "Micro-nutrient Management",
            "content": "Micronutrients like zinc, iron, manganese, and boron are essential in small quantities. Zinc deficiency causes white bud in maize and khaira disease in rice. Apply zinc sulfate at 25 kg/ha for zinc-deficient soils. Iron deficiency causes interveinal chlorosis, treatable with iron chelates. Boron deficiency affects flowering and fruit set.",
            "metadata": {"type": "micronutrients", "application": "foliar_soil"}
        },
        {
            "title": "Rice Fertilizer Management",
            "content": "Rice requires specific fertilizer management due to waterlogged conditions. Apply NPK in ratio 120:60:40 kg/ha for high-yielding varieties. Use deep placement of urea super granules (USG) for better nitrogen efficiency. Apply phosphorus and potassium as basal dose. Split nitrogen application: 50% basal, 25% at tillering, 25% at panicle initiation.",
            "metadata": {"crop": "rice", "method": "split_application"}
        },
        {
            "title": "Soil Testing and Fertilizer Recommendations",
            "content": "Soil testing determines nutrient status and pH levels. Test soil every 2-3 years for accurate fertilizer recommendations. pH affects nutrient availability - most crops prefer pH 6.0-7.5. Acidic soils need lime application. Alkaline soils require sulfur or organic matter. Based on soil test results, adjust fertilizer rates accordingly.",
            "metadata": {"type": "soil_testing", "frequency": "2-3_years"}
        }
    ]
    
    print("Setting up sample agricultural fertilizer documents...")
    
    for doc in sample_documents:
        success = chatbot.add_document(
            title=doc["title"],
            content=doc["content"],
            metadata=doc["metadata"]
        )
        if success:
            print(f"✅ Added: {doc['title']}")
        else:
            print(f"❌ Failed to add: {doc['title']}")
    
    print("\nSample data setup completed!")

if __name__ == "__main__":
    # Setup database first
    print("Setting up database...")
    if chatbot.setup():
        print("✅ Database setup successful!")
        
        # Add sample documents
        setup_sample_data()
        
        print("\n🚀 RAG Chatbot is ready!")
        print("\nYou can now test with queries like:")
        print("- 'What is the best NPK ratio for wheat?'")
        print("- 'How to manage nitrogen deficiency?'")
        print("- 'What are the benefits of organic fertilizers?'")
        
    else:
        print("❌ Database setup failed! Please check your DATABASE_URL and ensure pgvector extension is available.")
