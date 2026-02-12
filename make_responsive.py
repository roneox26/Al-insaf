# -*- coding: utf-8 -*-
"""
Script to add responsive meta tags to all HTML templates
"""

import os
import re

def add_responsive_meta(file_path):
    """Add responsive meta tags and CSS to HTML file"""
    import os
    
    # Validate path to prevent path traversal
    file_path = os.path.basename(file_path)
    safe_path = os.path.abspath(file_path)
    
    # Ensure file is in current directory
    if not safe_path.startswith(os.path.abspath(os.getcwd())):
        print(f"Error: Invalid file path")
        return False
    
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'viewport' in content:
            print(f"Already responsive: {file_path}")
            return False
        
        if '<head>' not in content:
            print(f"No <head> tag: {file_path}")
            return False
        
        meta_tag = '\n  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">'
        content = content.replace('<head>', '<head>' + meta_tag, 1)
        
        css_link = '\n  <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/responsive.css\') }}">'
        
        if '</head>' in content:
            content = content.replace('</head>', css_link + '\n</head>', 1)
        
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated: {file_path}")
        return True
    
    except Exception as e:
        print(f"Error in {file_path}: {e}")
        return False

def process_templates(templates_dir='templates'):
    """Process all HTML templates"""
    # Validate directory to prevent path traversal
    templates_dir = os.path.basename(templates_dir)
    
    updated = 0
    skipped = 0
    
    print("Processing templates...")
    print("=" * 50)
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            # Validate filename to prevent path traversal
            filename = os.path.basename(filename)
            file_path = os.path.join(templates_dir, filename)
            if add_responsive_meta(file_path):
                updated += 1
            else:
                skipped += 1
    
    print("=" * 50)
    print(f"Updated: {updated} files")
    print(f"Skipped: {skipped} files")
    print("\nAll templates are now mobile responsive!")

if __name__ == '__main__':
    process_templates()
