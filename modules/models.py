from modules.database import db
import datetime
import json
import numpy as np

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    else:
        return obj

class WardrobeItem(db.Model):
    """Model for clothing items in the wardrobe"""
    __tablename__ = 'wardrobe_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50))
    image_path = db.Column(db.String(200), nullable=False)
    features = db.Column(db.Text)  # JSON string of extracted features
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, name, category, color, season, image_path, features=None):
        self.name = name
        self.category = category
        self.color = color
        self.season = season
        self.image_path = image_path
        
        if features:
            # Convert NumPy types before JSON serialization
            features = convert_numpy_types(features)
            self.features = json.dumps(features)
        else:
            self.features = json.dumps({})
    
    def __repr__(self):
        return f'<WardrobeItem {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'season': self.season,
            'image_path': self.image_path,
            'features': self.features,
            'date_added': self.date_added.isoformat() if self.date_added else None
    }