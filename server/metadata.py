from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
import os

Base = declarative_base()

class SharedFile(Base):
    __tablename__ = 'shared_files'
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    share_id = Column(String, unique=True, nullable=False)
    owner = Column(String, nullable=False)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    file_size = Column(Integer)
    file_type = Column(String)

# DB init
def get_engine():
    from dotenv import load_dotenv
    
    # Load .env from parent directory (pybox folder)
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)
    
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Clean up the URL (remove extra spaces)
        database_url = database_url.strip()
        
        # If it's a relative SQLite path, make it relative to the parent directory
        if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
            # Extract the database filename
            db_filename = database_url.replace('sqlite:///', '')
            # Create path relative to parent directory (pybox folder)
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(parent_dir, db_filename)
            database_url = f"sqlite:///{db_path}"
    
    print(f"Database URL: {database_url}")
    
    # Check if database file exists (for SQLite)
    if database_url and 'sqlite' in database_url:
        db_path = database_url.replace('sqlite:///', '')
        print(f"Database file path: {db_path}")
        print(f"Database file exists: {os.path.exists(db_path)}")
    
    return create_engine(database_url, echo=True)

engine = get_engine()
Session = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)
print('Database setup completed successfully!')

# Function to save and verify data
def save_shared_file(file_data):
    session = Session()
    try:
        new_file = SharedFile(**file_data)
        session.add(new_file)
        session.commit()
        print(f"File {file_data['filename']} saved successfully!")
        
        # Verify the data was actually saved
        verify_save(session, file_data['id'])
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving file: {e}")
        return False
    finally:
        session.close()

# Function to verify data was saved
def verify_save(session, file_id):
    try:
        saved_file = session.query(SharedFile).filter(SharedFile.id == file_id).first()
        if saved_file:
            print(f"✓ Verification successful: File found in database")
            print(f"  ID: {saved_file.id}")
            print(f"  Filename: {saved_file.filename}")
            print(f"  Created: {saved_file.created_at}")
        else:
            print(f"✗ Verification failed: File NOT found in database")
    except Exception as e:
        print(f"✗ Verification error: {e}")

# Function to list all files in database
def list_all_files():
    session = Session()
    try:
        all_files = session.query(SharedFile).all()
        print(f"\n--- All files in database ({len(all_files)} total) ---")
        for file in all_files:
            print(f"ID: {file.id}, Filename: {file.filename}, Created: {file.created_at}")
        if not all_files:
            print("No files found in database")
    except Exception as e:
        print(f"Error listing files: {e}")
    finally:
        session.close()

# Test the functionality
if __name__ == "__main__":
    # Example usage
    file_data = {
        'id': 'unique_id_789',
        'filename': 'another_test.pdf',
        's3_key': 'files/another_test.pdf',
        'share_id': 'share_789',
        'owner': 'test2@example.com',
        'file_size': 3072,
        'file_type': 'pdf'
    }
    
    print("Saving file...")
    save_shared_file(file_data)
    
    print("\nListing all files...")
    list_all_files()