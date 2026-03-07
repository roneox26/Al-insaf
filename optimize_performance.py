#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Performance Optimization Script"""

import re

def optimize_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add eager loading to prevent N+1 queries
    optimizations = [
        # Dashboard queries
        (r'Customer\.query\.filter_by\(is_active=True\)\.all\(\)',
         'Customer.query.options(db.joinedload(Customer.staff)).filter_by(is_active=True).all()'),
        
        # Collection queries
        (r'LoanCollection\.query\.order_by',
         'LoanCollection.query.options(db.joinedload(LoanCollection.customer), db.joinedload(LoanCollection.staff)).order_by'),
        
        (r'SavingCollection\.query\.order_by',
         'SavingCollection.query.options(db.joinedload(SavingCollection.customer), db.joinedload(SavingCollection.staff)).order_by'),
    ]
    
    for pattern, replacement in optimizations:
        content = re.sub(pattern, replacement, content)
    
    # Add pagination import
    if 'from flask import' in content and 'paginate' not in content:
        content = content.replace(
            'from flask import Flask, render_template, redirect, url_for, flash, request, make_response',
            'from flask import Flask, render_template, redirect, url_for, flash, request, make_response, abort'
        )
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Optimizations applied!")

if __name__ == '__main__':
    optimize_app()
