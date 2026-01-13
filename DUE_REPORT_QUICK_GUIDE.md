# 🚀 Due Report - Quick Start Guide

## 📦 Installation

### Step 1: Run Setup
```bash
# Windows
SETUP_DUE_IMPROVEMENTS.bat

# Linux/Mac
python add_followup_table.py
```

### Step 2: Restart Application
```bash
python run.py
```

## 🎯 Quick Features

### 1. View Due Report
```
URL: http://localhost:5000/due_report
```

### 2. Filter by Staff
- Select staff from dropdown
- Click "Search"

### 3. Filter by Amount
- Enter Min Due: 5000
- Enter Max Due: 50000
- Click "Search"

### 4. Filter by Risk
- Select "Critical" for urgent cases
- Select "High" for priority cases

### 5. Export to Excel
- Click "Excel Export" button
- File downloads automatically
- Open in Excel/Google Sheets

### 6. Add Follow-up
```
1. Go to customer details
2. Scroll to follow-up section
3. Fill form:
   - Method: Call/Visit/SMS
   - Notes: Customer response
   - Promised: Amount promised
   - Next Date: Schedule next contact
4. Click "Add Follow-up"
```

### 7. View Follow-ups
```
URL: http://localhost:5000/followup/list
```

## 📊 Risk Levels Explained

| Risk | Days Overdue | Amount | Action |
|------|--------------|--------|--------|
| 🔴 Critical | 30+ | ৳50,000+ | Immediate action |
| 🟠 High | 15-30 | ৳30,000+ | Priority follow-up |
| 🟡 Medium | 7-15 | ৳10,000+ | Regular follow-up |
| 🟢 Low | <7 | <৳10,000 | Monitor |

## 🎨 Color Codes

- 🔴 **Red Row**: Customer is overdue
- 🟡 **Yellow Row**: Due today
- 🟢 **Green Row**: On-time

## 📱 Mobile Access

All features are mobile-responsive:
- Touch-friendly buttons
- Scrollable tables
- Collapsible filters
- Easy navigation

## 🔐 Permissions

| Role | View All | Filter | Export | Follow-up |
|------|----------|--------|--------|-----------|
| Admin | ✅ | ✅ | ✅ | ✅ |
| Office Staff | ✅ | ✅ | ✅ | ✅ |
| Field Staff | Own Only | ✅ | ✅ | ✅ |
| Monitor | ✅ | ✅ | ✅ | ❌ |

## 💡 Pro Tips

### For Maximum Efficiency
1. **Morning Routine**
   - Check pending follow-ups
   - Review critical risk customers
   - Export daily report

2. **During Field Work**
   - Update follow-ups immediately
   - Record promised amounts
   - Schedule next visits

3. **End of Day**
   - Mark completed follow-ups
   - Review tomorrow's schedule
   - Update collection status

### Best Practices
- ✅ Update follow-ups daily
- ✅ Use specific notes
- ✅ Track promised amounts
- ✅ Schedule next contacts
- ✅ Export weekly reports

## 🔍 Search Tips

### Quick Search
- Type customer name
- Type phone number
- Type member number
- Results filter instantly

### Advanced Search
- Use filters for precise results
- Combine multiple filters
- Export filtered results

## 📈 Analytics Usage

### Daily Review
1. Check risk distribution
2. Identify critical cases
3. Assign follow-ups
4. Monitor progress

### Weekly Review
1. Export full report
2. Analyze trends
3. Staff performance
4. Collection efficiency

### Monthly Review
1. Compare with previous month
2. Identify patterns
3. Adjust strategies
4. Set targets

## 🆘 Common Issues

### Filter Not Working
```
Solution: Click "Clear Filters" and try again
```

### Export Shows Gibberish
```
Solution: Open in Excel, select UTF-8 encoding
```

### Follow-up Not Saving
```
Solution: Check all required fields are filled
```

### Can't See All Customers
```
Solution: Check your role permissions
Field staff can only see assigned customers
```

## 📞 Quick Actions

| Action | Shortcut |
|--------|----------|
| Search | Type in search box |
| Sort by Name | Click "নাম" button |
| Sort by Amount | Click "টাকা" button |
| Sort by Days | Click "দিন" button |
| Daily View | Click "তারিখ অনুযায়ী" |
| Export | Click "Excel Export" |
| Print | Click "প্রিন্ট" |

## 🎓 Training Checklist

### For New Users
- [ ] Understand risk levels
- [ ] Practice filtering
- [ ] Learn to export
- [ ] Add test follow-up
- [ ] Complete a follow-up
- [ ] View follow-up list

### For Admins
- [ ] Review all features
- [ ] Set up staff access
- [ ] Configure filters
- [ ] Test export function
- [ ] Train field staff
- [ ] Monitor usage

## 📊 Sample Workflow

### Daily Collection Workflow
```
1. Morning (9:00 AM)
   → Check pending follow-ups
   → Review critical customers
   → Plan route

2. Field Work (10:00 AM - 4:00 PM)
   → Visit customers
   → Collect payments
   → Update follow-ups
   → Record promises

3. Evening (5:00 PM)
   → Mark completed follow-ups
   → Schedule next visits
   → Submit daily report
```

## 🔗 Related Pages

- Dashboard: `/dashboard`
- Due Report: `/due_report`
- Follow-ups: `/followup/list`
- Customer Details: `/customer_details/<id>`
- Export: `/due_report/export`
- Print: `/due_report_print`

## 📝 Notes

- All times are in local timezone
- Amounts in Bangladeshi Taka (৳)
- Dates in DD-MM-YYYY format
- Export in UTF-8 encoding

---

**Need Help?** Check DUE_REPORT_IMPROVEMENTS.md for detailed documentation
