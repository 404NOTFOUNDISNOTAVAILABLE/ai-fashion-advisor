from app import app, db
import sqlite3

with app.app_context():
    # Get the database path from your app config
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables in database:")
    for table in tables:
        print(f" - {table[0]}")
    
    # Check specifically for saved_outfits
    if ('saved_outfits',) in tables:
        print("\nsaved_outfits table already exists!")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(saved_outfits);")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f" - {col[1]} ({col[2]})")
    else:
        print("\nsaved_outfits table does NOT exist!")
    
    conn.close()