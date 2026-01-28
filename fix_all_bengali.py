# -*- coding: utf-8 -*-
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all broken Bengali text with proper Bengali
replacements = [
    ("নিয়মিত খরচ ????? ??????!", "নিয়মিত খরচ মুছে ফেলা হয়েছে!"),
    ("সক্রিয়", "সক্রিয়"),
    ("সক্রিয়???", "নিষ্ক্রিয়"),
    ("কালেকশন ৳?? ??????!", "যোগ করা হয়েছে!"),
    ("কালেকশন ৳????", "সংরক্ষণ"),
    ("কালেকশন ৳???", "পাসওয়ার্ড"),
    ("কালেকশন ৳??", "যোগ"),
    ("???মোট", "সেভিংস"),
    ("?মোট", "বাকি"),
    ("???", "নাম"),
    ("??", "সব"),
    ("?", "৳"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
