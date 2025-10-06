"""
Database migration script to add file_data and file_size columns
Run this once to update the existing database schema
"""
from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Add file_data column
            db.session.execute(text("""
                ALTER TABLE datasets 
                ADD COLUMN IF NOT EXISTS file_data BYTEA;
            """))
            print("✅ Added file_data column")
            
            # Add file_size column
            db.session.execute(text("""
                ALTER TABLE datasets 
                ADD COLUMN IF NOT EXISTS file_size INTEGER;
            """))
            print("✅ Added file_size column")
            
            # Make file_path nullable (no longer required)
            db.session.execute(text("""
                ALTER TABLE datasets 
                ALTER COLUMN file_path DROP NOT NULL;
            """))
            print("✅ Made file_path nullable")
            
            db.session.commit()
            print("\n🎉 Database migration completed successfully!")
            print("Your application is now ready to store files in Neon database.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration error: {str(e)}")
            print("This might be okay if columns already exist.")

if __name__ == "__main__":
    migrate()

