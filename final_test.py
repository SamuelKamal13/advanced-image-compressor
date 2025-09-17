#!/usr/bin/env python3
"""
Test with minimal output to verify auto-repair works.
"""

import tempfile
import subprocess
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def main():
    """Test auto-repair functionality without Unicode issues."""
    print("Testing Auto-Repair Functionality")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create normal image
        normal_path = temp_path / "normal.jpg"
        arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
        img.save(normal_path, format='JPEG', quality=90)
        
        # Create corrupted image
        corrupted_path = temp_path / "corrupted.jpg"
        with open(normal_path, 'rb') as src:
            data = src.read()
        truncated_data = data[:int(len(data) * 0.7)]
        with open(corrupted_path, 'wb') as dst:
            dst.write(truncated_data)
        
        # Import and test Python API directly
        print("1. Testing Python API auto-repair...")
        
        sys.path.insert(0, str(Path(__file__).parent))
        from image_compressor import ImageCompressor
        
        # Test with auto-repair
        compressor = ImageCompressor(auto_repair=True)
        result = compressor.compress_image(
            str(corrupted_path),
            str(temp_path / "repaired.jpg")
        )
        
        if result['success']:
            print("   SUCCESS: Auto-repair worked!")
            if result.get('was_auto_repaired'):
                print(f"   Repair method: {result.get('repair_method', 'unknown')}")
                print(f"   Compression: {result['compression_ratio']:.1f}%")
            else:
                print("   No repair was needed")
        else:
            print(f"   FAILED: {result['error']}")
        
        # Test without auto-repair
        compressor_no_repair = ImageCompressor(auto_repair=False)
        result_no_repair = compressor_no_repair.compress_image(
            str(corrupted_path),
            str(temp_path / "no_repair.jpg")
        )
        
        print("2. Testing without auto-repair...")
        if result_no_repair['success']:
            print("   SUCCESS: Processed without repair")
        else:
            print(f"   FAILED: {result_no_repair['error']}")
        
        # Summary
        print("\n" + "=" * 40)
        print("SUMMARY:")
        print(f"  With auto-repair: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"  Without auto-repair: {'SUCCESS' if result_no_repair['success'] else 'FAILED'}")
        
        if result['success'] and not result_no_repair['success']:
            print("  CONCLUSION: Auto-repair is working correctly!")
            return True
        else:
            print("  CONCLUSION: Something needs investigation")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)