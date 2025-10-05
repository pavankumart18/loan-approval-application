from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import math
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loan_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import database and models
from database import db
from models import User, Bank, LoanProduct, Application, Manager

# Initialize the database with the app
db.init_app(app)

# Import services
from services.loan_calculator import LoanCalculator
from services.decision_engine import DecisionEngine
from services.gemini_service import GeminiService

# Hardcoded banks data
BANKS_DATA = [
    {
        'id': 1,
        'name': 'Stark Bank',
        'interest_rate': 7.5,
        'best_loan_type': 'Home Loan',
        'best_tenure': '20 years',
        'logo': 'stark_bank.png',
        'description': 'Leading digital bank with competitive rates'
    },
    {
        'id': 2,
        'name': 'Iron Financial',
        'interest_rate': 8.2,
        'best_loan_type': 'Personal Loan',
        'best_tenure': '5 years',
        'logo': 'iron_financial.png',
        'description': 'Fast approval for personal loans'
    },
    {
        'id': 3,
        'name': 'Captain Credit',
        'interest_rate': 6.8,
        'best_loan_type': 'Home Loan',
        'best_tenure': '25 years',
        'logo': 'captain_credit.png',
        'description': 'Lowest rates for home loans'
    },
    {
        'id': 4,
        'name': 'Thor Trust',
        'interest_rate': 9.1,
        'best_loan_type': 'Business Loan',
        'best_tenure': '10 years',
        'logo': 'thor_trust.png',
        'description': 'Supporting business growth'
    },
    {
        'id': 5,
        'name': 'Hulk Holdings',
        'interest_rate': 7.8,
        'best_loan_type': 'Auto Loan',
        'best_tenure': '7 years',
        'logo': 'hulk_holdings.png',
        'description': 'Drive your dreams with us'
    }
]

