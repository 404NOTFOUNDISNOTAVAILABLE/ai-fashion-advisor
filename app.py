from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from modules.database import db, init_app
from modules.models import WardrobeItem
from modules.garment_analyzer import analyze_garment, save_color_analysis_image
from modules.outfit_generator import OutfitGenerator, SavedOutfit

# Create Flask application
app = Flask(__name__)

# Load configuration
app.config.from_pyfile('config.py')

# Initialize database with Flask-SQLAlchemy
init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Ensure upload directory exists
upload_dir = os.path.join('static', app.config['UPLOAD_FOLDER'])
os.makedirs(upload_dir, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image using AI"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Save temporarily
        temp_filename = 'temp_' + secure_filename(file.filename)
        temp_path = os.path.join(upload_dir, temp_filename)
        file.save(temp_path)
        
        # Analyze the image
        analysis = analyze_garment(temp_path)
        
        # Create color analysis visualization if the function exists
        if analysis.get('color_analysis') and 'save_color_analysis_image' in globals():
            viz_filename = 'color_analysis_' + temp_filename
            viz_path = os.path.join(upload_dir, viz_filename)
            try:
                save_color_analysis_image(temp_path, analysis['color_analysis'], viz_path)
                analysis['color_visualization'] = os.path.join(app.config['UPLOAD_FOLDER'], viz_filename)
            except Exception as e:
                print(f"Error creating color visualization: {e}")
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(analysis)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file uploads and garment information"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            
            # Create uploads directory inside static if it doesn't exist
            upload_dir = os.path.join('static', app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file to the static/uploads directory
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Get form data
            name = request.form.get('name')
            category = request.form.get('category')
            color = request.form.get('color')
            season = request.form.get('season')
            
            # Analyze the image to extract features
            # We need to pass the full path for analysis
            analysis = analyze_garment(filepath)
            features = analysis.get('features', {})
            
            # Store the path relative to the static folder for url_for to work
            # This is the key change - store only the relative path from static
            relative_path = app.config['UPLOAD_FOLDER'] + '/' + filename
            
            item = WardrobeItem(
                name=name,
                category=category,
                color=color,
                season=season,
                image_path=relative_path,  # This should be like 'uploads/filename.jpg'
                features=features
            )
            
            # Use Flask-SQLAlchemy's session
            db.session.add(item)
            db.session.commit()
            
            flash('Item added successfully!', 'success')
            return redirect(url_for('wardrobe'))
        else:
            flash('Invalid file type. Please upload an image.', 'error')
            return redirect(request.url)
            
    return render_template('upload.html')

@app.route('/wardrobe')
def wardrobe():
    """Display the user's wardrobe"""
    items = WardrobeItem.query.order_by(WardrobeItem.date_added.desc()).all()
    return render_template('wardrobe.html', items=items)

@app.route('/delete-item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    """Delete an item from the wardrobe"""
    # Now we can use get_or_404 with Flask-SQLAlchemy
    item = WardrobeItem.query.get_or_404(item_id)
    
    # Delete the image file
    try:
        # Correct path for deletion
        file_path = os.path.join(app.root_path, 'static', item.image_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log the error but continue
        print(f"Error deleting file: {e}")
    
    # Delete from database using Flask-SQLAlchemy's session
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('wardrobe'))

@app.route('/outfits')
def outfits():
    """Display outfit generation page"""
    # Count items by category to check if we have enough for outfits
    tops_count = WardrobeItem.query.filter_by(category='tops').count()
    bottoms_count = WardrobeItem.query.filter_by(category='bottoms').count()
    item_count = tops_count + bottoms_count
    
    return render_template('outfits.html', item_count=item_count)

@app.route('/generate-outfits')
def generate_outfits():
    """Generate outfit recommendations"""
    # Get filter parameters
    season = request.args.get('season')
    style = request.args.get('style')
    color_scheme = request.args.get('color_scheme')
    
    # Create outfit generator
    generator = OutfitGenerator(season=season, style=style, color_scheme=color_scheme)
    
    # Generate outfits
    outfits = generator.generate_multiple_outfits(count=3)
    
    # Check for errors
    if outfits and "error" in outfits[0]:
        return jsonify({"error": outfits[0]["error"]})
    
    # Convert outfit items to dictionaries for JSON serialization
    serialized_outfits = []
    for outfit in outfits:
        serialized_outfit = {}
        for category, item in outfit.items():
            if item:
                serialized_outfit[category] = item.to_dict()
        serialized_outfits.append(serialized_outfit)
    
    return jsonify({"outfits": serialized_outfits})

@app.route('/save-outfit', methods=['POST'])
def save_outfit():
    """Save an outfit to the database"""
    data = request.json
    
    if not data or 'name' not in data or 'tops' not in data or 'bottoms' not in data:
        return jsonify({"success": False, "error": "Invalid outfit data"})
    
    try:
        # Create new saved outfit
        outfit = SavedOutfit(
            name=data['name'],
            top_id=data['tops']['id'],
            bottom_id=data['bottoms']['id'],
            outerwear_id=data.get('outerwear', {}).get('id'),
            footwear_id=data.get('footwear', {}).get('id'),
            accessory_id=data.get('accessories', {}).get('id')
        )
        
        db.session.add(outfit)
        db.session.commit()
        
        return jsonify({"success": True, "outfit_id": outfit.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route('/saved-outfits')
def saved_outfits():
    """Display saved outfits"""
    outfits = SavedOutfit.query.order_by(SavedOutfit.date_created.desc()).all()
    return render_template('saved_outfits.html', outfits=outfits)

@app.route('/delete-outfit/<int:outfit_id>', methods=['POST'])
def delete_outfit(outfit_id):
    """Delete a saved outfit"""
    outfit = SavedOutfit.query.get_or_404(outfit_id)
    
    db.session.delete(outfit)
    db.session.commit()
    
    flash('Outfit deleted successfully!', 'success')
    return redirect(url_for('saved_outfits'))

@app.route('/fix-image-paths')
def fix_image_paths():
    """Fix image paths for existing items"""
    items = WardrobeItem.query.all()
    fixed_count = 0
    
    for item in items:
        # If path starts with 'static/'
        if item.image_path.startswith('static/'):
            # Remove 'static/' prefix
            item.image_path = item.image_path[7:]  # 'static/' is 7 characters
            fixed_count += 1
        # If path doesn't start with 'uploads/'
        elif not item.image_path.startswith(app.config['UPLOAD_FOLDER']):
            # Get just the filename
            filename = os.path.basename(item.image_path)
            # Set the correct path
            item.image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            fixed_count += 1
    
    if fixed_count > 0:
        db.session.commit()
        return f"Fixed {fixed_count} image paths"
    else:
        return "No paths needed fixing"

# Run the application
if __name__ == '__main__':
    app.run(debug=True)