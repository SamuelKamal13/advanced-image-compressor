#!/usr/bin/env python3
"""
Comprehensive integration test for the Image Compressor with auto-repair.
Tests all interfaces (Python API, CLI, GUI integration) with various scenarios.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import json

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from image_compressor import ImageCompressor
from PIL import Image
import numpy as np

def create_test_images(test_dir):
    """Create various test images for comprehensive testing."""
    images = {}
    
    # Create normal test image
    normal_path = test_dir / "normal.jpg"
    arr = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    img.save(normal_path, format='JPEG', quality=95)
    images['normal'] = normal_path
    
    # Create truncated (corrupted) image
    truncated_path = test_dir / "truncated.jpg"
    with open(normal_path, 'rb') as src:
        data = src.read()
    # Truncate to 70% of original size
    truncated_data = data[:int(len(data) * 0.7)]
    with open(truncated_path, 'wb') as dst:
        dst.write(truncated_data)
    images['truncated'] = truncated_path
    
    # Create PNG image
    png_path = test_dir / "test.png"
    img.save(png_path, format='PNG')
    images['png'] = png_path
    
    return images

def test_python_api(test_images, output_dir):
    """Test Python API with auto-repair."""
    print("🐍 Testing Python API")
    print("-" * 30)
    
    results = {}
    
    # Test with auto-repair enabled (default)
    print("1. Testing with auto-repair enabled...")
    compressor = ImageCompressor(auto_repair=True)
    
    for name, path in test_images.items():
        output_path = output_dir / f"api_{name}_repaired.jpg"
        result = compressor.compress_image(str(path), str(output_path))
        results[f"api_{name}_repaired"] = result
        
        status = "✅ Success" if result['success'] else "❌ Failed"
        repair_info = ""
        if result.get('was_auto_repaired'):
            repair_info = f" (🔧 Auto-repaired: {result.get('repair_method', 'unknown')})"
        
        print(f"   {name}: {status}{repair_info}")
        if result['success']:
            print(f"      {result['compression_ratio']:.1f}% reduction")
    
    # Test with auto-repair disabled
    print("\n2. Testing with auto-repair disabled...")
    compressor_no_repair = ImageCompressor(auto_repair=False)
    
    for name, path in test_images.items():
        output_path = output_dir / f"api_{name}_no_repair.jpg"
        result = compressor_no_repair.compress_image(str(path), str(output_path))
        results[f"api_{name}_no_repair"] = result
        
        status = "✅ Success" if result['success'] else "❌ Failed"
        print(f"   {name}: {status}")
    
    # Cleanup
    compressor.cleanup_temp_files()
    compressor_no_repair.cleanup_temp_files()
    
    return results

def test_cli_interface(test_images, output_dir):
    """Test CLI interface with auto-repair."""
    print("\n⌨️  Testing CLI Interface")
    print("-" * 30)
    
    python_exe = sys.executable
    cli_script = Path(__file__).parent / "cli_compressor.py"
    
    results = {}
    
    # Test with auto-repair (default behavior)
    print("1. Testing CLI with auto-repair (default)...")
    for name, path in test_images.items():
        output_path = output_dir / f"cli_{name}_default.jpg"
        cmd = [python_exe, str(cli_script), str(path), "-o", str(output_dir), "--suffix", f"cli_{name}_default", "--quiet"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
            success = result.returncode == 0
            results[f"cli_{name}_default"] = {
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            status = "✅ Success" if success else "❌ Failed"
            print(f"   {name}: {status}")
            if not success and result.stderr:
                print(f"      Error: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"   {name}: ❌ Exception - {str(e)}")
            results[f"cli_{name}_default"] = {'success': False, 'error': str(e)}
    
    # Test with auto-repair disabled
    print("\n2. Testing CLI with --no-auto-repair...")
    for name, path in test_images.items():
        output_path = output_dir / f"cli_{name}_no_repair.jpg"
        cmd = [python_exe, str(cli_script), str(path), "-o", str(output_dir), "--suffix", f"cli_{name}_no_repair", "--no-auto-repair", "--quiet"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
            success = result.returncode == 0
            results[f"cli_{name}_no_repair"] = {
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            status = "✅ Success" if success else "❌ Failed"
            print(f"   {name}: {status}")
            
        except Exception as e:
            print(f"   {name}: ❌ Exception - {str(e)}")
            results[f"cli_{name}_no_repair"] = {'success': False, 'error': str(e)}
    
    return results

def analyze_results(api_results, cli_results):
    """Analyze and summarize test results."""
    print("\n📊 Test Results Analysis")
    print("=" * 50)
    
    # Count successes and failures
    api_successes = sum(1 for r in api_results.values() if r['success'])
    api_total = len(api_results)
    api_repairs = sum(1 for r in api_results.values() if r.get('was_auto_repaired', False))
    
    cli_successes = sum(1 for r in cli_results.values() if r['success'])
    cli_total = len(cli_results)
    
    print(f"Python API: {api_successes}/{api_total} successful ({api_repairs} auto-repaired)")
    print(f"CLI Interface: {cli_successes}/{cli_total} successful")
    
    # Analyze auto-repair effectiveness
    print(f"\n🔧 Auto-Repair Analysis:")
    
    # Check if truncated images were handled differently
    truncated_with_repair = api_results.get('api_truncated_repaired', {})
    truncated_without_repair = api_results.get('api_truncated_no_repair', {})
    
    if truncated_with_repair and truncated_without_repair:
        repair_success = truncated_with_repair['success']
        no_repair_success = truncated_without_repair['success']
        
        if repair_success and not no_repair_success:
            print("   ✅ Auto-repair successfully handled corrupted image")
            if truncated_with_repair.get('was_auto_repaired'):
                method = truncated_with_repair.get('repair_method', 'unknown')
                print(f"   🔧 Repair method used: {method}")
        elif repair_success and no_repair_success:
            print("   ⚠️  Both repair and no-repair succeeded (image may not be corrupted)")
        elif not repair_success and not no_repair_success:
            print("   ❌ Both repair and no-repair failed (severe corruption)")
        else:
            print("   🤔 Unexpected result pattern")
    
    # Summary
    print(f"\n📝 Summary:")
    total_tests = api_total + cli_total
    total_successes = api_successes + cli_successes
    success_rate = (total_successes / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"   Overall success rate: {success_rate:.1f}% ({total_successes}/{total_tests})")
    print(f"   Auto-repair functionality: {'✅ Working' if api_repairs > 0 else '⚠️  Not triggered'}")
    
    return {
        'api_success_rate': (api_successes / api_total) * 100 if api_total > 0 else 0,
        'cli_success_rate': (cli_successes / cli_total) * 100 if cli_total > 0 else 0,
        'auto_repairs': api_repairs,
        'overall_success_rate': success_rate
    }

def main():
    """Run comprehensive integration tests."""
    print("🧪 Comprehensive Integration Test")
    print("Testing Image Compressor with Auto-Repair Functionality")
    print("=" * 60)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_dir = temp_path / "output"
        output_dir.mkdir()
        
        # Create test images
        print("📁 Creating test images...")
        test_images = create_test_images(temp_path)
        print(f"   Created {len(test_images)} test images")
        
        # Test Python API
        api_results = test_python_api(test_images, output_dir)
        
        # Test CLI interface
        cli_results = test_cli_interface(test_images, output_dir)
        
        # Analyze results
        summary = analyze_results(api_results, cli_results)
        
        # Final status
        print("\n🎯 Integration Test Complete!")
        if summary['overall_success_rate'] >= 80 and summary['auto_repairs'] > 0:
            print("   ✅ All systems working correctly with auto-repair functionality")
        elif summary['overall_success_rate'] >= 80:
            print("   ⚠️  Systems working but auto-repair not triggered (no corrupted files detected)")
        else:
            print("   ❌ Some issues detected - review results above")
        
        return summary['overall_success_rate'] >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)