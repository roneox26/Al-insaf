# -*- coding: utf-8 -*-
import os
import re

print_templates = [
    'all_customers_print.html',
    'all_fees_print.html', 
    'all_staff_report_print.html',
    'customer_details_print.html',
    'due_report_print.html',
    'expenses_print.html',
    'investor_details_print.html',
    'loans_print.html',
    'monthly_report.html',
    'daily_report.html',
    'withdrawal_report.html',
    'customer_loan_sheet.html',
    'monthly_sheet.html'
]

header_include = '{% include "print_header.html" %}\n\n'

for template in print_templates:
    filepath = f'templates/{template}'
    if not os.path.exists(filepath):
        print(f"[SKIP] {template} not found")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if header already included
    if 'print_header.html' in content:
        print(f"[SKIP] {template} already has header")
        continue
    
    # Find <body> tag and add header after it
    if '<body' in content:
        content = re.sub(
            r'(<body[^>]*>)',
            r'\1\n  ' + header_include,
            content,
            count=1
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Added header to {template}")
    else:
        print(f"[ERROR] No <body> tag in {template}")

print("\n[SUCCESS] Print headers added!")
