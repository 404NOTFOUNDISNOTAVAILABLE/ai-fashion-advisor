import cv2
import numpy as np
from sklearn.cluster import KMeans
import time
import os
import json

# Color name mapping - RGB values to color names
COLOR_NAMES = {
    # Black, white, gray
    (0, 0, 0): 'Black',
    (255, 255, 255): 'White',
    (128, 128, 128): 'Gray',
    (169, 169, 169): 'Dark Gray',
    (211, 211, 211): 'Light Gray',
    
    # Red shades
    (255, 0, 0): 'Red',
    (178, 34, 34): 'Dark Red',
    (220, 20, 60): 'Crimson',
    (255, 99, 71): 'Tomato',
    (255, 127, 80): 'Coral',
    
    # Pink shades
    (255, 192, 203): 'Pink',
    (255, 105, 180): 'Hot Pink',
    (219, 112, 147): 'Pale Violet Red',
    
    # Orange shades
    (255, 165, 0): 'Orange',
    (255, 140, 0): 'Dark Orange',
    (255, 69, 0): 'Red-Orange',
    
    # Yellow shades
    (255, 255, 0): 'Yellow',
    (255, 215, 0): 'Gold',
    (240, 230, 140): 'Khaki',
    
    # Green shades
    (0, 128, 0): 'Green',
    (34, 139, 34): 'Forest Green',
    (0, 255, 0): 'Lime',
    (50, 205, 50): 'Lime Green',
    (152, 251, 152): 'Pale Green',
    (0, 255, 127): 'Spring Green',
    (46, 139, 87): 'Sea Green',
    (60, 179, 113): 'Medium Sea Green',
    (32, 178, 170): 'Light Sea Green',
    (0, 128, 128): 'Teal',
    
    # Blue shades
    (0, 0, 255): 'Blue',
    (0, 0, 139): 'Dark Blue',
    (0, 0, 205): 'Medium Blue',
    (65, 105, 225): 'Royal Blue',
    (100, 149, 237): 'Cornflower Blue',
    (135, 206, 235): 'Sky Blue',
    (173, 216, 230): 'Light Blue',
    (176, 224, 230): 'Powder Blue',
    (95, 158, 160): 'Cadet Blue',
    (70, 130, 180): 'Steel Blue',
    (30, 144, 255): 'Dodger Blue',
    (0, 191, 255): 'Deep Sky Blue',
    
    # Purple shades
    (128, 0, 128): 'Purple',
    (148, 0, 211): 'Dark Violet',
    (153, 50, 204): 'Dark Orchid',
    (138, 43, 226): 'Blue Violet',
    (147, 112, 219): 'Medium Purple',
    (186, 85, 211): 'Medium Orchid',
    (218, 112, 214): 'Orchid',
    (221, 160, 221): 'Plum',
    (238, 130, 238): 'Violet',
    (255, 0, 255): 'Magenta',
    (255, 20, 147): 'Deep Pink',
    
    # Brown shades
    (165, 42, 42): 'Brown',
    (139, 69, 19): 'Saddle Brown',
    (160, 82, 45): 'Sienna',
    (210, 105, 30): 'Chocolate',
    (205, 133, 63): 'Peru',
    (222, 184, 135): 'Burlywood',
    (245, 245, 220): 'Beige',
    (250, 235, 215): 'Antique White',
    (255, 228, 196): 'Bisque',
    (255, 222, 173): 'Navajo White',
    (245, 222, 179): 'Wheat',
    (210, 180, 140): 'Tan'
}

def analyze_garment(image_path):
    """
    Analyze a garment image to identify colors and basic attributes.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with name, category, and color information
    """
    # Simulate some processing time to show the AI is "thinking"
    time.sleep(0.5)
    
    try:
        # Extract dominant colors
        colors = extract_dominant_colors(image_path)
        
        if not colors:
            raise Exception("Could not extract colors from image")
        
        # Get the primary color (most dominant)
        primary_color = colors[0]['name']
        
        # For now, we'll use placeholder values for category
        # In Phase 4, we'll implement actual classification
        category = "tops"  # Default category
        
        # Generate a name based on color and category
        name = f"{primary_color} {category.rstrip('s').capitalize()}"
        
        # Create a feature vector for the item
        # This will be used for outfit matching in later phases
        features = {
            'colors': [{'rgb': c['rgb'], 'percentage': c['percentage']} for c in colors],
            'primary_color': primary_color,
            # More features will be added in Phase 4
        }
        
        return {
            "name": name,
            "category": category,
            "color": primary_color,
            "features": features,
            "color_analysis": colors  # Include detailed color analysis
        }
    except Exception as e:
        print(f"Error analyzing image: {e}")
        # Fallback to default values if analysis fails
        return {
            "name": "Unknown Item",
            "category": "tops",  # Default category
            "color": "Blue",     # Default color
            "features": {},
            "color_analysis": []
        }

