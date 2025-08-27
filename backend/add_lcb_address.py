import os
import json
import sys
sys.path.append('.')
from api.index import chatbot

def add_lcb_address():
    """Add LCB Fertilizers address information to the database"""
    
    # Document content
    title = "LCB Fertilizers Address"
    content = """Address:
3rd Floor, Diamond Jubeeli Hall,
IIT Kanpur,
Kanpur - 208016

LCB Fertilizers is located at the 3rd Floor of Diamond Jubeeli Hall within the prestigious IIT Kanpur campus in Kanpur, Uttar Pradesh. The complete address is:

3rd Floor, Diamond Jubeeli Hall,
IIT Kanpur,
Kanpur - 208016, Uttar Pradesh, India

This location places LCB Fertilizers within one of India's premier technological institutes, reflecting the company's commitment to scientific innovation and research-based agricultural solutions. The IIT Kanpur campus location provides access to cutting-edge research facilities and collaboration opportunities with leading agricultural scientists and researchers."""
    
    # Metadata
    metadata = {
        "type": "company_address",
        "title": "LCB Fertilizers Address",
        "category": "address_info",
        "company_name": "LCB Fertilizers",
        "content_type": "address_information",
        "address_details": {
            "floor": "3rd Floor",
            "building": "Diamond Jubeeli Hall",
            "institution": "IIT Kanpur",
            "city": "Kanpur",
            "postal_code": "208016",
            "state": "Uttar Pradesh",
            "country": "India"
        },
        "tags": [
            "LCB Fertilizers",
            "address",
            "location",
            "IIT Kanpur",
            "Kanpur",
            "Diamond Jubeeli Hall",
            "office address",
            "company location"
        ]
    }
    
    print("Adding LCB Fertilizers address information to database...")
    
    success = chatbot.add_document(
        title=title,
        content=content,
        metadata=metadata
    )
    
    if success:
        print("✅ Successfully added LCB Fertilizers address information!")
    else:
        print("❌ Failed to add LCB Fertilizers address information.")
    
    return success

if __name__ == "__main__":
    # Setup database connection if needed
    print("Setting up database connection...")
    
    # Add the address information
    success = add_lcb_address()
    
    if success:
        print("\n🎉 LCB Fertilizers address information has been added to the RAG database!")
        print("\nNow users can ask questions like:")
        print("- 'What is LCB Fertilizers address?'")
        print("- 'Where is LCB Fertilizers located?'")
        print("- 'What is the office location of LCB Fertilizers?'")
    else:
        print("\n❌ Failed to add address information. Please check your database connection.")
