$content = Get-Content app.py -Raw -Encoding UTF8

# Fix all broken Bengali text
$content = $content -replace 'নিয়মিত খরচ \?\?\?\?\? \?\?\?\?\?\?!', 'নিয়মিত খরচ মুছে ফেলা হয়েছে!'
$content = $content -replace 'সক্রিয়\?\?\?', 'নিষ্ক্রিয়'
$content = $content -replace 'কালেকশন ৳\?\? \?\?\?\?\?\?!', 'যোগ করা হয়েছে!'
$content = $content -replace 'কালেকশন ৳\?\?\?\?\?', 'সংরক্ষণ করা'
$content = $content -replace 'কালেকশন ৳\?\?', 'যোগ করা'
$content = $content -replace '\?\?\?মোট', 'সেভিংস'
$content = $content -replace '\?মোট', 'বাকি'
$content = $content -replace '\?\?\?', 'নাম'
$content = $content -replace '\?\?', 'সব'

Set-Content app.py $content -Encoding UTF8 -NoNewline
Write-Host "সব ভাঙা বাংলা টেক্সট ঠিক করা হয়েছে!"
