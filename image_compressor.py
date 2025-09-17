"""
Advanced Image Compressor
Reduces file size while maintaining quality and resolution using optimal compression algorithms.
"""

import os
import sys
from PIL import Image, ImageFile
from PIL.ExifTags import TAGS
import logging
from typing import Dict, Tuple, Optional, List
from pathlib import Path
import tempfile
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageCompressor:
    """Advanced image compressor with quality preservation and automatic repair."""
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
    
    # Optimal quality settings for different compression levels
    QUALITY_PRESETS = {
        'maximum': {'jpeg': 95, 'webp': 85, 'png_optimize': True},
        'high': {'jpeg': 88, 'webp': 80, 'png_optimize': True},
        'balanced': {'jpeg': 82, 'webp': 75, 'png_optimize': True},
        'small': {'jpeg': 75, 'webp': 70, 'png_optimize': True}
    }
    
    def __init__(self, auto_repair: bool = True):
        """Initialize the image compressor.
        
        Args:
            auto_repair: Enable automatic repair of corrupted images
        """
        self.processed_files = []
        self.errors = []
        self.auto_repair = auto_repair
        self.repaired_files = []  # Track files that were automatically repaired
    
    def validate_image_file(self, image_path: str) -> Dict:
        """Validate an image file and return detailed diagnostic info."""
        validation_result = {
            'is_valid': False,
            'file_exists': False,
            'file_size': 0,
            'is_readable': False,
            'format_detected': None,
            'error_message': None,
            'suggestions': []
        }
        
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                validation_result['error_message'] = "File does not exist"
                validation_result['suggestions'].append("Check the file path")
                return validation_result
            
            validation_result['file_exists'] = True
            validation_result['file_size'] = os.path.getsize(image_path)
            
            # Check if file is empty
            if validation_result['file_size'] == 0:
                validation_result['error_message'] = "File is empty (0 bytes)"
                validation_result['suggestions'].append("Re-download or recreate the file")
                return validation_result
            
            # Check if file is too small to be a valid image
            if validation_result['file_size'] < 100:
                validation_result['error_message'] = "File too small to be a valid image"
                validation_result['suggestions'].append("File may be corrupted or truncated")
                return validation_result
            
            # Try to open and verify the image
            try:
                with Image.open(image_path) as img:
                    # Force loading the image data
                    img.load()
                    validation_result['is_readable'] = True
                    validation_result['format_detected'] = img.format
                    validation_result['is_valid'] = True
                    
            except Image.UnidentifiedImageError:
                validation_result['error_message'] = "Cannot identify image format"
                validation_result['suggestions'].extend([
                    "File may not be a valid image",
                    "Check file extension matches content",
                    "Try opening in image viewer first"
                ])
                
            except OSError as e:
                if "broken data stream" in str(e).lower():
                    validation_result['error_message'] = "Broken data stream - corrupted image file"
                    validation_result['suggestions'].extend([
                        "File is corrupted or truncated",
                        "Try re-downloading the image",
                        "Use image repair tools",
                        "Convert with another tool first"
                    ])
                elif "truncated" in str(e).lower():
                    validation_result['error_message'] = "Image file is truncated"
                    validation_result['suggestions'].extend([
                        "Download was incomplete",
                        "File transfer was interrupted",
                        "Re-download the original file"
                    ])
                else:
                    validation_result['error_message'] = f"PIL/Pillow error: {e}"
                    validation_result['suggestions'].append("Try opening with different image software")
                    
            except MemoryError:
                validation_result['error_message'] = "Image too large for available memory"
                validation_result['suggestions'].extend([
                    "Reduce image size before processing",
                    "Use image editing software to resize first",
                    "Process on machine with more RAM"
                ])
                
        except Exception as e:
            validation_result['error_message'] = f"Unexpected error: {e}"
            validation_result['suggestions'].append("Contact support with this error message")
            
        return validation_result

    def attempt_auto_repair(self, image_path: str) -> Optional[str]:
        """Automatically attempt to repair a corrupted image file.
        
        Args:
            image_path: Path to the corrupted image
            
        Returns:
            Path to repaired temporary file if successful, None if failed
        """
        if not self.auto_repair:
            return None
        
        logger.info(f"🔧 Attempting automatic repair for {image_path}")
        
        # Create temporary file for repair attempt
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"repaired_{Path(image_path).name}")
        
        repair_methods = [
            ("truncated loading", self._repair_truncated),
            ("force RGB conversion", self._repair_force_rgb),
            ("strip metadata", self._repair_strip_metadata),
        ]
        
        for method_name, method_func in repair_methods:
            try:
                logger.info(f"   Trying: {method_name}")
                if method_func(image_path, temp_file):
                    # Verify the repaired file
                    validation = self.validate_image_file(temp_file)
                    if validation['is_valid']:
                        logger.info(f"   ✅ Auto-repair successful with {method_name}")
                        self.repaired_files.append({
                            'original_path': image_path,
                            'repair_method': method_name,
                            'temp_file': temp_file
                        })
                        return temp_file
                    else:
                        # Remove failed repair attempt
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                        
            except Exception as e:
                logger.debug(f"   Repair method {method_name} failed: {e}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                continue
        
        # Cleanup temp directory if all methods failed
        try:
            os.rmdir(temp_dir)
        except:
            pass
            
        logger.warning(f"   ❌ All auto-repair methods failed for {image_path}")
        return None
    
    def _repair_truncated(self, input_path: str, output_path: str) -> bool:
        """Repair using truncated image loading."""
        original_setting = ImageFile.LOAD_TRUNCATED_IMAGES
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            with Image.open(input_path) as img:
                img.load()
                # Save as JPEG with high quality to standardize
                if img.mode in ('RGBA', 'LA'):
                    # Convert to RGB for JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img, mask=img.split()[1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                img.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        except Exception:
            return False
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = original_setting
    
    def _repair_force_rgb(self, input_path: str, output_path: str) -> bool:
        """Repair by forcing RGB conversion with error tolerance."""
        original_setting = ImageFile.LOAD_TRUNCATED_IMAGES
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            with Image.open(input_path) as img:
                # Force load and convert to RGB
                if img.mode != 'RGB':
                    if img.mode in ('RGBA', 'LA'):
                        # Handle transparency
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img, mask=img.split()[1])
                        img = background
                    else:
                        img = img.convert('RGB')
                
                img.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        except Exception:
            return False
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = original_setting
    
    def _repair_strip_metadata(self, input_path: str, output_path: str) -> bool:
        """Repair by stripping all metadata and creating clean image."""
        original_setting = ImageFile.LOAD_TRUNCATED_IMAGES
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            with Image.open(input_path) as img:
                # Create new image without any metadata
                if img.mode in ('RGBA', 'LA'):
                    # Convert to RGB
                    new_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        new_img.paste(img, mask=img.split()[-1])
                    else:
                        new_img.paste(img, mask=img.split()[1])
                else:
                    new_img = Image.new(img.mode, img.size)
                    new_img.putdata(list(img.getdata()))
                    if new_img.mode != 'RGB':
                        new_img = new_img.convert('RGB')
                
                new_img.save(output_path, 'JPEG', quality=95, optimize=True)
                return True
        except Exception:
            return False
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = original_setting

    def cleanup_temp_files(self):
        """Clean up any temporary files created during auto-repair."""
        for repair_info in self.repaired_files:
            temp_file = repair_info['temp_file']
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    # Also try to remove the temp directory if empty
                    temp_dir = os.path.dirname(temp_file)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except Exception:
                    pass  # Ignore cleanup errors
        self.repaired_files.clear()

    def get_image_info(self, image_path: str) -> Dict:
        """Get detailed information about an image file."""
        try:
            # First validate the file
            validation = self.validate_image_file(image_path)
            if not validation['is_valid']:
                logger.warning(f"Invalid image file {image_path}: {validation['error_message']}")
                return {'validation': validation}
            
            with Image.open(image_path) as img:
                # Force load to catch any data issues early
                img.load()
                
                # Get basic info
                info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.size[0],
                    'height': img.size[1],
                    'file_size': os.path.getsize(image_path),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'validation': validation
                }
                
                # Get EXIF data if available
                try:
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        info['exif'] = {TAGS.get(tag, tag): value for tag, value in exif.items()}
                except Exception:
                    # EXIF reading can fail even if image is valid
                    pass
                
                return info
        except Exception as e:
            logger.error(f"Error getting info for {image_path}: {e}")
            return {'validation': self.validate_image_file(image_path)}
    
    def optimize_jpeg(self, img: Image.Image, quality: int = 85, 
                     preserve_exif: bool = True) -> Dict:
        """Optimize JPEG compression with advanced settings."""
        save_kwargs = {
            'format': 'JPEG',
            'quality': quality,
            'optimize': True,
            'progressive': True,  # Progressive JPEG for better perceived loading
        }
        
        # Preserve EXIF data if requested
        if preserve_exif and hasattr(img, 'info') and 'exif' in img.info:
            save_kwargs['exif'] = img.info['exif']
        
        return save_kwargs
    
    def optimize_png(self, img: Image.Image, optimize: bool = True) -> Dict:
        """Optimize PNG compression with advanced settings."""
        save_kwargs = {
            'format': 'PNG',
            'optimize': optimize,
            'compress_level': 9,  # Maximum compression
        }
        
        # For RGBA images, check if we can reduce to RGB
        if img.mode == 'RGBA':
            # Check if image actually uses transparency
            if not self._has_actual_transparency(img):
                # Convert to RGB to reduce file size
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1])
                return save_kwargs, rgb_img
        
        return save_kwargs, img
    
    def optimize_webp(self, img: Image.Image, quality: int = 80, 
                     lossless: bool = False) -> Dict:
        """Optimize WebP compression with advanced settings."""
        save_kwargs = {
            'format': 'WEBP',
            'quality': quality if not lossless else 100,
            'method': 6,  # Maximum compression effort
            'lossless': lossless,
        }
        
        # Use lossless for images with transparency or specific modes
        if img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
            save_kwargs['lossless'] = True
            save_kwargs['quality'] = 100
        
        return save_kwargs
    
    def _has_actual_transparency(self, img: Image.Image) -> bool:
        """Check if RGBA image actually uses transparency."""
        if img.mode != 'RGBA':
            return False
        
        # Sample a few pixels to check for transparency
        alpha_channel = img.split()[-1]
        alpha_values = list(alpha_channel.getdata())
        
        # If all alpha values are 255, no real transparency
        return not all(alpha == 255 for alpha in alpha_values[:1000])  # Sample first 1000 pixels
    
    def compress_image(self, input_path: str, output_path: str = None, 
                      quality_preset: str = 'balanced', 
                      target_format: str = None,
                      preserve_exif: bool = True,
                      max_size_mb: float = None) -> Dict:
        """
        Compress a single image with advanced optimization.
        
        Args:
            input_path: Path to input image
            output_path: Path to save compressed image (optional)
            quality_preset: Quality preset ('maximum', 'high', 'balanced', 'small')
            target_format: Target format ('jpeg', 'png', 'webp', None for same format)
            preserve_exif: Whether to preserve EXIF data
            max_size_mb: Maximum file size in MB (will adjust quality if needed)
        
        Returns:
            Dictionary with compression results
        """
        try:
            # Initialize variables
            was_repaired = False
            actual_input_path = input_path
            
            # Validate input file first
            validation = self.validate_image_file(input_path)
            if not validation['is_valid']:
                # Attempt automatic repair if enabled
                if self.auto_repair:
                    logger.info(f"🔧 File validation failed, attempting auto-repair for {input_path}")
                    repaired_path = self.attempt_auto_repair(input_path)
                    
                    if repaired_path:
                        logger.info(f"✅ Auto-repair successful, using repaired file")
                        # Use the repaired file for compression
                        actual_input_path = repaired_path
                        was_repaired = True
                    else:
                        # Auto-repair failed, return error with suggestions
                        error_msg = f"Invalid image file (auto-repair failed): {validation['error_message']}"
                        logger.error(f"Auto-repair failed for {input_path}: {error_msg}")
                        
                        result = {
                            'success': False,
                            'input_path': input_path,
                            'error': error_msg,
                            'validation': validation,
                            'suggestions': validation['suggestions'] + [
                                "Auto-repair was attempted but failed",
                                "Try using the diagnostic tool manually: python diagnostic.py " + Path(input_path).name,
                                "Consider using professional image repair software"
                            ]
                        }
                        self.errors.append(error_msg)
                        return result
                else:
                    # Auto-repair disabled, return validation error
                    error_msg = f"Invalid image file: {validation['error_message']}"
                    logger.error(f"Validation failed for {input_path}: {error_msg}")
                    
                    result = {
                        'success': False,
                        'input_path': input_path,
                        'error': error_msg,
                        'validation': validation,
                        'suggestions': validation['suggestions']
                    }
                    self.errors.append(error_msg)
                    return result
            else:
                # File is valid, use original path
                actual_input_path = input_path
                was_repaired = False
            
            file_ext = Path(input_path).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {file_ext}")
            
            # Set output path if not provided
            if output_path is None:
                name = Path(input_path).stem
                ext = target_format if target_format else file_ext.lstrip('.')
                output_path = str(Path(input_path).parent / f"{name}_compressed.{ext}")
            
            # Get original file info
            original_size = os.path.getsize(input_path)
            
            # Open and process image with enhanced error handling
            try:
                with Image.open(actual_input_path) as img:
                    # Force load the image data to catch corruption early
                    img.load()
                    
                    original_format = img.format
                    original_mode = img.mode
                    
                    # Convert to RGB if necessary for JPEG
                    if target_format == 'jpeg' and img.mode in ('RGBA', 'LA', 'P'):
                        if img.mode == 'P' and 'transparency' in img.info:
                            img = img.convert('RGBA')
                        
                        if img.mode in ('RGBA', 'LA'):
                            # Create white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[-1])
                            else:
                                background.paste(img, mask=img.split()[1])
                            img = background
                        else:
                            img = img.convert('RGB')
                    
                    # Determine target format
                    if target_format is None:
                        if original_format.lower() == 'jpeg':
                            target_format = 'jpeg'
                        elif original_format.lower() == 'png':
                            target_format = 'png'
                        else:
                            target_format = 'jpeg'  # Default to JPEG for other formats
                    
                    # Get quality settings
                    quality_settings = self.QUALITY_PRESETS.get(quality_preset, self.QUALITY_PRESETS['balanced'])
                    
                    # Optimize based on target format
                    compressed_img = img.copy()
                    
                    if target_format.lower() == 'jpeg':
                        save_kwargs = self.optimize_jpeg(
                            compressed_img, 
                            quality_settings['jpeg'], 
                            preserve_exif
                        )
                        
                    elif target_format.lower() == 'png':
                        save_kwargs, compressed_img = self.optimize_png(
                            compressed_img, 
                            quality_settings['png_optimize']
                        )
                        
                    elif target_format.lower() == 'webp':
                        save_kwargs = self.optimize_webp(
                            compressed_img, 
                            quality_settings['webp']
                        )
                    
                    # Adjust quality if max_size_mb is specified
                    if max_size_mb:
                        save_kwargs = self._adjust_quality_for_size(
                            compressed_img, save_kwargs, max_size_mb * 1024 * 1024
                        )
                    
                    # Save compressed image
                    compressed_img.save(output_path, **save_kwargs)
                    
            except OSError as e:
                if "broken data stream" in str(e).lower():
                    error_msg = f"Corrupted image file - broken data stream: {e}"
                    suggestions = [
                        "The image file is corrupted or truncated",
                        "Try re-downloading the original image",
                        "Use image repair software",
                        "Convert with another tool first (e.g., GIMP, Photoshop)"
                    ]
                elif "truncated" in str(e).lower():
                    error_msg = f"Image file is truncated: {e}"
                    suggestions = [
                        "The file download was incomplete",
                        "Re-download the original file",
                        "Check file integrity"
                    ]
                else:
                    error_msg = f"Image processing error: {e}"
                    suggestions = ["Try with a different image editing tool"]
                
                logger.error(f"OSError processing {input_path}: {error_msg}")
                result = {
                    'success': False,
                    'input_path': input_path,
                    'error': error_msg,
                    'suggestions': suggestions
                }
                self.errors.append(error_msg)
                return result
                
            except MemoryError as e:
                error_msg = f"Image too large for available memory: {e}"
                suggestions = [
                    "Reduce image size before processing",
                    "Use image editing software to resize first",
                    "Process on machine with more RAM"
                ]
                logger.error(f"MemoryError processing {input_path}: {error_msg}")
                result = {
                    'success': False,
                    'input_path': input_path,
                    'error': error_msg,
                    'suggestions': suggestions
                }
                self.errors.append(error_msg)
                return result
            
            # Calculate compression results
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (original_size - compressed_size) / original_size * 100
            
            result = {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'size_reduction_bytes': original_size - compressed_size,
                'compression_ratio': compression_ratio,
                'original_format': original_format,
                'target_format': target_format.upper(),
                'quality_preset': quality_preset,
                'was_auto_repaired': was_repaired
            }
            
            if was_repaired:
                # Add repair information to the result
                repair_info = next((r for r in self.repaired_files if r['temp_file'] == actual_input_path), None)
                if repair_info:
                    result['repair_method'] = repair_info['repair_method']
                    result['repair_note'] = f"File was automatically repaired using {repair_info['repair_method']}"
                    logger.info(f"✅ Compressed auto-repaired file: {compression_ratio:.1f}% size reduction")
                
            self.processed_files.append(result)
            logger.info(f"Compressed {input_path}: {compression_ratio:.1f}% size reduction")
            
            return result
            
        except Exception as e:
            error_msg = f"Error compressing {input_path}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                'success': False,
                'input_path': input_path,
                'error': str(e)
            }
    
    def _adjust_quality_for_size(self, img: Image.Image, save_kwargs: Dict, 
                                target_size: int) -> Dict:
        """Adjust quality settings to meet target file size."""
        import io
        
        if save_kwargs['format'] not in ['JPEG', 'WEBP']:
            return save_kwargs  # Can't adjust quality for PNG
        
        # Binary search for optimal quality
        min_quality = 10
        max_quality = save_kwargs.get('quality', 85)
        best_kwargs = save_kwargs.copy()
        
        for _ in range(10):  # Max 10 iterations
            current_quality = (min_quality + max_quality) // 2
            test_kwargs = save_kwargs.copy()
            test_kwargs['quality'] = current_quality
            
            # Test file size
            buffer = io.BytesIO()
            img.save(buffer, **test_kwargs)
            current_size = buffer.tell()
            
            if current_size <= target_size:
                best_kwargs = test_kwargs.copy()
                min_quality = current_quality + 1
            else:
                max_quality = current_quality - 1
            
            if min_quality >= max_quality:
                break
        
        return best_kwargs
    
    def compress_batch(self, input_paths: List[str], output_dir: str = None,
                      quality_preset: str = 'balanced',
                      target_format: str = None,
                      preserve_structure: bool = True) -> Dict:
        """
        Compress multiple images in batch.
        
        Args:
            input_paths: List of input image paths or directories
            output_dir: Directory to save compressed images
            quality_preset: Quality preset for compression
            target_format: Target format for all images
            preserve_structure: Whether to preserve directory structure
        
        Returns:
            Dictionary with batch processing results
        """
        all_files = []
        
        # Collect all image files
        for path in input_paths:
            if os.path.isfile(path):
                all_files.append(path)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS:
                            all_files.append(file_path)
        
        # Set output directory
        if output_dir is None:
            output_dir = "compressed_images"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each file
        results = []
        for i, file_path in enumerate(all_files):
            logger.info(f"Processing {i+1}/{len(all_files)}: {file_path}")
            
            # Determine output path
            if preserve_structure and len(input_paths) == 1 and os.path.isdir(input_paths[0]):
                # Preserve directory structure
                rel_path = os.path.relpath(file_path, input_paths[0])
                output_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                # Flat structure
                filename = Path(file_path).name
                output_path = os.path.join(output_dir, filename)
            
            # Compress image
            result = self.compress_image(
                file_path, output_path, quality_preset, target_format
            )
            results.append(result)
        
        # Clean up any temporary files created during auto-repair
        self.cleanup_temp_files()
        
        # Calculate batch statistics
        successful = [r for r in results if r.get('success', False)]
        total_original_size = sum(r.get('original_size', 0) for r in successful)
        total_compressed_size = sum(r.get('compressed_size', 0) for r in successful)
        total_reduction = total_original_size - total_compressed_size
        avg_compression = (total_reduction / total_original_size * 100) if total_original_size > 0 else 0
        
        batch_result = {
            'total_files': len(all_files),
            'successful': len(successful),
            'failed': len(results) - len(successful),
            'total_original_size': total_original_size,
            'total_compressed_size': total_compressed_size,
            'total_size_reduction': total_reduction,
            'average_compression_ratio': avg_compression,
            'output_directory': output_dir,
            'results': results
        }
        
        logger.info(f"Batch compression complete: {len(successful)}/{len(all_files)} files processed")
        logger.info(f"Total size reduction: {avg_compression:.1f}%")
        
        return batch_result

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    # Example usage
    compressor = ImageCompressor()
    
    # Example: Compress a single image
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        result = compressor.compress_image(input_file, quality_preset='balanced')
        
        if result['success']:
            print(f"✅ Compression successful!")
            print(f"Original size: {format_size(result['original_size'])}")
            print(f"Compressed size: {format_size(result['compressed_size'])}")
            print(f"Size reduction: {result['compression_ratio']:.1f}%")
            print(f"Output: {result['output_path']}")
        else:
            print(f"❌ Compression failed: {result['error']}")
    else:
        print("Image Compressor - Advanced image compression tool")
        print("Usage: python image_compressor.py <image_file>")
        print("\nSupported formats: JPEG, PNG, WebP, TIFF, BMP")
        print("Quality presets: maximum, high, balanced, small")