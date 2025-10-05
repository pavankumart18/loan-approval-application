#!/usr/bin/env python3
"""
Run script for Stark Bank Loan Application
"""

import os
import sys
from app import app, db

def setup_database():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def create_sample_data():
    """Create sample manager account"""
    from models import Manager
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Check if manager already exists
        existing_manager = Manager.query.filter_by(email='manager@starkbank.com').first()
        
        if not existing_manager:
            try:
                manager = Manager(
                    email='manager@starkbank.com',
                    password_hash=generate_password_hash('manager123'),
                    name='John Manager',
                    bank_id=1
                )
                db.session.add(manager)
                db.session.commit()
                print("Sample manager account created!")
                print("Email: manager@starkbank.com")
                print("Password: manager123")
            except Exception as e:
                print("Manager account already exists or creation failed!")
        else:
            print("Sample manager account already exists!")

if __name__ == '__main__':
    print("Starting Stark Bank Loan Application...")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("Application is ready!")
    print("Access the application at: http://localhost:5001")
    print("Manager Login:")
    print("  Email: manager@starkbank.com")
    print("  Password: manager123")
    print("=" * 50)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5001)
