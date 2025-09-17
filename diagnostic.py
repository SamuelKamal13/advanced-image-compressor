#!/usr/bin/env python3
"""
Image Diagnostic Tool
Diagnose and repair problematic image files.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageFile
import argparse
from image_compressor import ImageCompressor, format_size

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

class ImageDiagnostic:
    """Diagnostic tool for problematic image files."""
    
    def __init__(self):
        self.compressor = ImageCompressor()
    
    def diagnose_file(self, file_path: str, verbose: bool = True) -> dict:
        """Comprehensive diagnostic of an image file."""
        print(f"🔍 Diagnosing: {file_path}")
        print("=" * 50)
        
        # Basic file checks
        if not os.path.exists(file_path):
            print("❌ File does not exist!")
            return {'status': 'file_not_found'}
        
        file_size = os.path.getsize(file_path)
        print(f"📁 File size: {format_size(file_size)}")
        
        if file_size == 0:
            print("❌ File is empty (0 bytes)")
            return {'status': 'empty_file'}
        
        # Check file extension
        ext = Path(file_path).suffix.lower()
        print(f"📎 Extension: {ext}")
        
        # Use our enhanced validation
        validation = self.compressor.validate_image_file(file_path)
        
        print(f"\n📊 Validation Results:")
        print(f"   Valid: {'✅ Yes' if validation['is_valid'] else '❌ No'}")
        print(f"   Readable: {'✅ Yes' if validation['is_readable'] else '❌ No'}")
        print(f"   Format detected: {validation['format_detected'] or 'Unknown'}")
        
        if validation['error_message']:
            print(f"   Error: {validation['error_message']}")
            
        if validation['suggestions']:
            print(f"\n💡 Suggestions:")
            for i, suggestion in enumerate(validation['suggestions'], 1):
                print(f"   {i}. {suggestion}")
        
        # Try different approaches to read the file
        print(f"\n🔧 Attempting different read methods:")
        
        # Method 1: Standard PIL
        try:
            with Image.open(file_path) as img:
                img.load()
                print("   ✅ Standard PIL: Success")
                print(f"      Format: {img.format}, Mode: {img.mode}, Size: {img.size}")
        except Exception as e:
            print(f"   ❌ Standard PIL: {e}")
        
        # Method 2: With truncated images enabled
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            with Image.open(file_path) as img:
                img.load()
                print("   ✅ Truncated loading: Success")
                print(f"      Format: {img.format}, Mode: {img.mode}, Size: {img.size}")
        except Exception as e:
            print(f"   ❌ Truncated loading: {e}")
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
        
        # Method 3: Try to verify without loading
        try:
            with Image.open(file_path) as img:
                print("   ✅ Open without load: Success")
                print(f"      Format: {img.format}, Mode: {img.mode}")
        except Exception as e:
            print(f"   ❌ Open without load: {e}")
        
        # Check if it's a JPEG-specific issue
        if ext in ['.jpg', '.jpeg']:
            self._diagnose_jpeg_specific(file_path)
        
        return validation
    
    def _diagnose_jpeg_specific(self, file_path: str):
        """JPEG-specific diagnostics."""
        print(f"\n📸 JPEG-Specific Diagnostics:")
        
        # Check for common JPEG issues
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
                
                # Check JPEG signature
                if header[:3] == b'\xff\xd8\xff':
                    print("   ✅ Valid JPEG signature")
                else:
                    print("   ❌ Invalid JPEG signature")
                    print(f"      Header: {header.hex()}")
                
                # Read the end of file
                f.seek(-10, 2)  # Go to 10 bytes before end
                tail = f.read()
                
                if tail.endswith(b'\xff\xd9'):
                    print("   ✅ Valid JPEG end marker")
                else:
                    print("   ⚠️  Missing or invalid JPEG end marker")
                    print("      File might be truncated")
                    
        except Exception as e:
            print(f"   ❌ Error reading file structure: {e}")
    
    def attempt_repair(self, file_path: str, output_path: str = None) -> bool:
        """Attempt to repair a corrupted image file."""
        if output_path is None:
            name = Path(file_path).stem
            ext = Path(file_path).suffix
            output_path = str(Path(file_path).parent / f"{name}_repaired{ext}")
        
        print(f"\n🔧 Attempting repair...")
        print(f"   Input: {file_path}")
        print(f"   Output: {output_path}")
        
        repair_methods = [
            ("Enable truncated loading", self._repair_truncated),
            ("Force RGB conversion", self._repair_force_rgb),
            ("Strip and resave", self._repair_strip_resave),
        ]
        
        for method_name, method_func in repair_methods:
            print(f"\n   Trying: {method_name}")
            try:
                if method_func(file_path, output_path):
                    print(f"   ✅ Success with {method_name}")
                    
                    # Verify the repaired file
                    validation = self.compressor.validate_image_file(output_path)
                    if validation['is_valid']:
                        print(f"   ✅ Repaired file is valid")
                        return True
                    else:
                        print(f"   ⚠️  Repaired file still has issues")
                        
            except Exception as e:
                print(f"   ❌ {method_name} failed: {e}")
        
        print("   ❌ All repair methods failed")
        return False
    
    def _repair_truncated(self, input_path: str, output_path: str) -> bool:
        """Repair using truncated image loading."""
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            with Image.open(input_path) as img:
                img.load()
                img.save(output_path, quality=95, optimize=True)
                return True
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
    
    def _repair_force_rgb(self, input_path: str, output_path: str) -> bool:
        """Repair by forcing RGB conversion."""
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
    
    def _repair_strip_resave(self, input_path: str, output_path: str) -> bool:
        """Repair by stripping metadata and resaving."""
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            with Image.open(input_path) as img:
                # Create new image without metadata
                new_img = Image.new(img.mode, img.size)
                new_img.putdata(list(img.getdata()))
                
                if new_img.mode != 'RGB':
                    new_img = new_img.convert('RGB')
                    
                new_img.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

def main():
    """Main diagnostic function."""
    parser = argparse.ArgumentParser(
        description="Diagnose and repair problematic image files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python diagnostic.py BOB_5931.jpg                    # Diagnose file
  python diagnostic.py BOB_5931.jpg --repair           # Attempt repair
  python diagnostic.py BOB_5931.jpg --repair --output fixed.jpg
        """
    )
    
    parser.add_argument('image_file', help='Image file to diagnose')
    parser.add_argument('--repair', action='store_true', 
                       help='Attempt to repair the image')
    parser.add_argument('--output', help='Output path for repaired image')
    parser.add_argument('--verbose', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    diagnostic = ImageDiagnostic()
    
    # Run diagnosis
    result = diagnostic.diagnose_file(args.image_file, args.verbose)
    
    # Attempt repair if requested
    if args.repair:
        if diagnostic.attempt_repair(args.image_file, args.output):
            print(f"\n🎉 Repair completed successfully!")
            
            # Try to compress the repaired file
            print(f"\n🔄 Testing compression on repaired file...")
            if args.output:
                test_result = diagnostic.compressor.compress_image(args.output)
                if test_result['success']:
                    print(f"✅ Compression test successful!")
                    print(f"   Size reduction: {test_result['compression_ratio']:.1f}%")
                else:
                    print(f"❌ Compression test failed: {test_result['error']}")
        else:
            print(f"\n❌ Repair failed - file may be too corrupted")
            print(f"\nAlternative solutions:")
            print(f"1. Try opening in GIMP or Photoshop and re-saving")
            print(f"2. Use online image repair tools")
            print(f"3. Re-download or re-scan the original image")

if __name__ == "__main__":
    main()