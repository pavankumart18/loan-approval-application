from datetime import datetime, date
import json
from database import db

class User(db.Model):
    """User model for customers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Financial Information
    monthly_income = db.Column(db.Float, nullable=False)
    other_monthly_income = db.Column(db.Float, default=0.0)
    employment_type = db.Column(db.String(50), nullable=False)  # salaried, self-employed, business, etc.
    employer_name = db.Column(db.String(100))
    employment_tenure_years = db.Column(db.Float, nullable=False)
    
    # Credit Information
    credit_score = db.Column(db.Integer, nullable=False)
    existing_emi = db.Column(db.Float, default=0.0)
    other_monthly_obligations = db.Column(db.Float, default=0.0)
    
    # Banking Information
    bank_id = db.Column(db.Integer, nullable=False)
    savings_balance = db.Column(db.Float, default=0.0)
    bank_account_age_months = db.Column(db.Integer, default=0)
    
    # Authentication
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.full_name}>'
    
    @property
    def total_monthly_income(self):
        return self.monthly_income + (self.other_monthly_income or 0)
    
    @property
    def total_monthly_liabilities(self):
        return self.existing_emi + (self.other_monthly_obligations or 0)
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class Bank(db.Model):
    """Bank model"""
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    interest_rate_base = db.Column(db.Float, nullable=False)
    
    # Relationships
    managers = db.relationship('Manager', backref='bank', lazy=True)
    applications = db.relationship('Application', backref='bank', lazy=True)
    loan_products = db.relationship('LoanProduct', backref='bank', lazy=True)
    
    def __repr__(self):
        return f'<Bank {self.name}>'

class Manager(db.Model):
    """Manager model for bank employees"""
    __tablename__ = 'managers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    processed_applications = db.relationship('Application', backref='manager', lazy=True)
    
    def __repr__(self):
        return f'<Manager {self.name}>'

class LoanProduct(db.Model):
    """Loan product model"""
    __tablename__ = 'loan_products'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)  # personal, home, auto, etc.
    interest_rate = db.Column(db.Float, nullable=False)
    min_amount = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    min_tenure_years = db.Column(db.Integer, nullable=False)
    max_tenure_years = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<LoanProduct {self.name}>'

class Application(db.Model):
    """Loan application model"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    
    # Application Details
    loan_type = db.Column(db.String(50), nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    tenure_years = db.Column(db.Integer, nullable=False)
    down_payment = db.Column(db.Float, default=0.0)
    property_value = db.Column(db.Float, nullable=True)  # For secured loans
    purpose = db.Column(db.String(200))
    
    # Decision Information
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, document_required
    decision = db.Column(db.String(50))  # APPROVED, REJECTED, PARTIAL
    decision_reason = db.Column(db.Text)
    approval_probability = db.Column(db.Float)
    suggestions = db.Column(db.Text)  # JSON string of suggestions
    manager_notes = db.Column(db.Text)
    
    # Calculated Fields
    emi = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    total_interest = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Application {self.id} - {self.loan_type}>'
    
    @property
    def decision_json(self):
        """Parse suggestions JSON"""
        if self.suggestions:
            try:
                return json.loads(self.suggestions)
            except:
                return []
        return []
    
    @decision_json.setter
    def decision_json(self, value):
        """Set suggestions as JSON string"""
        self.suggestions = json.dumps(value) if value else None

class ApplicationLog(db.Model):
    """Audit log for application changes"""
    __tablename__ = 'application_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    
    action = db.Column(db.String(50), nullable=False)  # approve, reject, request_docs, etc.
    previous_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    notes = db.Column(db.Text)
    decision_data = db.Column(db.Text)  # JSON string of decision data
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    application = db.relationship('Application', backref='logs')
    manager = db.relationship('Manager', backref='logs')
    
    def __repr__(self):
        return f'<ApplicationLog {self.action} - {self.timestamp}>'

class GeminiChat(db.Model):
    """Store Gemini chat sessions for users"""
    __tablename__ = 'gemini_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    messages = db.Column(db.Text)  # JSON string of conversation
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='gemini_chats')
    
    def __repr__(self):
        return f'<GeminiChat {self.session_id}>'
    
    @property
    def messages_json(self):
        """Parse messages JSON"""
        if self.messages:
            try:
                return json.loads(self.messages)
            except:
                return []
        return []
    
    @messages_json.setter
    def messages_json(self, value):
        """Set messages as JSON string"""
        self.messages = json.dumps(value) if value else None
