import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.index import chatbot

def add_navyakosh_coffee_guide():
    """Add Navyakosh coffee application guide to the database"""
    
    title = "How to Use Navyakosh: Application Guide for Coffee"
    
    content = """COFFEE

Application by Plant Age:
• Seedlings: 500 grams per plant
• Less than 1 year old: 1 kg per plant
• 2-4 years old: 3 kg per plant
• Above 4 years old: 5 kg per plant

Application Timing:
• First Application: Apply the fertilizer in a 30 cm deep ring around the crop before the monsoon season (pre-monsoon)
• Second Application: Apply after the monsoon season (post-monsoon). For this application, ensure weeds and vegetative debris are completely turned under and buried in the soil, and any stumps are removed

Key Application Features:
- Age-based dosing system for optimal nutrition
- Seasonal timing aligned with monsoon patterns
- Deep ring application method (30 cm depth)
- Pre and post-monsoon application schedule
- Proper soil preparation requirements
- Weed and debris management protocols

Benefits for Coffee Plants:
- Supports healthy growth at all plant stages
- Improves soil structure and water retention
- Enhances root development with deep ring application
- Provides balanced nutrition throughout growing seasons
- Promotes better coffee bean quality and yield"""
    
    metadata = {
        "product_name": "Navyakosh",
        "category": "organic_fertilizer",
        "type": "application_guide",
        "company": "LCB Fertilizers",
        "content_type": "usage_instructions",
        "crop_category": "coffee_specific",
        "crops_covered": [
            "coffee"
        ],
        "application_method": "ring_around_plant_age_based",
        "dosage_information": {
            "seedlings": "500 grams per plant",
            "less_than_1_year": "1 kg per plant",
            "2_to_4_years": "3 kg per plant",
            "above_4_years": "5 kg per plant"
        },
        "application_timing": {
            "first_application": "pre_monsoon_season",
            "second_application": "post_monsoon_season",
            "ring_depth": "30 cm deep ring around crop"
        },
        "special_instructions": {
            "pre_monsoon": "30 cm deep ring application before monsoon",
            "post_monsoon": "remove weeds and vegetative debris, bury in soil, remove stumps"
        },
        "age_based_dosing": {
            "seedling_stage": "500g",
            "young_plant": "1kg",
            "developing_plant": "3kg",
            "mature_plant": "5kg"
        },
        "crop_type": "plantation_crop",
        "application_frequency": "two_dose_seasonal_system",
        "seasonal_timing": [
            "pre_monsoon",
            "post_monsoon"
        ],
        "tags": [
            "coffee",
            "plantation_crop",
            "age_based_dosing",
            "seasonal_application",
            "monsoon_timing",
            "ring_application",
            "deep_ring_method",
            "weed_management"
        ]
    }
    
    print("Adding Navyakosh Coffee Application Guide to database...")
    
    success = chatbot.add_document(
        title=title,
        content=content,
        metadata=metadata
    )
    
    if success:
        print("✅ Successfully added: Navyakosh Coffee Application Guide")
        print("📋 Content includes:")
        print("   - Age-based dosing for coffee plants")
        print("   - Seasonal application timing")
        print("   - Deep ring application method")
        print("   - Pre and post-monsoon protocols")
        print("   - Soil preparation requirements")
    else:
        print("❌ Failed to add: Navyakosh Coffee Application Guide")

if __name__ == "__main__":
    # Setup database connection first
    print("Setting up database connection...")
    
    # Add the coffee application guide
    add_navyakosh_coffee_guide()
    
    print("\n🚀 Navyakosh Coffee Application Guide added successfully!")
    print("\nYou can now ask queries like:")
    print("- 'How to apply Navyakosh for coffee plants?'")
    print("- 'What is the dosage of Navyakosh for 3-year-old coffee plants?'")
    print("- 'When should I apply Navyakosh for coffee?'")
    print("- 'What is the ring application method for coffee?'")
