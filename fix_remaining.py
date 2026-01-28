# -*- coding: utf-8 -*-
import codecs

with codecs.open('app.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Fix remaining broken text
fixes = {
    "নাম সক্রিয়?!": "নাম প্রয়োজন!",
    "যোগ করা করা হয়েছে!": "যোগ করা হয়েছে!",
    "?যোগ করা?!": "খুঁজে পাওয়া যায়নি!",
    "নামনাম Collection নাম করা হয়েছে!": "নতুন Collection যোগ করা হয়েছে!",
}

for broken, fixed in fixes.items():
    content = content.replace(broken, fixed)

with codecs.open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
