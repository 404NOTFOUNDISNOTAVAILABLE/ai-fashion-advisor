import sqlite3
import os

print("Script is running!")

# Use the database filename we found
db_filename = "fashion_advisor.db"

if os.path.exists(db_filename):
    print(f"Database file exists: {db_filename}")
    
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        
        # Create the saved_outfits table directly
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            top_id INTEGER REFERENCES wardrobe_items(id),
            bottom_id INTEGER REFERENCES wardrobe_items(id),
            outerwear_id INTEGER REFERENCES wardrobe_items(id),
            footwear_id INTEGER REFERENCES wardrobe_items(id),
            accessory_id INTEGER REFERENCES wardrobe_items(id),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        print("Table created successfully!")
        
        # Verify the table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_outfits';")
        if cursor.fetchone():
            print("saved_outfits table now exists in the database")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(saved_outfits);")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f" - {col[1]} ({col[2]})")
        else:
            print("ERROR: saved_outfits table was NOT created")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
else:
    print(f"Database file does NOT exist: {db_filename}")