#!/usr/bin/env python3
"""
Image Compressor Launcher
Easy launcher script for all compression tools.
"""

import sys
import os
import argparse

def main():
    """Main launcher for image compression tools."""
    parser = argparse.ArgumentParser(
        description="Image Compressor - Launch GUI, CLI, or use Python API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available modes:
  gui         - Launch graphical user interface
  cli         - Use command-line interface  
  convert     - Format conversion tool
  diagnose    - Diagnose problematic image files
  
Examples:
  python main.py gui                    # Launch GUI
  python main.py cli image.jpg          # Compress via CLI
  python main.py convert image.png webp # Convert format
  python main.py diagnose problem.jpg   # Diagnose corrupted file
        """
    )
    
    parser.add_argument('mode', choices=['gui', 'cli', 'convert', 'diagnose'],
                       help='Which tool to launch')
    parser.add_argument('args', nargs='*',
                       help='Arguments to pass to the selected tool')
    
    args = parser.parse_args()
    
    if args.mode == 'gui':
        # Launch GUI
        print("🚀 Launching Image Compressor GUI...")
        try:
            from gui_compressor import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"❌ Error launching GUI: {e}")
            print("Make sure you have tkinter installed (usually comes with Python)")
            sys.exit(1)
    
    elif args.mode == 'cli':
        # Launch CLI with remaining arguments
        print("⌨️  Starting CLI compression...")
        try:
            from cli_compressor import main as cli_main
            # Replace sys.argv with our arguments, but keep the script name
            original_argv = sys.argv
            sys.argv = ['cli_compressor.py'] + args.args
            result = cli_main()
            sys.argv = original_argv
            sys.exit(result)
        except ImportError as e:
            print(f"❌ Error launching CLI: {e}")
            sys.exit(1)
    
    elif args.mode == 'convert':
        # Launch format converter
        if len(args.args) < 2:
            print("❌ Format conversion requires input file and target format")
            print("Usage: python main.py convert <input_file> <target_format>")
            sys.exit(1)
        
        print("🔄 Starting format conversion...")
        try:
            from format_converter import ImageFormatConverter, format_size
            
            input_file = args.args[0]
            target_format = args.args[1]
            
            converter = ImageFormatConverter()
            
            # Get recommendation first
            recommendation = converter.recommend_format(input_file)
            print(f"💡 Recommended format: {recommendation['recommended_format']}")
            print(f"📝 Reason: {recommendation['reason']}")
            
            # Convert
            result = converter.convert_format(input_file, target_format)
            
            if result['success']:
                print(f"✅ Conversion successful!")
                print(f"📁 Input: {result['input_path']}")
                print(f"📁 Output: {result['output_path']}")
                print(f"📊 Size change: {result['size_change_percent']:+.1f}%")
                print(f"📈 Original: {format_size(result['original_size'])}")
                print(f"📦 Converted: {format_size(result['converted_size'])}")
            else:
                print(f"❌ Conversion failed: {result['error']}")
                sys.exit(1)
                
        except ImportError as e:
            print(f"❌ Error launching converter: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            sys.exit(1)
    
    elif args.mode == 'diagnose':
        # Launch diagnostic tool
        if len(args.args) < 1:
            print("❌ Diagnosis requires an image file")
            print("Usage: python main.py diagnose <image_file> [--repair]")
            sys.exit(1)
        
        print("🔍 Starting image diagnosis...")
        try:
            from diagnostic import main as diagnostic_main
            # Replace sys.argv with our arguments
            original_argv = sys.argv
            sys.argv = ['diagnostic.py'] + args.args
            diagnostic_main()
            sys.argv = original_argv
        except ImportError as e:
            print(f"❌ Error launching diagnostic: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Diagnostic error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Check if all required modules are available
    try:
        import PIL
        print("📦 Pillow found")
    except ImportError:
        print("❌ Pillow not found. Please install: pip install Pillow")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required")
        sys.exit(1)
    
    print("🎯 Advanced Image Compressor")
    print("=" * 40)
    
    main()