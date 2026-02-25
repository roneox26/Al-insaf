# -*- coding: utf-8 -*-
import re

with open(r'e:\ngo\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Bengali flash messages with English
replacements = [
    (r"flash\('Monitor staff.*?cannot collect.*?', 'danger'\)", "flash('Monitor staff cannot collect money!', 'danger')"),
    (r"flash\('.*?select a customer.*?', 'danger'\)", "flash('Please select a customer!', 'danger')"),
    (r"flash\('.*?loan or saving.*?', 'danger'\)", "flash('Please enter loan or saving amount!', 'danger')"),
    (r"flash\(f'.*?exceeds remaining.*?\{customer\.remaining_loan\}.*?', 'danger'\)", "flash(f'Amount exceeds remaining loan (৳{customer.remaining_loan})!', 'danger')"),
    (r"flash\('.*?fill all.*?', 'danger'\)", "flash('Please fill all required fields!', 'danger')"),
    (r"flash\('.*?greater than 0.*?', 'danger'\)", "flash('Amount must be greater than 0!', 'danger')"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Specific replacements for collect_loan function
content = content.replace(
    "flash('Monitor staff ??????? ???? ????? ??!', 'danger')",
    "flash('Monitor staff cannot collect money!', 'danger')"
)
content = content.replace(
    "flash('???????? ????? ?????? ??????!', 'danger')",
    "flash('Please select a customer!', 'danger')"
)
content = content.replace(
    "flash('??? ??? ?? ???????? ?????? ??????!', 'danger')",
    "flash('Please enter loan or saving amount!', 'danger')"
)
content = content.replace(
    "flash('?? ???? ???????? ???!', 'danger')",
    "flash('Please fill all required fields!', 'danger')"
)
content = content.replace(
    "flash('????? ?????? ? ?? ???? ??? ???!', 'danger')",
    "flash('Amount must be greater than 0!', 'danger')"
)
content = content.replace(
    "flash(f'?? ???? ???????? ?? (?{customer.remaining_loan}) ?????? ??????, ???? ?????? ???? ??!', 'danger')",
    "flash(f'Amount exceeds remaining loan (৳{customer.remaining_loan})!', 'danger')"
)
content = content.replace(
    "flash(f'???? ???? ??? (?{customer.remaining_loan}) ?????? ??????, ???? ?????? ???? ??!', 'danger')",
    "flash(f'Amount exceeds remaining loan (৳{customer.remaining_loan})!', 'danger')"
)

with open(r'e:\ngo\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Flash messages converted to English!")
