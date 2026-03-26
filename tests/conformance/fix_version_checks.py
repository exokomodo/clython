#!/usr/bin/env python3
"""
Bulk fix manual version checks to use pytest markers.
"""
import os
import re
import sys

def fix_version_checks(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find manual version checks inside test methods
    patterns = [
        (r'\s+if sys\.version_info >= \(3, (\d+)\):\s*\n', ''),  # Remove if checks
        (r'\s+if sys\.version_info < \(3, (\d+)\):\s*\n\s+pytest\.skip\([^\)]+\)\s*\n', ''),  # Remove skips
        (r'if sys\.version_info < \(3, (\d+)\):\s*\n\s+pytest\.skip\([^\)]+\)\s*\n\s+', ''),  # Helper method skips
        # Fix indentation after removing if blocks
        (r'(\s+)# (Positional-only|F-strings|Match|Async|While)', r'\1# \2'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            modified = True
    
    # Remove hanging else blocks after if version_info
    content = re.sub(r'\s+else:\s*\n\s+source = [^\n]+\n', '', content, flags=re.MULTILINE)
    
    if modified:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
    
    return modified

def main():
    test_dir = "tests/conformance"
    for filename in os.listdir(test_dir):
        if filename.endswith('.py') and filename.startswith('test_'):
            file_path = os.path.join(test_dir, filename)
            fix_version_checks(file_path)

if __name__ == '__main__':
    main()