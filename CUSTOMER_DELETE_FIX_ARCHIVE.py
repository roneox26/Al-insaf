# Customer Delete Fix - Data Archive করে রাখবে

# এই code টি app.py তে permanent_delete_customer function এ replace করুন

@app.route('/customer/permanent_delete/<int:id>', methods=['POST'])
@login_required
def permanent_delete_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('inactive_customers'))
    
    try:
        password = request.form.get('password', '').strip()
        if not password:
            flash('Password required!', 'danger')\
            return redirect(url_for('inactive_customers'))
        
        if not bcrypt.check_password_hash(current_user.password, password):
            flash('Wrong password!', 'danger')
            return redirect(url_for('inactive_customers'))
        
        customer = Customer.query.get_or_404(id)
        
        if customer.is_active:
            flash('Can only delete deactivated customers!', 'danger')
            return redirect(url_for('inactive_customers'))
        
        customer_name = customer.name
        
        # ✅ DATA ARCHIVE - Delete করার পরিবর্তে customer_id NULL করে দিন
        # এতে data হারাবে না, শুধু customer এর সাথে link থাকবে না
        
        # Update collections - customer_id NULL করুন (data রাখুন)
        LoanCollection.query.filter_by(customer_id=id).update(
            {'customer_id': None}, 
            synchronize_session=False
        )
        
        SavingCollection.query.filter_by(customer_id=id).update(
            {'customer_id': None}, 
            synchronize_session=False
        )
        
        FeeCollection.query.filter_by(customer_id=id).update(
            {'customer_id': None}, 
            synchronize_session=False
        )
        
        Withdrawal.query.filter_by(customer_id=id).update(
            {'customer_id': None}, 
            synchronize_session=False
        )
        
        CollectionSchedule.query.filter_by(customer_id=id).update(
            {'customer_id': None}, 
            synchronize_session=False
        )
        
        # Loans - customer name এ [DELETED] tag যোগ করুন
        Loan.query.filter_by(customer_name=customer.name).update(
            {'customer_name': f'[DELETED] {customer.name}'}, 
            synchronize_session=False
        )
        
        # Customer delete করুন
        db.session.delete(customer)
        db.session.commit()
        
        flash(f'Customer "{customer_name}" archived! Data preserved in database.', 'success')
        return redirect(url_for('inactive_customers'))
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Delete error: {error_details}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('inactive_customers'))
