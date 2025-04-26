import random
from collections import defaultdict
from modules.models import WardrobeItem
from modules.database import db
from sqlalchemy import or_

# Color compatibility rules
COLOR_COMPATIBILITY = {
    'Black': ['White', 'Gray', 'Red', 'Blue', 'Green', 'Purple', 'Pink', 'Yellow', 'Orange'],
    'White': ['Black', 'Gray', 'Blue', 'Red', 'Purple', 'Pink', 'Green', 'Brown'],
    'Gray': ['Black', 'White', 'Blue', 'Red', 'Purple', 'Pink'],
    'Blue': ['White', 'Gray', 'Black', 'Beige', 'Brown', 'Green', 'Purple'],
    'Red': ['Black', 'White', 'Gray', 'Beige', 'Brown'],
    'Green': ['Black', 'White', 'Beige', 'Brown', 'Blue', 'Gray'],
    'Purple': ['White', 'Gray', 'Black', 'Pink', 'Blue'],
    'Pink': ['White', 'Gray', 'Black', 'Purple', 'Blue'],
    'Yellow': ['Black', 'Blue', 'Purple', 'Gray'],
    'Orange': ['Black', 'Blue', 'White', 'Gray'],
    'Brown': ['White', 'Blue', 'Green', 'Beige', 'Gray'],
    'Beige': ['Brown', 'Blue', 'Green', 'Red', 'Black']
}

# Style compatibility - which categories go well together
STYLE_COMPATIBILITY = {
    'Casual': ['tops', 'bottoms', 'outerwear', 'footwear', 'accessories'],
    'Formal': ['tops', 'bottoms', 'outerwear', 'footwear', 'accessories'],
    'Business': ['tops', 'bottoms', 'outerwear', 'footwear', 'accessories'],
    'Athletic': ['tops', 'bottoms', 'footwear', 'accessories']
}

# Season-specific category rules
SEASON_CATEGORY_RULES = {
    'summer': {
        'include': ['tops', 'bottoms', 'footwear', 'accessories'],
        'exclude': ['outerwear']  # Generally don't include outerwear in summer outfits
    },
    'winter': {
        'include': ['tops', 'bottoms', 'outerwear', 'footwear', 'accessories'],
        'required': ['outerwear']  # Outerwear is important for winter
    },
    'spring': {
        'include': ['tops', 'bottoms', 'footwear', 'accessories'],
        'optional': ['outerwear']  # Light outerwear sometimes for spring
    },
    'fall': {
        'include': ['tops', 'bottoms', 'outerwear', 'footwear', 'accessories'],
        'recommended': ['outerwear']  # Outerwear recommended but not required for fall
    }
}

class ClothingItem:
    def __init__(self, id, name, category, color, image_path):
        self.id = id
        self.name = name
        self.category = category
        self.color = color
        self.image_path = image_path

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'image': '/uploads/' + self.image_path if self.image_path and not self.image_path.startswith('/') else self.image_path
        }

