from modules.models import WardrobeItem
from modules.database import db
from flask import Flask
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

def debug_winter_query():
    with app.app_context():
        print("Testing winter season query:")
        
        # This is the exact query used in the outfit generator
        winter_items = WardrobeItem.query.filter(
            or_(WardrobeItem.season == 'winter', WardrobeItem.season == 'All')
        ).all()
        
        print(f"Total items found: {len(winter_items)}")
        
        # Group by category
        by_category = {}
        for item in winter_items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)
        
        # Print items by category
        for category, items in by_category.items():
            print(f"\n{category}: {len(items)} items")
            for item in items:
                print(f"  - {item.name} (Season: {item.season})")
        
        # Check specifically for bottoms
        bottoms = WardrobeItem.query.filter(
            WardrobeItem.category == 'bottoms'
        ).all()
        
        print("\nAll bottoms in database:")
        for item in bottoms:
            print(f"  - {item.name} (Season: {item.season})")
        
        # Check case sensitivity
        print("\nChecking for case sensitivity issues:")
        seasons = db.session.query(WardrobeItem.season).distinct().all()
        print(f"All season values in database: {[s[0] for s in seasons]}")
        
        # Try different case variations
        for season_var in ['winter', 'Winter', 'WINTER', 'all', 'All', 'ALL']:
            count = WardrobeItem.query.filter_by(season=season_var).count()
            print(f"Items with season='{season_var}': {count}")

if __name__ == "__main__":
    debug_winter_query()
