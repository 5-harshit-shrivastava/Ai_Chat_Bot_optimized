import os
import json
from api.index import chatbot

def add_contact_information():
    """Add LCB Fertilizers contact information to the database"""
    
    contact_document = {
        "title": "LCB Fertilizers Contact Information",
        "content": """LCB Fertilizers Contact Details:

Phone: +91 91988-03978

Email Addresses:
- General Inquiries: contact@lcbfertilizers.com
- B2B and Dealership: ceo@lcbfertilizers.com

For general questions about fertilizers, soil management, or product information, please contact us at contact@lcbfertilizers.com.

For business partnerships, dealership opportunities, or bulk orders, please reach out to our CEO at ceo@lcbfertilizers.com.

You can also call us directly at +91 91988-03978 for immediate assistance with your fertilizer needs.""",
        "metadata": {
            "type": "contact_information",
            "company": "LCB Fertilizers",
            "phone": "+91 91988-03978",
            "general_email": "contact@lcbfertilizers.com",
            "business_email": "ceo@lcbfertilizers.com",
            "category": "company_info"
        }
    }
    
    print("Adding LCB Fertilizers contact information to database...")
    
    success = chatbot.add_document(
        title=contact_document["title"],
        content=contact_document["content"],
        metadata=contact_document["metadata"]
    )
    
    if success:
        print("✅ Successfully added LCB Fertilizers contact information!")
        print("\nContact details now available in the chatbot:")
        print("- Phone: +91 91988-03978")
        print("- General: contact@lcbfertilizers.com") 
        print("- B2B/Dealership: ceo@lcbfertilizers.com")
    else:
        print("❌ Failed to add contact information!")
    
    return success

def clear_all_data():
    """Clear all existing data from the database"""
    try:
        from api.index import DatabaseService
        db_service = DatabaseService()
        conn = db_service.get_connection()
        
        if not conn:
            print("❌ Failed to connect to database!")
            return False
            
        cursor = conn.cursor()
        
        print("🗑️ Clearing all existing data from database...")
        
        # Delete all documents
        cursor.execute("DELETE FROM documents;")
        
        # Reset the sequence
        cursor.execute("ALTER SEQUENCE documents_id_seq RESTART WITH 1;")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ All data cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Database Management Script ===\n")
    
    # First clear all existing data
    if clear_all_data():
        print("\n=== Adding New Contact Information ===\n")
        
        # Add the contact information
        if add_contact_information():
            print("\n🚀 Database updated successfully!")
            print("\nYou can now ask the chatbot questions like:")
            print("- 'What is your contact information?'")
            print("- 'How can I contact LCB Fertilizers?'")
            print("- 'What is the phone number for LCB Fertilizers?'")
            print("- 'How do I contact for business partnerships?'")
        else:
            print("\n❌ Failed to add contact information!")
    else:
        print("\n❌ Failed to clear existing data!")
