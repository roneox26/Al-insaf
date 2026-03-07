#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix for monthly_report database query error
This script will patch the app.py file to fix the scalar() error
"""

import re

def fix_app_py():
    print("Reading app.py...")
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace problematic scalar() calls with coalesce
    # Pattern 1: ).scalar() or 0
    pattern1 = r'(\w+\s*=\s*db\.session\.query\(db\.func\.sum\([^)]+\)\)\.filter\([^)]+\))\s*\.scalar\(\)\s*or\s*0'
    replacement1 = r'\1.scalar() or 0'
    
    # Add coalesce to prevent NULL issues
    pattern2 = r'db\.session\.query\(db\.func\.sum\(([^)]+)\)\)'
    replacement2 = r'db.session.query(db.func.coalesce(db.func.sum(\1), 0))'
    
    print("Applying fixes...")
    content = re.sub(pattern2, replacement2, content)
    
    # Remove duplicate monthly_report functions
    # Find all @app.route('/monthly_report') occurrences
    monthly_report_count = content.count("@app.route('/monthly_report')")
    print(f"Found {monthly_report_count} monthly_report functions")
    
    if monthly_report_count > 1:
        print("Removing duplicate monthly_report functions...")
        # Keep only the first one
        parts = content.split("@app.route('/monthly_report')")
        if len(parts) > 2:
            # Find the end of the second function
            second_func = parts[2]
            # Find the next @app.route
            next_route_pos = second_func.find("\n@app.route(")
            if next_route_pos > 0:
                # Remove the duplicate function
                content = parts[0] + "@app.route('/monthly_report')" + parts[1] + second_func[next_route_pos:]
                print("Removed duplicate monthly_report function")
    
    # Remove excessive print statements in monthly_report
    lines = content.split('\n')
    new_lines = []
    in_monthly_report = False
    skip_print_block = False
    
    for i, line in enumerate(lines):
        if "@app.route('/monthly_report')" in line:
            in_monthly_report = True
        elif in_monthly_report and line.strip().startswith('@app.route('):
            in_monthly_report = False
        
        # Skip debug print statements in monthly_report
        if in_monthly_report:
            if 'print(f"\\n=== Monthly Due Calculation' in line:
                skip_print_block = True
            elif skip_print_block and ('print(f"\\nTotal Monthly Due:' in line or 'print("=" * 50)' in line):
                skip_print_block = False
                continue
            elif skip_print_block:
                continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    print("Writing fixed app.py...")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fix applied successfully!")
    print("\nChanges made:")
    print("1. Added db.func.coalesce() to all sum() queries to handle NULL values")
    print("2. Removed duplicate monthly_report functions")
    print("3. Removed excessive debug print statements")
    print("\nPlease restart your application on Render.com")

if __name__ == '__main__':
    try:
        fix_app_py()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
