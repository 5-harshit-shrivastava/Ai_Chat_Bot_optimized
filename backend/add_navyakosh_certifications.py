import os
import json
import sys

# Add the current directory to Python path to import from api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.index import chatbot

def add_navyakosh_certifications():
    """Add Navyakosh certifications and recommendations to the database"""
    
    # Title for the document
    title = "Navyakosh Organic Fertilizer - Certifications & Recommendations"
    
    # Content about certifications and recommendations
    content = """Certifications & Recommendations:
• Government Approved (Authorization Letter Exemption): LCB Fertilizers is exempted from needing an authority letter to manufacture Navyakosh organic fertilizers
• NABL Lab Tested: Certified by a reputed, NABL-accredited Government of India laboratory
• Recommended by ICAR and IIPR: Has received official recommendations from the Indian Council of Agricultural Research (ICAR) and the Indian Institute of Pulses Research (IIPR)
• Proven Performer: A comparative analysis by DAV PG College, Gorakhpur, concluded that Navyakosh is superior for crop production

Key Certifications:
- Government approval with authorization letter exemption
- NABL-accredited Government of India laboratory certification
- Indian Council of Agricultural Research (ICAR) recommendation
- Indian Institute of Pulses Research (IIPR) recommendation
- Research validation from DAV PG College, Gorakhpur

Quality Assurance:
Navyakosh has undergone rigorous testing and validation by multiple government and research institutions, ensuring its effectiveness and safety for agricultural use."""
    
    # Comprehensive metadata
    metadata = {
        "product_name": "Navyakosh",
        "category": "organic_fertilizer",
        "type": "certifications_and_recommendations",
        "company": "LCB Fertilizers",
        "content_type": "official_approvals_and_certifications",
        "topics_covered": [
            "government_approval",
            "lab_testing_certification",
            "institutional_recommendations",
            "comparative_analysis_results"
        ],
        "government_approvals": [
            "authorization_letter_exemption",
            "government_approved_manufacturing"
        ],
        "lab_certifications": [
            "NABL_lab_tested",
            "government_of_india_laboratory_certified"
        ],
        "institutional_recommendations": [
            "ICAR_recommended",
            "IIPR_recommended"
        ],
        "research_validations": [
            "DAV_PG_College_comparative_analysis",
            "proven_superior_for_crop_production"
        ],
        "certification_details": {
            "government_approval": "LCB_Fertilizers_exempted_from_authority_letter_requirement",
            "lab_testing": "NABL_accredited_Government_of_India_laboratory",
            "ICAR": "Indian_Council_of_Agricultural_Research",
            "IIPR": "Indian_Institute_of_Pulses_Research",
            "research_institution": "DAV_PG_College_Gorakhpur"
        },
        "credibility_indicators": [
            "government_approved",
            "NABL_lab_tested",
            "ICAR_recommended",
            "IIPR_recommended",
            "research_validated"
        ],
        "quality_assurance": [
            "NABL_accredited_testing",
            "government_laboratory_certification",
            "institutional_recommendations",
            "comparative_analysis_superiority"
        ]
    }
    
    print("Adding Navyakosh certifications and recommendations to database...")
    
    # Add document to the database
    success = chatbot.add_document(
        title=title,
        content=content,
        metadata=metadata
    )
    
    if success:
        print("✅ Successfully added Navyakosh certifications and recommendations!")
        print(f"   Title: {title}")
        print(f"   Content length: {len(content)} characters")
        print(f"   Metadata fields: {len(metadata)} keys")
    else:
        print("❌ Failed to add Navyakosh certifications data")
    
    return success

if __name__ == "__main__":
    print("=== Adding Navyakosh Certifications Data ===")
    
    # Ensure database is set up
    print("Setting up database connection...")
    if not chatbot.setup():
        print("❌ Database setup failed!")
        exit(1)
    
    # Add the certifications data
    success = add_navyakosh_certifications()
    
    if success:
        print("\n🎉 Navyakosh certifications data successfully added to database!")
        print("\nYou can now ask questions like:")
        print("- 'What certifications does Navyakosh have?'")
        print("- 'Is Navyakosh government approved?'")
        print("- 'What institutions recommend Navyakosh?'")
        print("- 'Tell me about ICAR and IIPR recommendations for Navyakosh'")
    else:
        print("\n❌ Failed to add certifications data. Please check your database connection.")
