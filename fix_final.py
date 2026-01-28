# -*- coding: utf-8 -*-
import codecs

# Read file
with codecs.open('app.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# All replacements
fixes = {
    "নিয়মিত খরচ ????? ??????!": "নিয়মিত খরচ মুছে ফেলা হয়েছে!",
    "সক্রিয়???": "নিষ্ক্রিয়",
    "কালেকশন ৳?? ??????!": "যোগ করা হয়েছে!",
    "কালেকশন ৳?????": "সংরক্ষণ করা",
    "কালেকশন ৳??": "যোগ করা",
    "???মোট": "সেভিংস",
    "?মোট": "বাকি",
    "???": "নাম",
    "??": "সব",
}

for broken, fixed in fixes.items():
    content = content.replace(broken, fixed)

# Write back
with codecs.open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all broken Bengali text!")
