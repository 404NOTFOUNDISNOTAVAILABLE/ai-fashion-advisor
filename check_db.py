from app import app, db
import sqlite3
import os

try:
    with app.app_context():
        # Print app config for debugging
        print("Database URI:", app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set'))
        
        # Get the database path
        if 'SQLALCHEMY_DATABASE_URI' in app.config:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print("Database path:", db_path)
            
            # Check if file exists
            if os.path.exists(db_path):
                print(f"Database file exists at: {db_path}")
            else:
                print(f"Database file does NOT exist at: {db_path}")
                
            # Try to connect
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                print("\nTables in database:")
                for table in tables:
                    print(f" - {table[0]}")
                
                conn.close()
            except Exception as e:
                print(f"Error connecting to database: {e}")
        else:
            print("SQLALCHEMY_DATABASE_URI not found in app config")
except Exception as e:
    print(f"Error: {e}")