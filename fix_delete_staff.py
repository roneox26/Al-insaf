# -*- coding: utf-8 -*-
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the corrupt delete_staff function
# Remove everything from @app.route('/admin/staff/delete to the next @app.route
pattern = r"@app\.route\('/admin/staff/delete/<int:id>', methods=\['POST'\]\).*?(?=@app\.route\('/admin/staff/view/<int:id>'\))"

clean_delete_staff = """@app.route('/admin/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    password = request.form.get('password', '').strip()
    if not password:
        flash('পাসওয়ার্ড আবশ্যক!', 'danger')
        return redirect(url_for('manage_staff'))
    
    if not bcrypt.check_password_hash(current_user.password, password):
        flash('পাসওয়ার্ড ভুল! Staff ডিলিট করা যায়নি।', 'danger')
        return redirect(url_for('manage_staff'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    db.session.delete(staff)
    db.session.commit()
    flash('Staff সফলভাবে ডিলিট হয়েছে!', 'success')
    return redirect(url_for('manage_staff'))

"""

# Replace the corrupt function
content = re.sub(pattern, clean_delete_staff, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] delete_staff function fixed!")
