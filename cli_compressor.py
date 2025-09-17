#!/usr/bin/env python3
"""
Command Line Image Compressor
Advanced command-line tool for batch image compression with extensive options.
"""

import argparse
import sys
import os
from pathlib import Path
import json
from typing import List, Dict
import time
from image_compressor import ImageCompressor, format_size

class CLIImageCompressor:
    """Command-line interface for the image compressor."""
    
    def __init__(self):
        self.compressor = ImageCompressor()
        self.start_time = None
    
    def safe_print(self, message, file=None):
        """Safely print message handling Unicode encoding issues."""
        try:
            if file:
                print(self.format_message(message), file=file)
            else:
                print(self.format_message(message))
        except UnicodeEncodeError:
            # If still having issues, strip all non-ASCII characters
            ascii_message = message.encode('ascii', 'ignore').decode('ascii')
            if file:
                print(ascii_message, file=file)
            else:
                print(ascii_message)
        """Format message for console output, handling encoding issues."""
        try:
            # Try to encode with console encoding
            if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
                message.encode(sys.stdout.encoding)
            return message
        except (UnicodeEncodeError, AttributeError):
            # Fallback: replace problematic Unicode characters
            replacements = {
                '✅': '[SUCCESS]',
                '❌': '[ERROR]',
                '🔧': '[REPAIR]',
                '📊': '[INFO]',
                '📁': '[FOLDER]',
                '📦': '[PACKAGE]',
                '⚠️': '[WARNING]',
                '📏': '[SIZE]',
                '🎯': '[TARGET]',
                '💡': '[TIP]',
                '�': '[ROCKET]',
                '🧪': '[TEST]'
            }
            
            for unicode_char, replacement in replacements.items():
                message = message.replace(unicode_char, replacement)
            
            return message
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser."""
        parser = argparse.ArgumentParser(
            description="Advanced Image Compressor - Reduce file size while maintaining quality",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s image.jpg                           # Compress single image with balanced quality
  %(prog)s *.jpg -q high                       # Compress all JPEGs with high quality
  %(prog)s folder/ -r -o compressed/           # Recursively compress folder
  %(prog)s image.png -f webp -q maximum        # Convert PNG to WebP with maximum quality
  %(prog)s *.jpg -s 2                          # Compress to max 2MB file size
  %(prog)s folder/ -r --format-stats           # Show format statistics
  %(prog)s image.jpg --dry-run                 # Preview compression without saving
            """
        )
        
        # Input arguments
        parser.add_argument('inputs', nargs='+', 
                          help='Input image files or directories to compress')
        
        # Output options
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument('-o', '--output', 
                                help='Output directory (default: same as input with _compressed suffix)')
        output_group.add_argument('--suffix', default='_compressed',
                                help='Suffix for output files (default: _compressed)')
        output_group.add_argument('--no-suffix', action='store_true',
                                help='Don\'t add suffix to output files (overwrite originals)')
        
        # Compression options
        compression_group = parser.add_argument_group('Compression Options')
        compression_group.add_argument('-q', '--quality', 
                                     choices=['maximum', 'high', 'balanced', 'small'],
                                     default='balanced',
                                     help='Quality preset (default: balanced)')
        compression_group.add_argument('-f', '--format', 
                                     choices=['jpeg', 'png', 'webp'],
                                     help='Target format (default: keep original)')
        compression_group.add_argument('-s', '--size', type=float,
                                     help='Maximum file size in MB')
        compression_group.add_argument('--no-exif', action='store_true',
                                     help='Remove EXIF data from images')
        compression_group.add_argument('--no-auto-repair', action='store_true',
                                     help='Disable automatic repair of corrupted images')
        
        # Processing options
        processing_group = parser.add_argument_group('Processing Options')
        processing_group.add_argument('-r', '--recursive', action='store_true',
                                    help='Process directories recursively')
        processing_group.add_argument('--parallel', type=int, metavar='N',
                                    help='Number of parallel processes (default: CPU count)')
        processing_group.add_argument('--preserve-structure', action='store_true',
                                    help='Preserve directory structure in output')
        
        # Filter options
        filter_group = parser.add_argument_group('Filter Options')
        filter_group.add_argument('--min-size', type=float, metavar='MB',
                                help='Only process files larger than X MB')
        filter_group.add_argument('--max-size', type=float, metavar='MB',
                                help='Only process files smaller than X MB')
        filter_group.add_argument('--formats', nargs='+',
                                choices=['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp'],
                                help='Only process specific formats')
        
        # Information options
        info_group = parser.add_argument_group('Information Options')
        info_group.add_argument('--dry-run', action='store_true',
                              help='Show what would be compressed without actually doing it')
        info_group.add_argument('--stats', action='store_true',
                              help='Show detailed statistics after compression')
        info_group.add_argument('--format-stats', action='store_true',
                              help='Show statistics by format')
        info_group.add_argument('--json', action='store_true',
                              help='Output results in JSON format')
        
        # Verbosity options
        verbosity_group = parser.add_mutually_exclusive_group()
        verbosity_group.add_argument('-v', '--verbose', action='store_true',
                                   help='Verbose output')
        verbosity_group.add_argument('--quiet', action='store_true',
                                   help='Quiet output (errors only)')
        
        return parser
    
    def collect_files(self, inputs: List[str], recursive: bool = False,
                     formats: List[str] = None, min_size: float = None,
                     max_size: float = None) -> List[str]:
        """Collect image files from input paths with filtering."""
        files = []
        supported_exts = self.compressor.SUPPORTED_FORMATS
        
        # Filter by specified formats if given
        if formats:
            supported_exts = {f'.{fmt.lower()}' for fmt in formats}
            supported_exts.update({f'.{fmt.upper()}' for fmt in formats})
        
        for input_path in inputs:
            path = Path(input_path)
            
            if path.is_file():
                if path.suffix.lower() in supported_exts:
                    files.append(str(path))
            elif path.is_dir():
                if recursive:
                    pattern = "**/*"
                else:
                    pattern = "*"
                
                for ext in supported_exts:
                    files.extend(str(p) for p in path.glob(f"{pattern}{ext}") if p.is_file())
            else:
                # Handle glob patterns
                import glob
                matched_files = glob.glob(str(path))
                for file in matched_files:
                    if Path(file).suffix.lower() in supported_exts:
                        files.append(file)
        
        # Apply size filters
        if min_size or max_size:
            filtered_files = []
            for file in files:
                try:
                    size_mb = os.path.getsize(file) / (1024 * 1024)
                    if min_size and size_mb < min_size:
                        continue
                    if max_size and size_mb > max_size:
                        continue
                    filtered_files.append(file)
                except OSError:
                    continue
            files = filtered_files
        
        return sorted(set(files))
    
    def determine_output_path(self, input_path: str, output_dir: str = None,
                            suffix: str = '_compressed', target_format: str = None,
                            preserve_structure: bool = False,
                            base_input_dir: str = None) -> str:
        """Determine output path for a given input file."""
        input_file = Path(input_path)
        
        # Determine output filename
        if target_format:
            output_name = f"{input_file.stem}{suffix}.{target_format}"
        else:
            output_name = f"{input_file.stem}{suffix}{input_file.suffix}"
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
            
            # Preserve directory structure if requested
            if preserve_structure and base_input_dir:
                rel_path = input_file.parent.relative_to(Path(base_input_dir))
                output_path = output_path / rel_path
        else:
            output_path = input_file.parent
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        return str(output_path / output_name)
    
    def print_results(self, results: List[Dict], args: argparse.Namespace,
                     elapsed_time: float):
        """Print compression results based on output format."""
        if args.json:
            self.print_json_results(results, elapsed_time)
        else:
            self.print_text_results(results, args, elapsed_time)
    
    def print_json_results(self, results: List[Dict], elapsed_time: float):
        """Print results in JSON format."""
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        total_original = sum(r.get('original_size', 0) for r in successful)
        total_compressed = sum(r.get('compressed_size', 0) for r in successful)
        
        output = {
            'summary': {
                'total_files': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'elapsed_time_seconds': elapsed_time,
                'total_original_size_bytes': total_original,
                'total_compressed_size_bytes': total_compressed,
                'total_size_reduction_bytes': total_original - total_compressed,
                'average_compression_ratio': ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0
            },
            'results': results
        }
        
        print(json.dumps(output, indent=2))
    
    def print_text_results(self, results: List[Dict], args: argparse.Namespace,
                          elapsed_time: float):
        """Print results in human-readable text format."""
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        if not args.quiet:
            self.safe_print(f"\n📊 Compression Results")
            print("=" * 50)
            
            # Individual results
            if args.verbose:
                for result in results:
                    if result.get('success', False):
                        self.safe_print(f"✅ {Path(result['input_path']).name}")
                        print(f"   {format_size(result['original_size'])} → {format_size(result['compressed_size'])} "
                              f"({result['compression_ratio']:.1f}% reduction)")
                        
                        # Show auto-repair information if applicable
                        if result.get('was_auto_repaired', False):
                            repair_method = result.get('repair_method', 'unknown method')
                            self.safe_print(f"   🔧 Auto-repaired using: {repair_method}")
                            
                    else:
                        self.safe_print(f"❌ {Path(result['input_path']).name}: {result['error']}")
                        # Show suggestions if available
                        if 'suggestions' in result and result['suggestions']:
                            print(f"   💡 Suggestions:")
                            for suggestion in result['suggestions']:
                                print(f"      • {suggestion}")
                print()
        
        # Summary statistics
        if successful:
            total_original = sum(r['original_size'] for r in successful)
            total_compressed = sum(r['compressed_size'] for r in successful)
            total_reduction = total_original - total_compressed
            avg_compression = (total_reduction / total_original * 100) if total_original > 0 else 0
            
            self.safe_print(f"✅ Successfully processed: {len(successful)}/{len(results)} files")
            self.safe_print(f"📁 Total size reduction: {format_size(total_reduction)} ({avg_compression:.1f}%)")
            self.safe_print(f"📊 Original total: {format_size(total_original)}")
            self.safe_print(f"📦 Compressed total: {format_size(total_compressed)}")
        
        if failed and not args.quiet:
            self.safe_print(f"❌ Failed: {len(failed)} files")
            if args.verbose:
                for result in failed:
                    print(f"   {Path(result['input_path']).name}: {result['error']}")
                    if 'suggestions' in result and result['suggestions']:
                        print(f"      💡 Try:")
                        for suggestion in result['suggestions']:
                            print(f"         • {suggestion}")
            else:
                print(f"   Run with --verbose to see detailed error information")
        
        # Format statistics
        if args.format_stats and successful:
            self.print_format_stats(successful)
        
        print(f"⏱️  Processing time: {elapsed_time:.2f} seconds")
    
    def print_format_stats(self, results: List[Dict]):
        """Print statistics grouped by format."""
        format_stats = {}
        
        for result in results:
            fmt = result.get('original_format', 'Unknown')
            if fmt not in format_stats:
                format_stats[fmt] = {
                    'count': 0,
                    'total_original': 0,
                    'total_compressed': 0
                }
            
            stats = format_stats[fmt]
            stats['count'] += 1
            stats['total_original'] += result.get('original_size', 0)
            stats['total_compressed'] += result.get('compressed_size', 0)
        
        print(f"\n📈 Format Statistics")
        print("-" * 30)
        
        for fmt, stats in format_stats.items():
            reduction = stats['total_original'] - stats['total_compressed']
            ratio = (reduction / stats['total_original'] * 100) if stats['total_original'] > 0 else 0
            
            print(f"{fmt}: {stats['count']} files")
            print(f"  Size reduction: {format_size(reduction)} ({ratio:.1f}%)")
    
    def run(self, args: argparse.Namespace) -> int:
        """Run the compression with given arguments."""
        self.start_time = time.time()
        
        try:
            # Collect files
            files = self.collect_files(
                args.inputs,
                recursive=args.recursive,
                formats=args.formats,
                min_size=args.min_size,
                max_size=args.max_size
            )
            
            if not files:
                self.safe_print("❌ No image files found matching criteria.", file=sys.stderr)
                return 1
            
            if not args.quiet:
                print(f"📁 Found {len(files)} image files to process")
                if not getattr(args, 'no_auto_repair', False):
                    print("🔧 Auto-repair enabled for corrupted images")
            
            # Dry run mode
            if args.dry_run:
                print("\n🔍 Dry Run - Files that would be processed:")
                for file in files:
                    size = format_size(os.path.getsize(file))
                    print(f"  {Path(file).name} ({size})")
                return 0
            
            # Initialize compressor with auto-repair setting
            self.compressor = ImageCompressor(auto_repair=not getattr(args, 'no_auto_repair', False))
            
            # Determine base input directory for structure preservation
            base_input_dir = None
            if args.preserve_structure and len(args.inputs) == 1:
                input_path = Path(args.inputs[0])
                if input_path.is_dir():
                    base_input_dir = str(input_path)
            
            # Process files
            results = []
            for i, file_path in enumerate(files):
                if not args.quiet and not args.json:
                    print(f"🔄 Processing {i+1}/{len(files)}: {Path(file_path).name}")
                
                # Determine output path
                suffix = '' if args.no_suffix else args.suffix
                output_path = self.determine_output_path(
                    file_path,
                    args.output,
                    suffix,
                    args.format,
                    args.preserve_structure,
                    base_input_dir
                )
                
                # Compress image
                result = self.compressor.compress_image(
                    input_path=file_path,
                    output_path=output_path,
                    quality_preset=args.quality,
                    target_format=args.format,
                    preserve_exif=not args.no_exif,
                    max_size_mb=args.size
                )
                
                results.append(result)
            
            # Print results
            elapsed_time = time.time() - self.start_time
            self.print_results(results, args, elapsed_time)
            
            # Show auto-repair summary if any files were repaired
            repaired_count = len([r for r in results if r.get('was_auto_repaired', False)])
            if repaired_count > 0 and not args.quiet:
                print(f"\n🔧 Auto-repair summary: {repaired_count} file(s) were automatically repaired")
            
            # Return appropriate exit code
            failed_count = len([r for r in results if not r.get('success', False)])
            return 1 if failed_count > 0 else 0
            
        except KeyboardInterrupt:
            print("\n🛑 Compression interrupted by user.", file=sys.stderr)
            return 130
        except Exception as e:
            self.safe_print(f"❌ Error: {e}", file=sys.stderr)
            return 1

def main():
    """Main entry point for the CLI application."""
    try:
        cli = CLIImageCompressor()
        parser = cli.create_parser()
        args = parser.parse_args()
        
        # Handle conflicting arguments
        if hasattr(args, 'quiet') and hasattr(args, 'verbose'):
            # This is handled by mutually_exclusive_group, but just in case
            if args.quiet and args.verbose:
                args.verbose = False
        
        return cli.run(args)
    except UnicodeEncodeError as e:
        # Handle Unicode encoding issues gracefully
        try:
            print("[ERROR] Unicode encoding issue in output. Results may still be valid.", file=sys.stderr)
            return 0  # Still consider it successful if files were processed
        except:
            return 1
    except Exception as e:
        try:
            print(f"[ERROR] {str(e)}", file=sys.stderr)
        except:
            print("[ERROR] An error occurred", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())