class OutfitGenerator:
    """Generate outfit recommendations based on wardrobe items"""
    
    def __init__(self, season=None, style=None, color_scheme=None):
        """
        Initialize the outfit generator with optional filters
        
        Args:
            season: Optional season to filter by
            style: Optional style to filter by
            color_scheme: Optional color scheme to use
        """
        self.season = season
        self.style = style
        self.color_scheme = color_scheme
    
    def generate_outfit(self):
        """
        Generate a complete outfit based on available wardrobe items
        
        Returns:
            Dictionary with outfit items by category
        """
        # Get all items from wardrobe with appropriate filters
        query = WardrobeItem.query
        
        # Filter by season if specified and not "Any"
        if self.season and self.season != 'Any':
            # Convert season to lowercase to match database values
            season_lower = self.season.lower()
            
            # Include items that match the season OR are marked as "all" seasons
            query = query.filter(or_(WardrobeItem.season == season_lower, 
                                    WardrobeItem.season == 'all'))
        
        all_items = query.all()
        
        if not all_items:
            return {"error": "Your wardrobe is empty or no items match the selected filters. Try different filters or add more items."}
        
        # Group items by category
        items_by_category = {}
        for item in all_items:
            if item.category not in items_by_category:
                items_by_category[item.category] = []
            items_by_category[item.category].append(item)
        
        # Check if we have enough categories for a complete outfit
        required_categories = ['tops', 'bottoms']
        for category in required_categories:
            if category not in items_by_category or not items_by_category[category]:
                return {"error": f"You need at least one {category} item that matches your filters for an outfit"}
        
        # Start with a top
        selected_top = random.choice(items_by_category['tops'])
        
        # Find compatible bottoms based on color
        compatible_bottoms = []
        if 'bottoms' in items_by_category:
            for bottom in items_by_category['bottoms']:
                if self._are_colors_compatible(selected_top.color, bottom.color):
                    compatible_bottoms.append(bottom)
        
        if not compatible_bottoms and 'bottoms' in items_by_category:
            # If no compatible bottoms, just use any bottom
            compatible_bottoms = items_by_category['bottoms']
        
        selected_bottom = random.choice(compatible_bottoms) if compatible_bottoms else None
        
        # Build the outfit
        outfit = {
            "tops": selected_top,
            "bottoms": selected_bottom
        }
        
        # Get season-specific rules
        season_rules = {}
        if self.season and self.season != 'Any':
            season_lower = self.season.lower()
            season_rules = SEASON_CATEGORY_RULES.get(season_lower, {})
        
        # Add optional items if available, considering season rules
        optional_categories = ['outerwear', 'footwear', 'accessories']
        for category in optional_categories:
            # Skip categories excluded for this season
            if 'exclude' in season_rules and category in season_rules['exclude']:
                continue
                
            # Only include categories appropriate for this season
            if 'include' in season_rules and category not in season_rules['include']:
                continue
                
            # For summer, add outerwear only 10% of the time (very rarely)
            if category == 'outerwear' and self.season and self.season.lower() == 'summer':
                if random.random() > 0.1:  # 90% chance to skip outerwear in summer
                    continue
            
            # For spring, add outerwear only 40% of the time (occasionally)
            if category == 'outerwear' and self.season and self.season.lower() == 'spring':
                if random.random() > 0.4:  # 60% chance to skip outerwear in spring
                    continue
            
            if category in items_by_category and items_by_category[category]:
                # Try to find a compatible item
                compatible_items = []
                for item in items_by_category[category]:
                    if self._are_colors_compatible(selected_top.color, item.color) or \
                       (selected_bottom and self._are_colors_compatible(selected_bottom.color, item.color)):
                        compatible_items.append(item)
                
                if not compatible_items:
                    # If no compatible items, just use any item from this category
                    compatible_items = items_by_category[category]
                
                outfit[category] = random.choice(compatible_items)
        
        return outfit
    
    def generate_multiple_outfits(self, count=3):
        """
        Generate multiple outfit options
        
        Args:
            count: Number of outfits to generate
            
        Returns:
            List of outfit dictionaries
        """
        outfits = []
        max_attempts = count * 3  # Try more times than needed to get unique outfits
        attempts = 0
        
        while len(outfits) < count and attempts < max_attempts:
            outfit = self.generate_outfit()
            if "error" in outfit:
                return [outfit]  # Return the error
            
            # Check if this outfit is unique (not exactly the same as previous outfits)
            is_unique = True
            for existing_outfit in outfits:
                if (existing_outfit.get('tops') == outfit.get('tops') and 
                    existing_outfit.get('bottoms') == outfit.get('bottoms')):
                    is_unique = False
                    break
            
            if is_unique:
                outfits.append(outfit)
            
            attempts += 1
        
        return outfits
    
    def _are_colors_compatible(self, color1, color2):
        """
        Check if two colors are compatible based on color theory
        
        Args:
            color1: First color
            color2: Second color
            
        Returns:
            Boolean indicating if colors are compatible
        """
        # Same colors are always compatible
        if color1 == color2:
            return True
        
        # Check color compatibility rules
        if color1 in COLOR_COMPATIBILITY and color2 in COLOR_COMPATIBILITY[color1]:
            return True
        
        if color2 in COLOR_COMPATIBILITY and color1 in COLOR_COMPATIBILITY[color2]:
            return True
        
        # Default compatibility for colors not in our rules
        return False

# Create a model for saved outfits
class SavedOutfit(db.Model):
    """Model for saved outfit combinations"""
    __tablename__ = 'saved_outfits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    top_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'))
    bottom_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'))
    outerwear_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'), nullable=True)
    footwear_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'), nullable=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Define relationships
    top = db.relationship('WardrobeItem', foreign_keys=[top_id])
    bottom = db.relationship('WardrobeItem', foreign_keys=[bottom_id])
    outerwear = db.relationship('WardrobeItem', foreign_keys=[outerwear_id])
    footwear = db.relationship('WardrobeItem', foreign_keys=[footwear_id])
    accessory = db.relationship('WardrobeItem', foreign_keys=[accessory_id])
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'top': self.top.to_dict() if self.top else None,
            'bottom': self.bottom.to_dict() if self.bottom else None,
            'outerwear': self.outerwear.to_dict() if self.outerwear else None,
            'footwear': self.footwear.to_dict() if self.footwear else None,
            'accessory': self.accessory.to_dict() if self.accessory else None,
            'date_created': self.date_created.isoformat() if self.date_created else None
        }

if __name__ == '__main__':
    # Example Usage
    items = [
        ClothingItem(1, "Blue Shirt", "top", "blue", "blue_shirt.jpg"),
        ClothingItem(2, "Red Shirt", "top", "red", "red_shirt.jpg"),
        ClothingItem(3, "Black Pants", "bottom", "black", "black_pants.jpg"),
        ClothingItem(4, "Blue Jeans", "bottom", "blue", "blue_jeans.jpg"),
        ClothingItem(5, "Sneakers", "shoes", "white", "sneakers.jpg"),
        ClothingItem(6, "Boots", "shoes", "black", "boots.jpg"),
        ClothingItem(7, "Hat", "accessory", "red", "hat.jpg"),
        ClothingItem(8, "Scarf", "accessory", "blue", "scarf.jpg")
    ]

    generator = OutfitGenerator()
    #generator = OutfitGenerator(items)
    #outfit = generator.generate_outfit()
    outfits = generator.generate_multiple_outfits(count=2)

    #for category, items in outfit.items():
    #    print(f"Category: {category}")
    #    for item in items:
    #        print(f"  - {item['name']} ({item['color']}) - Image: {item['image']}")
    for outfit in outfits:
        print("Outfit:")
        for category, item in outfit.items():
            if category != "error":
                print(f"  {category}: {item.name} ({item.color})")
            else:
                print(f"  Error: {item}")
