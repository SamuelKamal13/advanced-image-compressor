#!/usr/bin/env python3
"""
Test script for auto-repair functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from image_compressor import ImageCompressor
from PIL import Image
import numpy as np

def create_test_image(path, size=(100, 100), format='JPEG'):
    """Create a test image."""
    # Create a simple test image with gradient
    arr = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    for i in range(size[1]):
        for j in range(size[0]):
            arr[i, j] = [i % 256, j % 256, (i + j) % 256]
    
    img = Image.fromarray(arr)
    img.save(path, format=format, quality=95)
    return path

def create_corrupted_image(source_path, corrupt_path):
    """Create a corrupted version of an image by truncating it."""
    with open(source_path, 'rb') as src:
        data = src.read()
    
    # Truncate the image data (remove last 30% of data)
    truncated_data = data[:int(len(data) * 0.7)]
    
    with open(corrupt_path, 'wb') as dst:
        dst.write(truncated_data)
    
    return corrupt_path

def test_auto_repair():
    """Test auto-repair functionality."""
    print("🧪 Testing Auto-Repair Functionality")
    print("=" * 50)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test image
        print("1. Creating test image...")
        test_image = temp_path / "test_image.jpg"
        create_test_image(test_image)
        print(f"   ✅ Created: {test_image}")
        
        # Create corrupted version
        print("\n2. Creating corrupted image...")
        corrupted_image = temp_path / "corrupted_image.jpg"
        create_corrupted_image(test_image, corrupted_image)
        print(f"   ✅ Created: {corrupted_image}")
        
        # Test without auto-repair
        print("\n3. Testing compression WITHOUT auto-repair...")
        compressor_no_repair = ImageCompressor(auto_repair=False)
        output_no_repair = temp_path / "output_no_repair.jpg"
        
        result_no_repair = compressor_no_repair.compress_image(
            str(corrupted_image),
            str(output_no_repair),
            quality_preset="balanced"
        )
        
        print(f"   Result: {'✅ Success' if result_no_repair['success'] else '❌ Failed'}")
        if not result_no_repair['success']:
            print(f"   Error: {result_no_repair['error']}")
        
        # Test WITH auto-repair
        print("\n4. Testing compression WITH auto-repair...")
        compressor_with_repair = ImageCompressor(auto_repair=True)
        output_with_repair = temp_path / "output_with_repair.jpg"
        
        result_with_repair = compressor_with_repair.compress_image(
            str(corrupted_image),
            str(output_with_repair),
            quality_preset="balanced"
        )
        
        print(f"   Result: {'✅ Success' if result_with_repair['success'] else '❌ Failed'}")
        if result_with_repair['success']:
            if result_with_repair.get('was_auto_repaired', False):
                repair_method = result_with_repair.get('repair_method', 'unknown')
                print(f"   🔧 Auto-repaired using: {repair_method}")
                print(f"   📊 Compression ratio: {result_with_repair['compression_ratio']:.1f}%")
                print(f"   📏 Size: {result_with_repair['original_size']} → {result_with_repair['compressed_size']} bytes")
            else:
                print("   ℹ️  No repair was needed")
        else:
            print(f"   Error: {result_with_repair['error']}")
        
        # Test normal image (should not trigger repair)
        print("\n5. Testing normal image (should not trigger repair)...")
        output_normal = temp_path / "output_normal.jpg"
        
        result_normal = compressor_with_repair.compress_image(
            str(test_image),
            str(output_normal),
            quality_preset="balanced"
        )
        
        print(f"   Result: {'✅ Success' if result_normal['success'] else '❌ Failed'}")
        if result_normal['success']:
            if result_normal.get('was_auto_repaired', False):
                print("   ⚠️  Unexpected: repair was triggered for normal image")
            else:
                print("   ✅ No repair triggered (expected)")
                print(f"   📊 Compression ratio: {result_normal['compression_ratio']:.1f}%")
        
        # Clean up
        print("\n6. Cleaning up temporary files...")
        compressor_with_repair.cleanup_temp_files()
        compressor_no_repair.cleanup_temp_files()
        print("   ✅ Cleanup complete")
    
    print("\n" + "=" * 50)
    print("🎯 Auto-Repair Test Complete!")
    
    # Summary
    print("\n📋 Summary:")
    print(f"   Without auto-repair: {'✅ Handled gracefully' if not result_no_repair['success'] else '⚠️  Unexpected success'}")
    print(f"   With auto-repair: {'✅ Successfully repaired' if result_with_repair['success'] and result_with_repair.get('was_auto_repaired') else '❌ Failed to repair'}")
    print(f"   Normal image: {'✅ Processed normally' if result_normal['success'] and not result_normal.get('was_auto_repaired') else '❌ Unexpected behavior'}")

if __name__ == "__main__":
    test_auto_repair()