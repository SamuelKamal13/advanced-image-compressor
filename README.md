# Advanced Image Compressor

A powerful, user-friendly tool for compressing images while maintaining quality and resolution. This tool offers multiple interfaces (GUI, CLI, and Python API) and supports batch processing with intelligent format conversion.

## 🚀 Features

### Core Capabilities

- **Quality Preservation**: Advanced algorithms maintain image quality while reducing file size
- **Multiple Formats**: Support for JPEG, PNG, WebP, TIFF, and BMP
- **Batch Processing**: Process hundreds of images at once
- **Smart Compression**: Automatic optimization based on image characteristics
- **Format Conversion**: Intelligent format recommendations with optimal settings
- **EXIF Preservation**: Optional preservation of metadata

### User Interfaces

- **🖥️ GUI Application**: User-friendly interface with real-time preview
- **⌨️ Command Line**: Powerful CLI for automation and batch processing
- **🐍 Python API**: Integrate into your own projects

### Advanced Features

- **Auto-Repair**: Automatically fix corrupted or truncated image files during compression
- **Progressive JPEG**: Better perceived loading for web images
- **PNG Optimization**: Advanced compression with transparency support
- **WebP Support**: Modern format with superior compression
- **Size Targeting**: Compress to specific file size limits
- **Quality Presets**: Maximum, High, Balanced, and Small presets
- **Parallel Processing**: Multi-core support for faster batch operations

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Setup

1. **Clone or download** this repository
2. **Navigate** to the project directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Manual Installation

```bash
pip install Pillow pillow-simd
```

## 🎯 Quick Start

### GUI Application

Launch the graphical interface:

```bash
python gui_compressor.py
```

**Features:**

- Drag & drop file selection
- Real-time image preview
- Compression settings with presets
- Batch processing with progress tracking
- Results summary and statistics

### Command Line Interface

Basic compression:

```bash
python cli_compressor.py image.jpg
```

Advanced usage:

```bash
# Compress with high quality preset
python cli_compressor.py *.jpg -q high

# Convert PNG to WebP
python cli_compressor.py image.png -f webp

# Batch compress folder recursively
python cli_compressor.py photos/ -r -o compressed/

# Compress to maximum 2MB file size
python cli_compressor.py large_image.jpg -s 2

# Dry run (preview without processing)
python cli_compressor.py *.jpg --dry-run
```

### Python API

```python
from image_compressor import ImageCompressor

# Initialize compressor
compressor = ImageCompressor()

# Compress single image
result = compressor.compress_image(
    'input.jpg',
    'output.jpg',
    quality_preset='balanced'
)

# Batch compress
results = compressor.compress_batch(
    ['image1.jpg', 'image2.png'],
    output_dir='compressed/',
    quality_preset='high'
)
```

## 🔧 Configuration Options

### Quality Presets

| Preset       | JPEG Quality | WebP Quality | PNG Optimize | Best For           |
| ------------ | ------------ | ------------ | ------------ | ------------------ |
| **Maximum**  | 95           | 85           | Yes          | Professional/Print |
| **High**     | 88           | 80           | Yes          | High-quality web   |
| **Balanced** | 82           | 75           | Yes          | General use        |
| **Small**    | 75           | 70           | Yes          | Web optimization   |

### Format Recommendations

#### JPEG

- **Best for**: Photos, natural images, complex scenes
- **Pros**: Excellent compression for photos, universal support
- **Cons**: No transparency, lossy compression
- **Settings**: Quality 75-95, progressive for web

#### PNG

- **Best for**: Graphics, logos, images with transparency
- **Pros**: Lossless, transparency support, good for graphics
- **Cons**: Larger files for photos
- **Settings**: Compression level 6-9, palette optimization

#### WebP

- **Best for**: Modern web applications
- **Pros**: Superior compression, transparency, animation support
- **Cons**: Limited support in older browsers
- **Settings**: Quality 70-90, lossless for graphics

## 📊 Usage Examples

### CLI Examples

#### Basic Operations