# Loan types and their requirements
LOAN_TYPES = {
    'personal': {
        'name': 'Personal Loan',
        'min_amount': 10000,
        'max_amount': 5000000,
        'min_tenure': 1,
        'max_tenure': 7,
        'interest_range': (8.0, 15.0)
    },
    'home': {
        'name': 'Home Loan',
        'min_amount': 100000,
        'max_amount': 10000000,
        'min_tenure': 5,
        'max_tenure': 30,
        'interest_range': (6.5, 9.5)
    },
    'auto': {
        'name': 'Auto Loan',
        'min_amount': 50000,
        'max_amount': 2000000,
        'min_tenure': 1,
        'max_tenure': 7,
        'interest_range': (7.0, 12.0)
    },
    'business': {
        'name': 'Business Loan',
        'min_amount': 100000,
        'max_amount': 20000000,
        'min_tenure': 1,
        'max_tenure': 15,
        'interest_range': (9.0, 16.0)
    },
    'education': {
        'name': 'Education Loan',
        'min_amount': 50000,
        'max_amount': 4000000,
        'min_tenure': 1,
        'max_tenure': 15,
        'interest_range': (8.5, 13.0)
    },
    'medical': {
        'name': 'Medical Loan',
        'min_amount': 10000,
        'max_amount': 2000000,
        'min_tenure': 1,
        'max_tenure': 5,
        'interest_range': (10.0, 18.0)
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('role_selection'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'manager':
            return redirect(url_for('role_selection'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def role_selection():
    """Initial screen asking if user is a customer or manager"""
    return render_template('role_selection.html')

@app.route('/user_dashboard')
def user_dashboard():
    """Dashboard showing all banks with their best offers"""
    return render_template('user_dashboard.html', banks=BANKS_DATA)

@app.route('/bank_selection/<int:bank_id>')
def bank_selection(bank_id):
    """Bank selection page with login/create account options"""
    bank = next((b for b in BANKS_DATA if b['id'] == bank_id), None)
    if not bank:
        flash('Bank not found', 'error')
        return redirect(url_for('user_dashboard'))
    
    return render_template('bank_selection.html', bank=bank)

@app.route('/user_login/<int:bank_id>', methods=['GET', 'POST'])
def user_login(bank_id):
    """User login page"""
    bank = next((b for b in BANKS_DATA if b['id'] == bank_id), None)
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, bank_id=bank_id).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_type'] = 'customer'
            session['bank_id'] = bank_id
            flash('Login successful!', 'success')
            return redirect(url_for('main_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('user_login.html', bank=bank)

@app.route('/user_register/<int:bank_id>', methods=['GET', 'POST'])
def user_register(bank_id):
    """User registration page"""
    bank = next((b for b in BANKS_DATA if b['id'] == bank_id), None)
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        address = request.form['address']
        monthly_income = float(request.form['monthly_income'])
        employment_type = request.form['employment_type']
        employer_name = request.form.get('employer_name', '')
        employment_tenure = float(request.form['employment_tenure'])
        credit_score = int(request.form['credit_score'])
        password = request.form['password']
        
        # Check if user already exists (globally unique email)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists with this email. Please use a different email or try logging in.', 'error')
            return render_template('user_register.html', bank=bank)
        
        # Create new user
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            dob=dob,
            address=address,
            monthly_income=monthly_income,
            employment_type=employment_type,
            employer_name=employer_name,
            employment_tenure_years=employment_tenure,
            credit_score=credit_score,
            bank_id=bank_id,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            session['user_type'] = 'customer'
            session['bank_id'] = bank_id
            
            flash('Registration successful!', 'success')
            return redirect(url_for('main_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again with different details.', 'error')
            return render_template('user_register.html', bank=bank)
    
    return render_template('user_register.html', bank=bank)

@app.route('/main_dashboard')
@login_required
def main_dashboard():
    """Main dashboard for logged-in users"""
    user = User.query.get(session['user_id'])
    bank = next((b for b in BANKS_DATA if b['id'] == session['bank_id']), None)
    
    # Get user's applications
    applications = Application.query.filter_by(user_id=user.id).order_by(Application.created_at.desc()).limit(5).all()
    
    return render_template('main_dashboard.html', user=user, bank=bank, applications=applications)

@app.route('/loan_application', methods=['GET', 'POST'])
@login_required
def loan_application():
    """Loan application questionnaire flow"""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        step = request.form.get('step')
        
        if step == '1':  # Loan type selection
            loan_type = request.form['loan_type']
            session['application_data'] = {'loan_type': loan_type}
            session.modified = True  # Ensure session is saved
            return redirect(url_for('loan_application'))
        
        elif step == '2':  # Loan amount
            amount = float(request.form['amount'])
            if 'application_data' not in session:
                flash('Session expired. Please start the application again.', 'error')
                return redirect(url_for('loan_application'))
            
            session['application_data']['amount'] = amount
            session.modified = True  # Ensure session is saved
            
            # Redirect to step 3 (tenure selection)
            return redirect(url_for('loan_application'))
        
        elif step == '3':  # Tenure selection
            try:
                tenure = int(request.form['tenure'])
            except (KeyError, ValueError):
                flash('Invalid tenure selected. Please try again.', 'error')
                return redirect(url_for('loan_application'))

            # ensure application_data exists
            if 'application_data' not in session:
                session['application_data'] = {}

            session['application_data']['tenure'] = tenure
            session.modified = True   # <-- IMPORTANT: ensure Flask saves nested change

            # Calculate EMI and show final details
            calculator = LoanCalculator()
            loan_type = session['application_data'].get('loan_type')
            amount = session['application_data'].get('amount')
            
            if loan_type is None or amount is None:
                flash('Application data incomplete. Please re-enter details.', 'error')
                return redirect(url_for('loan_application'))

            # Get bank's interest rate for this loan type
            bank = next((b for b in BANKS_DATA if b['id'] == session['bank_id']), None)
            interest_rate = bank['interest_rate']  # Simplified - in real app, get from loan products

            emi = calculator.calculate_emi(amount, interest_rate, tenure)
            total_interest = calculator.calculate_total_interest(amount, interest_rate, tenure)

            return render_template('loan_application_step3.html',
                                 loan_type=loan_type,
                                 amount=amount,
                                 tenure=tenure,
                                 interest_rate=interest_rate,
                                 emi=emi,
                                 total_interest=total_interest)
        
        elif step == '4':  # Submit application (safe, validated)
            # Defensive checks: ensure application data exists and has required fields
            app_data = session.get('application_data')
            if not app_data:
                flash('Session expired or application data missing. Please start the application again.', 'error')
                return redirect(url_for('loan_application'))

            # Required keys
            loan_type = app_data.get('loan_type')
            amount = app_data.get('amount')
            tenure = app_data.get('tenure')

            # If any required field missing, redirect to appropriate step with message
            if not loan_type:
                flash('Loan type missing. Please select the loan type first.', 'error')
                return redirect(url_for('loan_application'))  # goes to step 1
            if amount is None:
                flash('Loan amount missing. Please enter the amount.', 'error')
                return redirect(url_for('loan_application'))  # goes to step 2
            if tenure is None:
                flash('Loan tenure missing. Please choose tenure.', 'error')
                return redirect(url_for('loan_application'))  # goes to step 3

            # Validate types / convert if needed
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                flash('Invalid loan amount provided. Please enter a valid number.', 'error')
                return redirect(url_for('loan_application'))

            try:
                tenure_years = int(tenure)
            except (ValueError, TypeError):
                flash('Invalid tenure provided. Please select a valid number of years.', 'error')
                return redirect(url_for('loan_application'))

            # Optional: validate against LOAN_TYPES constraints
            loan_spec = LOAN_TYPES.get(loan_type)
            if loan_spec:
                if amount < loan_spec['min_amount'] or amount > loan_spec['max_amount']:
                    flash(f'Amount must be between {loan_spec["min_amount"]} and {loan_spec["max_amount"]}.', 'error')
                    return redirect(url_for('loan_application'))
                if tenure_years < loan_spec['min_tenure'] or tenure_years > loan_spec['max_tenure']:
                    flash(f'Tenure must be between {loan_spec["min_tenure"]} and {loan_spec["max_tenure"]} years.', 'error')
                    return redirect(url_for('loan_application'))

            # Create application record
            application = Application(
                user_id=user.id,
                bank_id=session.get('bank_id'),
                loan_type=loan_type,
                amount_requested=amount,
                tenure_years=tenure_years,
                status='pending',
                created_at=datetime.now()
            )

            try:
                db.session.add(application)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.exception("Failed to save application")
                flash('Failed to submit application. Please try again later.', 'error')
                return redirect(url_for('loan_application'))

            # Run decision engine (safe handling)
            try:
                decision_engine = DecisionEngine()
                decision = decision_engine.evaluate_application(application, user)
                application.decision = decision.get('status')
                application.decision_reason = decision.get('reason')
                application.approval_probability = decision.get('probability')
                application.suggestions = json.dumps(decision.get('suggestions', []))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.exception("Decision engine error")
                # Keep application, but mark decision fields empty / notify admin in real app
                flash('Application submitted but decision processing failed. Manager will review manually.', 'warning')

            flash('Application submitted successfully!', 'success')
            session.pop('application_data', None)
            return redirect(url_for('main_dashboard'))

    
    # GET request - determine which step to show
    if 'application_data' not in session:
        # Step 1: Loan type selection
        return render_template('loan_application_step1.html', loan_types=LOAN_TYPES)
    
    elif 'amount' not in session['application_data']:
        # Step 2: Loan amount with suggestions
        loan_type = session['application_data']['loan_type']
        try:
            suggestions = get_loan_suggestions(loan_type, 500000)  # Default amount for suggestions
        except:
            suggestions = None
        return render_template('loan_application_step2.html',
                             loan_type=loan_type,
                             suggestions=suggestions)
    
    elif 'tenure' not in session['application_data']:
        # Step 3: Tenure selection
        return render_template('loan_application_step3.html',
                             loan_type=session['application_data']['loan_type'],
                             amount=session['application_data']['amount'])
    
    else:
        # All steps completed, redirect to dashboard
        return redirect(url_for('main_dashboard'))

@app.route('/debug_session')
@login_required
def debug_session():
    """Debug route to check session data"""
    return {
        'user_id': session.get('user_id'),
        'user_type': session.get('user_type'),
        'bank_id': session.get('bank_id'),
        'application_data': session.get('application_data', {}),
        'session_keys': list(session.keys())
    }

@app.route('/gemini_suggestions')
@login_required
def gemini_suggestions():
    """Get AI suggestions for loan recommendations"""
    user = User.query.get(session['user_id'])
    gemini_service = GeminiService()
    
    suggestions = gemini_service.get_loan_suggestions(user)
    return jsonify(suggestions)

@app.route('/manager_login', methods=['GET', 'POST'])
def manager_login():
    """Manager login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        manager = Manager.query.filter_by(email=email).first()
        
        if manager and check_password_hash(manager.password_hash, password):
            session['manager_id'] = manager.id
            session['user_type'] = 'manager'
            session['bank_id'] = manager.bank_id
            flash('Manager login successful!', 'success')
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('manager_login.html')

@app.route('/manager_dashboard')
@manager_required
def manager_dashboard():
    """Manager dashboard for loan approvals"""
    manager = Manager.query.get(session['manager_id'])
    bank = next((b for b in BANKS_DATA if b['id'] == session['bank_id']), None)
    
    # Get pending applications
    pending_applications = Application.query.filter_by(
        bank_id=session['bank_id'],
        status='pending'
    ).order_by(Application.created_at.desc()).all()
    
    # Get all applications for this bank
    all_applications = Application.query.filter_by(
        bank_id=session['bank_id']
    ).order_by(Application.created_at.desc()).limit(20).all()
    
    return render_template('manager_dashboard.html',
                         manager=manager,
                         bank=bank,
                         pending_applications=pending_applications,
                         all_applications=all_applications)

@app.route('/get_application_details/<int:app_id>')
@manager_required
def get_application_details(app_id):
    """Get application details for manager review"""
    application = Application.query.get_or_404(app_id)
    
    if application.bank_id != session['bank_id']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    user = User.query.get(application.user_id)
    
    return jsonify({
        'status': 'success',
        'application': {
            'id': application.id,
            'loan_type': application.loan_type,
            'amount_requested': application.amount_requested,
            'tenure_years': application.tenure_years,
            'interest_rate': application.interest_rate,
            'emi': application.emi,
            'approval_probability': application.approval_probability,
            'decision_reason': application.decision_reason,
            'status': application.status
        },
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'monthly_income': user.monthly_income,
            'credit_score': user.credit_score
        }
    })

@app.route('/approve_application/<int:app_id>', methods=['POST'])
@manager_required
def approve_application(app_id):
    """Manager approves an application"""
    application = Application.query.get_or_404(app_id)
    
    if application.bank_id != session['bank_id']:
        flash('Unauthorized', 'error')
        return redirect(url_for('manager_dashboard'))
    
    action = request.form.get('action')
    manager_notes = request.form.get('manager_notes', '')
    
    if action == 'approve':
        application.status = 'approved'
        application.manager_notes = manager_notes
        application.manager_id = session['manager_id']
        application.processed_at = datetime.now()
        
        flash('Application approved!', 'success')
    elif action == 'reject':
        application.status = 'rejected'
        application.manager_notes = manager_notes
        application.manager_id = session['manager_id']
        application.processed_at = datetime.now()
        
        flash('Application rejected', 'info')
    elif action == 'request_docs':
        application.status = 'document_required'
        application.manager_notes = f"Document required: {manager_notes}"
        application.manager_id = session['manager_id']
        
        flash('Document request sent to customer', 'info')
    
    db.session.commit()
    return redirect(url_for('manager_dashboard'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update user profile"""
    user = User.query.get(session['user_id'])
    bank = next((b for b in BANKS_DATA if b['id'] == session['bank_id']), None)
    
    if request.method == 'POST':
        # Update user information
        user.full_name = request.form['full_name']
        user.phone = request.form['phone']
        user.address = request.form['address']
        user.monthly_income = float(request.form['monthly_income'])
        user.employment_type = request.form['employment_type']
        user.employer_name = request.form.get('employer_name', '')
        user.employment_tenure_years = float(request.form['employment_tenure'])
        user.credit_score = int(request.form['credit_score'])
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main_dashboard'))
    
    return render_template('update_profile.html', user=user, bank=bank)

@app.route('/loan_products')
@login_required
def loan_products():
    """View available loan products"""
    bank = next((b for b in BANKS_DATA if b['id'] == session['bank_id']), None)
    user = User.query.get(session['user_id'])
    
    return render_template('loan_products.html', bank=bank, user=user, loan_types=LOAN_TYPES)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('role_selection'))

def get_loan_suggestions(loan_type, amount):
    """Generate attractive loan suggestions based on loan type and amount"""
    suggestions = []
    
    if loan_type == 'home':
        suggestions = [
            {
                'amount': amount,
                'tenure': 20,
                'interest_rate': 7.5,
                'emi': 8500,
                'approval_probability': 92,
                'benefits': ['Lowest interest rate', 'Long tenure option', 'Quick approval']
            },
            {
                'amount': amount,
                'tenure': 15,
                'interest_rate': 7.8,
                'emi': 9500,
                'approval_probability': 95,
                'benefits': ['Higher approval chance', 'Lower total interest', 'Flexible payment']
            }
        ]
    elif loan_type == 'personal':
        suggestions = [
            {
                'amount': amount,
                'tenure': 5,
                'interest_rate': 12.0,
                'emi': 11000,
                'approval_probability': 88,
                'benefits': ['Quick disbursement', 'No collateral needed', 'Flexible usage']
            }
        ]
    
    return suggestions

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample manager accounts
        if not Manager.query.first():
            manager = Manager(
                email='manager@starkbank.com',
                password_hash=generate_password_hash('manager123'),
                name='John Manager',
                bank_id=1
            )
            db.session.add(manager)
            db.session.commit()
    
    app.run(debug=True)
