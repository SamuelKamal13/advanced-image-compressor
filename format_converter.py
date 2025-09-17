"""
Advanced Format Converter
Specialized tool for converting between image formats with optimal settings.
"""

import os
from pathlib import Path
from PIL import Image
import logging
from typing import Dict, List, Optional, Tuple
from image_compressor import ImageCompressor, format_size

logger = logging.getLogger(__name__)

class ImageFormatConverter:
    """Advanced image format converter with optimal settings for each format."""
    
    # Format-specific optimal settings
    FORMAT_CONFIGS = {
        'jpeg': {
            'quality_ranges': {'high': 92, 'medium': 85, 'low': 75},
            'supports_transparency': False,
            'supports_animation': False,
            'recommended_for': ['photos', 'natural_images'],
            'file_size': 'small_to_medium'
        },
        'png': {
            'quality_ranges': {'high': 9, 'medium': 6, 'low': 3},  # compression levels
            'supports_transparency': True,
            'supports_animation': False,
            'recommended_for': ['graphics', 'logos', 'screenshots'],
            'file_size': 'medium_to_large'
        },
        'webp': {
            'quality_ranges': {'high': 90, 'medium': 80, 'low': 70},
            'supports_transparency': True,
            'supports_animation': True,
            'recommended_for': ['web', 'modern_browsers'],
            'file_size': 'small'
        },
        'tiff': {
            'supports_transparency': True,
            'supports_animation': False,
            'recommended_for': ['professional', 'archival'],
            'file_size': 'large'
        },
        'bmp': {
            'supports_transparency': False,
            'supports_animation': False,
            'recommended_for': ['simple_graphics'],
            'file_size': 'very_large'
        }
    }
    
    def __init__(self):
        self.compressor = ImageCompressor()
        self.conversion_results = []
    
    def analyze_image_characteristics(self, image_path: str) -> Dict:
        """Analyze image to recommend optimal format."""
        try:
            with Image.open(image_path) as img:
                # Basic properties
                has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                is_grayscale = img.mode in ('L', 'LA')
                is_palette = img.mode == 'P'
                
                # Color analysis
                colors = img.getcolors(maxcolors=256*256*256)
                unique_colors = len(colors) if colors else None
                
                # Complexity analysis (simplified)
                # Convert to grayscale for analysis
                gray_img = img.convert('L')
                edges = self._detect_edges_simple(gray_img)
                
                characteristics = {
                    'width': img.size[0],
                    'height': img.size[1],
                    'mode': img.mode,
                    'has_transparency': has_transparency,
                    'is_grayscale': is_grayscale,
                    'is_palette': is_palette,
                    'unique_colors': unique_colors,
                    'is_simple_graphics': unique_colors and unique_colors < 256,
                    'is_complex_photo': unique_colors is None or unique_colors > 10000,
                    'has_many_edges': edges > 0.1,  # Simplified edge detection
                    'file_size': os.path.getsize(image_path)
                }
                
                return characteristics
                
        except Exception as e:
            logger.error(f"Error analyzing {image_path}: {e}")
            return {}
    
    def _detect_edges_simple(self, gray_img: Image.Image) -> float:
        """Simple edge detection for image complexity analysis."""
        try:
            # Resize for faster processing
            small_img = gray_img.resize((100, 100))
            pixels = list(small_img.getdata())
            
            # Simple gradient calculation
            edges = 0
            width, height = small_img.size
            
            for y in range(height - 1):
                for x in range(width - 1):
                    current = pixels[y * width + x]
                    right = pixels[y * width + (x + 1)]
                    down = pixels[(y + 1) * width + x]
                    
                    grad = abs(current - right) + abs(current - down)
                    if grad > 30:  # Threshold for edge
                        edges += 1
            
            return edges / (width * height)
            
        except Exception:
            return 0.0
    
    def recommend_format(self, image_path: str, target_use: str = 'web') -> Dict:
        """Recommend optimal format based on image characteristics and use case."""
        characteristics = self.analyze_image_characteristics(image_path)
        
        if not characteristics:
            return {'recommended_format': 'jpeg', 'reason': 'Default fallback'}
        
        recommendations = []
        
        # Format selection logic
        if characteristics.get('has_transparency'):
            if target_use == 'web':
                recommendations.append({
                    'format': 'webp',
                    'reason': 'WebP supports transparency and is web-optimized',
                    'score': 9
                })
                recommendations.append({
                    'format': 'png',
                    'reason': 'PNG supports transparency with good compatibility',
                    'score': 7
                })
            else:
                recommendations.append({
                    'format': 'png',
                    'reason': 'PNG is best for transparency',
                    'score': 9
                })
        
        elif characteristics.get('is_simple_graphics'):
            recommendations.append({
                'format': 'png',
                'reason': 'PNG is optimal for graphics with few colors',
                'score': 8
            })
            if target_use == 'web':
                recommendations.append({
                    'format': 'webp',
                    'reason': 'WebP provides excellent compression for graphics',
                    'score': 9
                })
        
        elif characteristics.get('is_complex_photo'):
            recommendations.append({
                'format': 'jpeg',
                'reason': 'JPEG is optimal for complex photos',
                'score': 9
            })
            if target_use == 'web':
                recommendations.append({
                    'format': 'webp',
                    'reason': 'WebP provides better compression than JPEG',
                    'score': 8
                })
        
        else:
            # Default recommendations
            if target_use == 'web':
                recommendations.append({
                    'format': 'webp',
                    'reason': 'WebP provides best web performance',
                    'score': 8
                })
            recommendations.append({
                'format': 'jpeg',
                'reason': 'JPEG provides good balance of quality and size',
                'score': 7
            })
        
        # Sort by score and return best recommendation
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        if recommendations:
            best = recommendations[0]
            return {
                'recommended_format': best['format'],
                'reason': best['reason'],
                'score': best['score']
            }
        else:
            return {'recommended_format': 'jpeg', 'reason': 'Default fallback', 'score': 5}
    
    def convert_format(self, input_path: str, target_format: str,
                      output_path: str = None, quality: str = 'high',
                      optimize_for_web: bool = False) -> Dict:
        """Convert image to specified format with optimal settings."""
        try:
            if target_format not in self.FORMAT_CONFIGS:
                raise ValueError(f"Unsupported target format: {target_format}")
            
            # Set output path if not provided
            if output_path is None:
                input_file = Path(input_path)
                output_path = str(input_file.parent / f"{input_file.stem}.{target_format}")
            
            # Get original file info
            original_size = os.path.getsize(input_path)
            characteristics = self.analyze_image_characteristics(input_path)
            
            with Image.open(input_path) as img:
                original_format = img.format
                converted_img = img.copy()
                
                # Format-specific conversion
                if target_format == 'jpeg':
                    result = self._convert_to_jpeg(converted_img, output_path, quality, optimize_for_web)
                    
                elif target_format == 'png':
                    result = self._convert_to_png(converted_img, output_path, quality, optimize_for_web)
                    
                elif target_format == 'webp':
                    result = self._convert_to_webp(converted_img, output_path, quality, optimize_for_web)
                    
                elif target_format == 'tiff':
                    result = self._convert_to_tiff(converted_img, output_path, quality)
                    
                elif target_format == 'bmp':
                    result = self._convert_to_bmp(converted_img, output_path)
                
                else:
                    raise ValueError(f"Conversion to {target_format} not implemented")
            
            # Calculate results
            converted_size = os.path.getsize(output_path)
            size_change = converted_size - original_size
            size_change_percent = (size_change / original_size * 100) if original_size > 0 else 0
            
            result.update({
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'original_format': original_format,
                'target_format': target_format.upper(),
                'original_size': original_size,
                'converted_size': converted_size,
                'size_change': size_change,
                'size_change_percent': size_change_percent,
                'characteristics': characteristics
            })
            
            self.conversion_results.append(result)
            logger.info(f"Converted {input_path} to {target_format}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error converting {input_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'input_path': input_path,
                'error': str(e)
            }
    
    def _convert_to_jpeg(self, img: Image.Image, output_path: str,
                        quality: str, optimize_for_web: bool) -> Dict:
        """Convert to JPEG with optimal settings."""
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
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
        
        # Quality settings
        quality_map = self.FORMAT_CONFIGS['jpeg']['quality_ranges']
        jpeg_quality = quality_map.get(quality, quality_map['medium'])
        
        save_kwargs = {
            'format': 'JPEG',
            'quality': jpeg_quality,
            'optimize': True,
            'progressive': optimize_for_web
        }
        
        # Preserve EXIF if available
        if hasattr(img, 'info') and 'exif' in img.info:
            save_kwargs['exif'] = img.info['exif']
        
        img.save(output_path, **save_kwargs)
        
        return {
            'conversion_settings': save_kwargs,
            'notes': 'Converted to RGB, preserved EXIF data'
        }
    
    def _convert_to_png(self, img: Image.Image, output_path: str,
                       quality: str, optimize_for_web: bool) -> Dict:
        """Convert to PNG with optimal settings."""
        # PNG compression level (0-9)
        quality_map = self.FORMAT_CONFIGS['png']['quality_ranges']
        compress_level = quality_map.get(quality, quality_map['medium'])
        
        save_kwargs = {
            'format': 'PNG',
            'optimize': True,
            'compress_level': compress_level
        }
        
        notes = []
        
        # Optimize palette mode if possible
        if img.mode == 'RGBA':
            # Check if we can use palette mode
            colors = img.getcolors(maxcolors=256)
            if colors and len(colors) <= 256:
                # Convert to palette mode for smaller file size
                img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                notes.append("Converted to palette mode for smaller size")
        
        img.save(output_path, **save_kwargs)
        
        return {
            'conversion_settings': save_kwargs,
            'notes': '; '.join(notes) if notes else 'Standard PNG conversion'
        }
    
    def _convert_to_webp(self, img: Image.Image, output_path: str,
                        quality: str, optimize_for_web: bool) -> Dict:
        """Convert to WebP with optimal settings."""
        quality_map = self.FORMAT_CONFIGS['webp']['quality_ranges']
        webp_quality = quality_map.get(quality, quality_map['medium'])
        
        # Use lossless for images with transparency or simple graphics
        use_lossless = (img.mode in ('RGBA', 'LA') or 
                       'transparency' in img.info or 
                       self._is_simple_graphic(img))
        
        save_kwargs = {
            'format': 'WEBP',
            'quality': 100 if use_lossless else webp_quality,
            'method': 6,  # Maximum compression effort
            'lossless': use_lossless
        }
        
        if optimize_for_web:
            save_kwargs['method'] = 4  # Faster compression for web
        
        img.save(output_path, **save_kwargs)
        
        return {
            'conversion_settings': save_kwargs,
            'notes': f"Used {'lossless' if use_lossless else 'lossy'} compression"
        }
    
    def _convert_to_tiff(self, img: Image.Image, output_path: str, quality: str) -> Dict:
        """Convert to TIFF with optimal settings."""
        save_kwargs = {
            'format': 'TIFF',
            'compression': 'lzw'  # Lossless compression
        }
        
        img.save(output_path, **save_kwargs)
        
        return {
            'conversion_settings': save_kwargs,
            'notes': 'Used LZW lossless compression'
        }
    
    def _convert_to_bmp(self, img: Image.Image, output_path: str) -> Dict:
        """Convert to BMP."""
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        save_kwargs = {'format': 'BMP'}
        img.save(output_path, **save_kwargs)
        
        return {
            'conversion_settings': save_kwargs,
            'notes': 'Converted to RGB mode'
        }
    
    def _is_simple_graphic(self, img: Image.Image) -> bool:
        """Check if image is a simple graphic (few colors, sharp edges)."""
        try:
            # Sample a portion of the image
            sample_img = img.resize((50, 50))
            colors = sample_img.getcolors(maxcolors=256)
            
            # If we can get all colors and there are few of them
            return colors is not None and len(colors) < 64
            
        except Exception:
            return False
    
    def batch_convert(self, input_paths: List[str], target_format: str,
                     output_dir: str = None, quality: str = 'high',
                     auto_recommend: bool = False,
                     optimize_for_web: bool = False) -> Dict:
        """Convert multiple images to specified format."""
        results = []
        
        # Create output directory
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        for input_path in input_paths:
            if not os.path.exists(input_path):
                continue
            
            # Auto-recommend format if requested
            if auto_recommend:
                recommendation = self.recommend_format(input_path)
                actual_format = recommendation.get('recommended_format', target_format)
            else:
                actual_format = target_format
            
            # Determine output path
            if output_dir:
                filename = Path(input_path).stem
                output_path = os.path.join(output_dir, f"{filename}.{actual_format}")
            else:
                output_path = None
            
            # Convert image
            result = self.convert_format(
                input_path, actual_format, output_path, quality, optimize_for_web
            )
            
            if auto_recommend and actual_format != target_format:
                result['auto_recommended'] = True
                result['recommendation_reason'] = recommendation.get('reason', '')
            
            results.append(result)
        
        # Calculate batch statistics
        successful = [r for r in results if r.get('success', False)]
        total_original_size = sum(r.get('original_size', 0) for r in successful)
        total_converted_size = sum(r.get('converted_size', 0) for r in successful)
        
        return {
            'total_files': len(input_paths),
            'successful': len(successful),
            'failed': len(results) - len(successful),
            'total_original_size': total_original_size,
            'total_converted_size': total_converted_size,
            'total_size_change': total_converted_size - total_original_size,
            'results': results
        }

if __name__ == "__main__":
    # Example usage
    import sys
    
    converter = ImageFormatConverter()
    
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        target_format = sys.argv[2]
        
        # Get recommendation
        recommendation = converter.recommend_format(input_file)
        print(f"🔍 Recommended format: {recommendation['recommended_format']}")
        print(f"📝 Reason: {recommendation['reason']}")
        
        # Convert
        result = converter.convert_format(input_file, target_format)
        
        if result['success']:
            print(f"✅ Conversion successful!")
            print(f"📁 Output: {result['output_path']}")
            print(f"📊 Size change: {result['size_change_percent']:+.1f}%")
        else:
            print(f"❌ Conversion failed: {result['error']}")
    else:
        print("Format Converter - Advanced image format conversion")
        print("Usage: python format_converter.py <input_file> <target_format>")
        print("Supported formats: jpeg, png, webp, tiff, bmp")