```bash
# Compress single image with balanced quality
python cli_compressor.py photo.jpg

# Compress multiple images
python cli_compressor.py *.jpg *.png

# Compress entire folder
python cli_compressor.py photos/ -r
```

#### Advanced Compression

```bash
# High quality with custom output directory
python cli_compressor.py images/ -r -q high -o compressed/

# Convert all images to WebP format
python cli_compressor.py *.jpg -f webp -q balanced

# Compress large images to max 5MB
python cli_compressor.py large_photos/ -r -s 5

# Remove EXIF data and compress
python cli_compressor.py *.jpg --no-exif -q small

# Disable auto-repair for corrupted files
python cli_compressor.py damaged_photos/ --no-auto-repair
```

#### Information and Analysis

```bash
# Show what would be processed (dry run)
python cli_compressor.py photos/ -r --dry-run

# Detailed statistics by format
python cli_compressor.py *.* -r --format-stats

# JSON output for integration
python cli_compressor.py images/ -r --json > results.json
```

#### Filtering Options

```bash
# Only process large files (>5MB)
python cli_compressor.py photos/ -r --min-size 5

# Only process JPEG files
python cli_compressor.py photos/ -r --formats jpg jpeg

# Process files between 1-10MB
python cli_compressor.py photos/ -r --min-size 1 --max-size 10
```

### Python API Examples

#### Basic Usage

```python
from image_compressor import ImageCompressor
from format_converter import ImageFormatConverter

# Initialize tools
compressor = ImageCompressor()
converter = ImageFormatConverter()

# Simple compression
result = compressor.compress_image('photo.jpg')
print(f"Size reduced by {result['compression_ratio']:.1f}%")

# Format conversion with recommendation
recommendation = converter.recommend_format('image.png', target_use='web')
print(f"Recommended: {recommendation['recommended_format']}")

converter.convert_format('image.png', recommendation['recommended_format'])
```

#### Advanced Processing

```python
import os
from pathlib import Path

# Batch process with custom settings
files = list(Path('photos').glob('*.jpg'))
results = compressor.compress_batch(
    [str(f) for f in files],
    output_dir='compressed',
    quality_preset='high',
    preserve_structure=True
)

# Analyze results
successful = [r for r in results['results'] if r['success']]
total_savings = sum(r['size_reduction_bytes'] for r in successful)
print(f"Total space saved: {total_savings / (1024*1024):.1f} MB")

# Smart format conversion
for image_path in files:
    analysis = converter.analyze_image_characteristics(str(image_path))
    if analysis.get('has_transparency'):
        converter.convert_format(str(image_path), 'webp', quality='high')
    elif analysis.get('is_complex_photo'):
        compressor.compress_image(str(image_path), quality_preset='balanced')
```

## 🎨 GUI Usage Guide

### Main Interface

1. **File Selection**: Click "Add Images" or "Add Folder" to select files
2. **Preview**: Click any file in the list to preview it
3. **Settings**: Choose quality preset and target format
4. **Output**: Set output directory or use default
5. **Process**: Click "Start Compression" to begin

### Settings Panel

- **Quality Preset**: Choose from Maximum, High, Balanced, or Small
- **Target Format**: Keep original or convert to JPEG/PNG/WebP
- **Preserve EXIF**: Keep or remove metadata
- **Output Directory**: Where to save compressed images

### Results Panel

- **Progress Bar**: Shows compression progress
- **Results Log**: Detailed results for each file
- **Statistics**: Overall compression statistics

## 🔧 Technical Details

### Compression Algorithms

#### JPEG Optimization

- **Progressive Encoding**: Better perceived loading
- **Optimized Huffman Tables**: Smaller file sizes
- **Quality Scaling**: Adaptive quality based on content
- **Chroma Subsampling**: Optimized for human vision

#### PNG Optimization

- **Compression Levels**: 0-9 with automatic selection
- **Palette Optimization**: Reduce colors when possible
- **Transparency Analysis**: Smart RGBA to RGB conversion
- **Filter Selection**: Optimal PNG filters

