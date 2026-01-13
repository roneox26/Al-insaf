# -*- coding: utf-8 -*-
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all Bangla flash messages with English
replacements = {
    "ইমেইল এবং পাসওয়ার্ড আবশ্যক!": "Email and password required!",
    "সব তথ্য পূরণ করুন!": "Please fill all fields!",
    "নাম এবং ইমেইল আবশ্যক!": "Name and email required!",
    "পাসওয়ার্ড আবশ্যক!": "Password required!",
    "পাসওয়ার্ড ভুল! Staff ডিলিট করা যায়নি।": "Wrong password! Cannot delete staff.",
    "Staff সফলভাবে ডিলিট হয়েছে!": "Staff deleted successfully!",
    "শুধুমাত্র Admin লোন দিতে পারবে!": "Only Admin can give loans!",
    "সব তথ্য সঠিকভাবে পূরণ করুন!": "Please fill all information correctly!",
    "পর্যাপ্ত টাকা নেই! বর্তমান ব্যালেন্স:": "Insufficient balance! Current balance:",
    "ঋণ যোগ সফল! পরিমাণ:": "Loan added successfully! Amount:",
    "সুদ:": "Interest:",
    "সার্ভিস চার্জ:": "Service charge:",
    "কল্যাণ ফি:": "Welfare fee:",
    "আবেদন ফি:": "Application fee:",
    "মোট:": "Total:",
    "নাম এবং ফোন নম্বর আবশ্যক!": "Name and phone required!",
    "সদস্য নং": "Member no",
    "ইতিমধ্যে ব্যবহৃত হয়েছে!": "already exists!",
    "সদস্য সফলভাবে যোগ হয়েছে! ভর্তি ফি:": "Member added successfully! Admission fee:",
    "কাস্টমার আপডেট সফল হয়েছে!": "Customer updated successfully!",
    "পাসওয়ার্ড ভুল! Customer ডিলিট করা যায়নি।": "Wrong password! Cannot delete customer.",
    "Customer সফলভাবে Deactivate হয়েছে!": "Customer deactivated successfully!",
    "Customer সফলভাবে Activate হয়েছে!": "Customer activated successfully!",
    "গ্রাহক নির্বাচন করুন!": "Please select customer!",
    "অন্তত একটি কালেকশন পরিমাণ দিন!": "Please enter at least one collection amount!",
    "লোন টাকা বাকি লোন": "Loan amount exceeds remaining loan",
    "থেকে বেশি হতে পারবে না!": "!",
    "সফলভাবে কালেকশন সম্পন্ন হয়েছে!": "Collection completed successfully!",
    "লোন:": "Loan:",
    "সেভিংস:": "Savings:",
    "Monitor staff কালেকশন করতে পারবে না!": "Monitor staff cannot collect!",
    "টাকার পরিমাণ ০ এর বেশি হতে হবে!": "Amount must be greater than 0!",
    "টাকা বাকি লোন": "Amount exceeds remaining loan",
    "সফলভাবে": "Successfully",
    "কালেকশন সম্পন্ন হয়েছে! বাকি:": "collection completed! Remaining:",
    "সেভিংস জমা হয়েছে!": "savings deposited!",
    "Investor নাম আবশ্যক!": "Investor name required!",
    "যোগ করা হয়েছে! Balance:": "added! Balance:",
    "বিয়োগ করা হয়েছে!": "deducted!",
    "পর্যাপ্ত টাকা নেই!": "Insufficient balance!",
    "Investor খুঁজে পাওয়া যায়নি!": "Investor not found!",
    "Investor এর balance": "Investor balance",
    "যথেষ্ট নয়!": "is insufficient!",
    "Withdrawal সফল হয়েছে! Balance:": "Withdrawal successful! Balance:",
    "বিয়োগ করা হয়েছে!": "deducted!",
    "ব্যয় সফল হয়েছে!": "Expense added successfully!",
    "পর্যাপ্ত সেভিংস নেই! বর্তমান:": "Insufficient savings! Current:",
    "পর্যাপ্ত ক্যাশ নেই!": "Insufficient cash!",
    "উত্তোলন সফল হয়েছে!": "Withdrawal successful!",
    "শিরোনাম এবং বিষয়বস্তু আবশ্যক!": "Title and content required!",
    "নোট সফলভাবে যোগ হয়েছে!": "Note added successfully!",
    "নোট আপডেট সফল!": "Note updated successfully!",
    "নোট ডিলিট সফল!": "Note deleted successfully!",
    "সব তথ্য পূরণ করুন!": "Please fill all fields!",
    "পাসওয়ার্ড ভুল!": "Wrong password!",
    "এই ইমেইল ইতিমধ্যে ব্যবহৃত হচ্ছে!": "Email already in use!",
    "ইমেইল সফলভাবে পরিবর্তন হয়েছে!": "Email changed successfully!",
    "বর্তমান পাসওয়ার্ড ভুল!": "Current password is wrong!",
    "নতুন পাসওয়ার্ড মিলছে না!": "New passwords do not match!",
    "পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!": "Password must be at least 6 characters!",
    "পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে!": "Password changed successfully!",
    "শিডিউল ব্যয় যোগ হয়েছে!": "Scheduled expense added!",
    "সক্রিয়": "active",
    "নিষ্ক্রিয়": "inactive",
    "শিডিউল ব্যয়": "Scheduled expense",
    "করা হয়েছে!": "updated!",
    "ডিলিট হয়েছে!": "deleted!",
}

for bangla, english in replacements.items():
    content = content.replace(bangla, english)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All Bangla messages replaced with English!")
