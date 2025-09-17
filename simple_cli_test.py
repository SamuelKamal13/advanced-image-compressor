#!/usr/bin/env python3
"""
Simple CLI test for auto-repair functionality.
"""

import tempfile
import subprocess
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def create_test_files(temp_dir):
    """Create test files."""
    # Normal image
    normal_path = temp_dir / "normal.jpg"
    arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    img = Image.fromarray(arr)
    img.save(normal_path, format='JPEG', quality=90)
    
    # Corrupted image
    corrupted_path = temp_dir / "corrupted.jpg"
    with open(normal_path, 'rb') as src:
        data = src.read()
    # Truncate
    truncated_data = data[:int(len(data) * 0.7)]
    with open(corrupted_path, 'wb') as dst:
        dst.write(truncated_data)
    
    return normal_path, corrupted_path

def test_cli_simple():
    """Simple CLI test."""
    print("Testing CLI with auto-repair...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_dir = temp_path / "output"
        output_dir.mkdir()
        
        normal_path, corrupted_path = create_test_files(temp_path)
        
        python_exe = sys.executable
        cli_script = Path(__file__).parent / "cli_compressor.py"
        
        # Test normal file
        print("1. Testing normal file...")
        cmd = [python_exe, str(cli_script), str(normal_path), "-o", str(output_dir), "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"   Normal file: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        if result.returncode != 0:
            print(f"   Error: {result.stderr}")
        
        # Test corrupted file with auto-repair (default)
        print("2. Testing corrupted file with auto-repair...")
        cmd = [python_exe, str(cli_script), str(corrupted_path), "-o", str(output_dir), "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"   Corrupted with repair: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        if result.returncode != 0:
            print(f"   Error: {result.stderr}")
        
        # Test corrupted file without auto-repair
        print("3. Testing corrupted file without auto-repair...")
        cmd = [python_exe, str(cli_script), str(corrupted_path), "-o", str(output_dir), "--no-auto-repair", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"   Corrupted without repair: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        
        # Check output files
        output_files = list(output_dir.glob("*.jpg"))
        print(f"4. Output files created: {len(output_files)}")
        for f in output_files:
            print(f"   {f.name}")

if __name__ == "__main__":
    test_cli_simple()