#### WebP Features

- **Lossless/Lossy**: Automatic selection based on content
- **Alpha Channel**: Full transparency support
- **Method Selection**: Compression effort optimization
- **Sharp YUV**: Better color accuracy

### Performance Optimizations

- **Streaming Processing**: Memory-efficient for large images
- **Multi-threading**: Parallel processing support
- **Smart Caching**: Avoid redundant operations
- **Progressive Loading**: Non-blocking GUI updates

## 📈 Performance Benchmarks

### Typical Compression Results

| Image Type            | Original Format | Optimized Format | Size Reduction | Quality Loss |
| --------------------- | --------------- | ---------------- | -------------- | ------------ |
| Digital Photo (5MB)   | JPEG            | JPEG (Optimized) | 15-25%         | Minimal      |
| Screenshot (2MB)      | PNG             | PNG (Optimized)  | 20-40%         | None         |
| Logo/Graphics (500KB) | PNG             | WebP             | 30-50%         | None         |
| High-res Photo (10MB) | TIFF            | JPEG (High)      | 80-90%         | Very Low     |

### Processing Speed

- **Single Image**: ~0.1-2 seconds (depending on size)
- **Batch Processing**: ~50-200 images/minute
- **Memory Usage**: <100MB for most operations
- **CPU Usage**: Scales with available cores

## � Auto-Repair Functionality

The Image Compressor includes an intelligent auto-repair system that can automatically fix corrupted or damaged image files during compression.

### How It Works

When auto-repair is enabled (default), the compressor automatically detects and attempts to fix:

- **Truncated images**: Files that were cut off during transfer or download
- **Corrupted headers**: Images with damaged metadata
- **Invalid formats**: Files with incorrect format information

### Repair Methods

1. **Truncated Loading**: Uses PIL's truncated image loading to recover partial images
2. **RGB Conversion**: Converts problematic color modes to standard RGB
3. **Metadata Stripping**: Removes corrupted EXIF and other metadata

### Usage

```python
# Python API - Enable auto-repair (default)
compressor = ImageCompressor(auto_repair=True)

# CLI - Disable auto-repair if needed
python cli_compressor.py images/ --no-auto-repair

# GUI - Use the "Auto-repair corrupted files" checkbox
```

### Output Messages

When auto-repair is successful, you'll see messages like:

```
🔧 Auto-repaired using: truncated loading
✅ Success: 45.2% reduction (repaired file)
```

## �🐛 Troubleshooting

### Common Issues

#### "No module named 'PIL'"

```bash
pip install Pillow
```

#### "Unsupported image format"

- Check if the file is actually an image
- Ensure the file extension matches the content
- Try opening the file in an image viewer first

#### "Permission denied" errors

- Check file permissions
- Ensure output directory is writable
- Run with appropriate user permissions

#### Memory errors with large images

- Process images individually instead of batch
- Use lower quality settings
- Ensure sufficient system RAM

#### GUI not responding

- Large batch operations may take time
- Check the Results panel for progress
- Use CLI for very large batches

### Performance Tips

1. **For Large Batches**: Use CLI instead of GUI
2. **For Web Images**: Use WebP format when possible
3. **For Archival**: Use PNG with maximum compression
4. **For Speed**: Use "small" quality preset
5. **For Quality**: Use "maximum" preset with format optimization

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues

- Use the GitHub issue tracker
- Include sample images (if possible)
- Describe your environment and steps to reproduce

### Feature Requests

- Check existing issues first
- Describe the use case clearly
- Consider backward compatibility

### Code Contributions

- Fork the repository
- Create a feature branch
- Write tests for new functionality
- Follow the existing code style
- Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments

- **Pillow**: The Python Imaging Library
- **Contributors**: Everyone who has contributed to this project
- **Community**: Users who provide feedback and bug reports

## 📞 Support

- **Documentation**: See this README and inline code comments
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub Discussions tab
- **Email**: For private inquiries

---

**Made with ❤️ for photographers, web developers, and anyone who works with images.**
