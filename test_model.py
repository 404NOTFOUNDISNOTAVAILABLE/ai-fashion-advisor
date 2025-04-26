from app import app, db
from modules.outfit_generator import SavedOutfit

# Print all models registered with SQLAlchemy
print("Registered models:")
for model in db.Model.__subclasses__():
    print(f" - {model.__name__}")

# Check if SavedOutfit is in the list
if SavedOutfit in db.Model.__subclasses__():
    print("SavedOutfit is properly registered!")
else:
    print("SavedOutfit is NOT registered correctly!")