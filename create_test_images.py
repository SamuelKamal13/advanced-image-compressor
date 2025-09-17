"""
Test Images Generator
Creates sample images for testing the compression tools.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np

def create_test_images(output_dir="test_images"):
    """Create various test images for compression testing."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating test images in {output_dir}/")
    
    # 1. High-resolution photo-like image
    create_photo_like_image(output_dir, "photo_test.jpg", (2048, 1536))
    
    # 2. Simple graphics with few colors
    create_simple_graphic(output_dir, "graphic_test.png", (800, 600))
    
    # 3. Image with transparency
    create_transparent_image(output_dir, "transparent_test.png", (600, 400))
    
    # 4. Complex pattern
    create_pattern_image(output_dir, "pattern_test.png", (1024, 768))
    
    # 5. Screenshot-like image
    create_screenshot_like(output_dir, "screenshot_test.png", (1920, 1080))
    
    # 6. Large high-quality image
    create_large_image(output_dir, "large_test.jpg", (4000, 3000))
    
    print("✅ Test images created successfully!")
    print("\nTest Images Summary:")
    
    for filename in os.listdir(output_dir):
        if filename.endswith(('.jpg', '.png')):
            filepath = os.path.join(output_dir, filename)
            size = os.path.getsize(filepath)
            with Image.open(filepath) as img:
                dimensions = f"{img.width}x{img.height}"
            print(f"  📁 {filename}: {dimensions}, {size/1024/1024:.1f} MB")

def create_photo_like_image(output_dir, filename, size):
    """Create a photo-like image with gradients and noise."""
    width, height = size
    
    # Create base gradient
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    # Create radial gradient
    for y in range(height):
        for x in range(width):
            # Distance from center
            center_x, center_y = width // 2, height // 2
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            max_distance = (width ** 2 + height ** 2) ** 0.5
            
            # Color based on distance and position
            red = int(255 * (1 - distance / max_distance) * (x / width))
            green = int(255 * (y / height) * (1 - distance / max_distance))
            blue = int(255 * (distance / max_distance) * (1 - y / height))
            
            # Add some noise
            noise = random.randint(-20, 20)
            red = max(0, min(255, red + noise))
            green = max(0, min(255, green + noise))
            blue = max(0, min(255, blue + noise))
            
            img.putpixel((x, y), (red, green, blue))
    
    # Add some geometric shapes
    draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], 
                fill=(255, 255, 0, 128))
    
    img.save(os.path.join(output_dir, filename), quality=95)

def create_simple_graphic(output_dir, filename, size):
    """Create a simple graphic with few colors."""
    width, height = size
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Background
    draw.rectangle([0, 0, width, height], fill='#f0f8ff')
    
    # Simple shapes
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7']
    
    # Rectangles
    for i in range(5):
        x1 = i * width // 5
        y1 = height // 4
        x2 = (i + 1) * width // 5 - 10
        y2 = 3 * height // 4
        draw.rectangle([x1, y1, x2, y2], fill=colors[i])
    
    # Text
    try:
        # Try to use a system font
        font_size = 48
        font = ImageFont.load_default()
        text = "GRAPHICS TEST"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height // 8
        draw.text((x, y), text, fill='black', font=font)
    except:
        pass
    
    img.save(os.path.join(output_dir, filename))

def create_transparent_image(output_dir, filename, size):
    """Create an image with transparency."""
    width, height = size
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Semi-transparent circles
    for i in range(10):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(20, 100)
        alpha = random.randint(50, 200)
        color = (random.randint(0, 255), random.randint(0, 255), 
                random.randint(0, 255), alpha)
        
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=color)
    
    img.save(os.path.join(output_dir, filename))

def create_pattern_image(output_dir, filename, size):
    """Create a complex pattern image."""
    width, height = size
    img = Image.new('RGB', size)
    
    # Create numpy array for complex patterns
    array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            # Complex mathematical pattern
            r = int(128 + 127 * np.sin(x * 0.01) * np.cos(y * 0.01))
            g = int(128 + 127 * np.sin((x + y) * 0.005))
            b = int(128 + 127 * np.cos(x * 0.008) * np.sin(y * 0.008))
            
            array[y, x] = [r, g, b]
    
    img = Image.fromarray(array)
    img.save(os.path.join(output_dir, filename))

def create_screenshot_like(output_dir, filename, size):
    """Create a screenshot-like image."""
    width, height = size
    img = Image.new('RGB', size, color='#2c3e50')
    draw = ImageDraw.Draw(img)
    
    # Window-like interface
    # Title bar
    draw.rectangle([50, 50, width-50, 100], fill='#34495e')
    draw.rectangle([50, 100, width-50, height-50], fill='white')
    
    # Sidebar
    draw.rectangle([70, 120, 250, height-70], fill='#ecf0f1')
    
    # Content area with text-like rectangles
    for i in range(20):
        x1 = 270 + random.randint(0, 50)
        y1 = 140 + i * 25 + random.randint(0, 10)
        x2 = x1 + random.randint(200, 400)
        y2 = y1 + 15
        gray = random.randint(100, 200)
        draw.rectangle([x1, y1, x2, y2], fill=(gray, gray, gray))
    
    # Buttons
    button_colors = ['#3498db', '#e74c3c', '#2ecc71']
    for i, color in enumerate(button_colors):
        x = 270 + i * 120
        y = height - 100
        draw.rectangle([x, y, x + 100, y + 40], fill=color)
    
    img.save(os.path.join(output_dir, filename))

def create_large_image(output_dir, filename, size):
    """Create a large, high-quality image."""
    width, height = size
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    # Create a landscape-like image
    # Sky gradient
    for y in range(height // 2):
        blue = int(135 + (255 - 135) * (1 - y / (height // 2)))
        draw.line([(0, y), (width, y)], fill=(100, 150, blue))
    
    # Ground
    for y in range(height // 2, height):
        green = int(50 + 100 * ((y - height // 2) / (height // 2)))
        draw.line([(0, y), (width, y)], fill=(green, 120, 50))
    
    # Add some "mountains"
    mountain_points = []
    for x in range(0, width, 20):
        y = height // 2 + int(50 * np.sin(x * 0.01)) - random.randint(0, 100)
        mountain_points.append((x, y))
    mountain_points.append((width, height))
    mountain_points.append((0, height))
    
    draw.polygon(mountain_points, fill='#8b7355')
    
    img.save(os.path.join(output_dir, filename), quality=100)

if __name__ == "__main__":
    try:
        import numpy as np
        create_test_images()
    except ImportError:
        print("❌ NumPy required for test image generation")
        print("Install with: pip install numpy")
        print("Or create test images manually.")