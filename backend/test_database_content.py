#!/usr/bin/env python3
"""
Test script to verify database content after adding LCB Fertilizers and Navyakosh data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.index import RAGChatbot

def test_queries():
    """Test various queries related to the new content"""
    
    print("=== Testing Database Content ===")
    chatbot = RAGChatbot()
    
    test_questions = [
        "What is the contact information for LCB Fertilizers?",
        "Tell me about Navyakosh certifications",
        "Is Navyakosh government approved?",
        "What institutions recommend Navyakosh fertilizer?",
        "How can I contact LCB Fertilizers?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 50)
        
        try:
            response = chatbot.get_response(question)
            print(f"Answer: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "="*70)

if __name__ == "__main__":
    test_queries()