def extract_dominant_colors(image_path, n_colors=5):
    """
    Extract the dominant colors from an image using K-means clustering.
    
    Args:
        image_path: Path to the image file
        n_colors: Number of dominant colors to extract
        
    Returns:
        List of dictionaries with color information
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"Could not read image at {image_path}")
    
    # Convert to RGB (OpenCV uses BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize image to speed up processing
    # Resizing to a smaller size still gives good color results
    # and dramatically speeds up processing
    max_size = 300  # Max width or height
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        if h > w:
            new_h, new_w = max_size, int(w * max_size / h)
        else:
            new_h, new_w = int(h * max_size / w), max_size
        image = cv2.resize(image, (new_w, new_h))
    
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    kmeans.fit(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_
    
    # Convert to integer RGB values
    colors = colors.astype(int)
    
    # Get percentage of each color
    labels = kmeans.labels_
    counts = np.bincount(labels)
    percentages = counts / len(labels)
    
    # Sort colors by percentage
    color_info = []
    for i in range(len(colors)):
        rgb = tuple(colors[i])
        color_name = find_closest_color(rgb)
        percentage = percentages[i] * 100  # Convert to percentage
        
        color_info.append({
            'rgb': rgb,
            'name': color_name,
            'percentage': percentage
        })
    
    # Sort by percentage (highest first)
    color_info = sorted(color_info, key=lambda x: x['percentage'], reverse=True)
    
    return color_info

def find_closest_color(rgb_tuple):
    """
    Find the closest named color to an RGB value.
    
    Args:
        rgb_tuple: Tuple of (R, G, B) values
        
    Returns:
        String name of the closest color
    """
    r, g, b = rgb_tuple
    min_distance = float('inf')
    closest_color = "Unknown"
    
    for color_rgb, color_name in COLOR_NAMES.items():
        cr, cg, cb = color_rgb
        # Calculate Euclidean distance in RGB space
        distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_color = color_name
    
    return closest_color

def save_color_analysis_image(image_path, colors, output_path):
    """
    Create a visualization of the color analysis and save it.
    
    Args:
        image_path: Path to the original image
        colors: List of color dictionaries from extract_dominant_colors
        output_path: Path to save the visualization
        
    Returns:
        Path to the saved visualization
    """
    # Load original image
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"Could not read image at {image_path}")
    
    # Convert to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize image if it's too large
    max_width = 400
    h, w = image.shape[:2]
    if w > max_width:
        h = int(h * max_width / w)
        w = max_width
        image = cv2.resize(image, (w, h))
    
    # Create a blank image for the color palette
    palette_height = 50
    palette_width = w
    palette = np.zeros((palette_height, palette_width, 3), dtype=np.uint8)
    
    # Fill the palette with the dominant colors
    if colors:
        # Calculate width for each color based on its percentage
        total_percentage = sum(c['percentage'] for c in colors)
        x_start = 0
        
        for color in colors:
            # Calculate width proportional to color percentage
            width = int(palette_width * (color['percentage'] / total_percentage))
            if width == 0:
                width = 1  # Ensure at least 1 pixel width
            
            # Fill the section with this color
            r, g, b = color['rgb']
            palette[:, x_start:x_start+width] = [r, g, b]
            
            x_start += width
    
    # Combine original image and palette
    combined = np.vstack((image, palette))
    
    # Add text labels for colors
    combined = cv2.cvtColor(combined, cv2.COLOR_RGB2BGR)  # Convert back to BGR for OpenCV
    y_text = h + 20  # Position text in the middle of the palette
    x_start = 10
    
    for i, color in enumerate(colors[:3]):  # Show top 3 colors
        percentage = color['percentage']
        color_name = color['name']
        text = f"{color_name}: {percentage:.1f}%"
        
        # Add white outline for better visibility
        cv2.putText(combined, text, (x_start-1, y_text-1), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(combined, text, (x_start, y_text), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        x_start += 130  # Space between color labels
    
    # Save the visualization
    cv2.imwrite(output_path, combined)
    
    return output_path