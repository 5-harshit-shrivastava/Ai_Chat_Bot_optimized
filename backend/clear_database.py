import os
import psycopg2
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all data from the database"""
    try:
        # Get database connection
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🗑️  Clearing all data from database...")
        
        # Drop all data from documents table
        cursor.execute("DELETE FROM documents;")
        
        # Reset the auto-increment counter
        cursor.execute("ALTER SEQUENCE documents_id_seq RESTART WITH 1;")
        
        # Commit the changes
        conn.commit()
        
        # Check how many rows were affected
        cursor.execute("SELECT COUNT(*) FROM documents;")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database cleared successfully!")
        print(f"📊 Remaining documents: {count}")
        print("\n🔄 Database is now empty and ready for fresh data.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing database: {str(e)}")
        return False

def reset_database_completely():
    """Drop and recreate the entire database schema"""
    try:
        # Get database connection
        db_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔥 Completely resetting database schema...")
        
        # Drop the documents table completely
        cursor.execute("DROP TABLE IF EXISTS documents CASCADE;")
        
        # Drop the index if it exists
        cursor.execute("DROP INDEX IF EXISTS documents_embedding_idx;")
        
        # Recreate the table with correct schema
        cursor.execute("""
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding vector(1024),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create HNSW index for better performance (instead of IVFFlat)
        cursor.execute("""
            CREATE INDEX documents_embedding_idx 
            ON documents USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """)
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database schema reset successfully!")
        print("🔧 Table recreated with 1024-dimension vectors (BAAI/bge-large-en-v1.5)")
        print("⚡ HNSW indexing enabled for optimal performance")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    print("🗄️  Database Management Options:")
    print("1. Clear all data (keep schema)")
    print("2. Reset database completely (drop and recreate)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        if clear_database():
            print("\n✨ Data cleared! You can now run setup_data.py to add fresh data.")
        else:
            print("\n❌ Failed to clear database.")
            
    elif choice == "2":
        confirm = input("\n⚠️  This will delete EVERYTHING. Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            if reset_database_completely():
                print("\n✨ Database reset! You can now run setup_data.py to initialize fresh data.")
            else:
                print("\n❌ Failed to reset database.")
        else:
            print("Operation cancelled.")
    else:
        print("Invalid choice. Please run the script again.")
