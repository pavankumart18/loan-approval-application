# Stark Bank - Loan Approval Management Application

A comprehensive loan approval management system built with Flask, featuring AI-powered suggestions, automated decision engine, and a beautiful user interface.

## Features

### For Customers
- **Bank Selection**: Choose from multiple banks with competitive rates
- **User Registration/Login**: Secure authentication system
- **Loan Application**: Step-by-step questionnaire for loan applications
- **AI Suggestions**: Personalized loan recommendations powered by Gemini AI
- **Real-time Calculations**: EMI, interest, and approval probability calculations
- **Application Tracking**: View application status and history

### For Managers
- **Application Review**: Review and process loan applications
- **Decision Engine**: Automated approval/rejection with detailed reasoning
- **Customer Management**: View and manage customer details
- **Analytics Dashboard**: Track application statistics and performance

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **AI Integration**: Google Gemini API
- **Architecture**: Model-View-Controller (MVC)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loan_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   ```
   Or create a `.env` file:
   ```
   GOOGLE_API_KEY=your-gemini-api-key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Usage

### Demo Credentials

**Manager Login:**
- Email: `manager@starkbank.com`
- Password: `manager123`

**Customer Registration:**
- Create a new account through the registration form
- Use any valid email and phone number

### Application Flow

1. **Role Selection**: Choose between Customer or Manager
2. **Bank Selection**: Browse and select from available banks
3. **Authentication**: Login or create a new account
4. **Dashboard**: Access main features (Apply Loan, AI Suggestions, etc.)
5. **Loan Application**: Complete the 3-step questionnaire
6. **Manager Review**: Managers can review and approve/reject applications

## Project Structure

```
loan_app/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── services/            # Business logic services
│   ├── __init__.py
│   ├── loan_calculator.py    # Financial calculations
│   ├── decision_engine.py    # Loan approval logic
│   └── gemini_service.py     # AI integration
└── templates/           # HTML templates
    ├── base.html
    ├── role_selection.html
    ├── user_dashboard.html
    ├── bank_selection.html
    ├── user_login.html
    ├── user_register.html
    ├── main_dashboard.html
    ├── loan_application_step1.html
    ├── loan_application_step2.html
    ├── loan_application_step3.html
    ├── manager_login.html
    └── manager_dashboard.html
```

## Key Features Explained

### Loan Calculator Service
- EMI calculations using standard formulas
- DTI (Debt-to-Income) ratio calculations
- LTV (Loan-to-Value) ratio calculations
- Amortization schedule generation
- Interest savings calculations

### Decision Engine
- Automated loan approval/rejection logic
- Policy-based evaluation system
- Risk assessment and scoring
- Suggestion generation for improvements
- Approval probability calculation

### Gemini AI Integration
- Personalized loan recommendations
- Financial health analysis
- Risk profile assessment
- Interactive chat interface
- Fallback suggestions when AI is unavailable

### Database Models
- User management (customers)
- Manager accounts
- Bank information
- Loan products
- Application tracking
- Audit logs

## Configuration

### Loan Policies
The application includes hardcoded loan policies for different loan types:

- **Personal Loans**: Min income ₹12,000, Max DTI 50%, Min credit 600
- **Home Loans**: Min income ₹25,000, Max LTV 85%, Min credit 620
- **Auto Loans**: Min income ₹18,000, Max LTV 85%, Min credit 600
- **Business Loans**: Min income ₹35,000, Min DSCR 1.2, Min credit 640
- **Education Loans**: No min income, Max DTI 60%, Min credit 550
- **Medical Loans**: Min income ₹8,000, Max DTI 60%, No min credit

### Banks Configuration
Five hardcoded banks with different specializations:
- Stark Bank (Home Loans - 7.5%)
- Iron Financial (Personal Loans - 8.2%)
- Captain Credit (Home Loans - 6.8%)
- Thor Trust (Business Loans - 9.1%)
- Hulk Holdings (Auto Loans - 7.8%)

## API Endpoints

### Customer Endpoints
- `GET /` - Role selection page
- `GET /user_dashboard` - Bank selection dashboard
- `GET /bank_selection/<bank_id>` - Bank-specific options
- `GET/POST /user_login/<bank_id>` - Customer login
- `GET/POST /user_register/<bank_id>` - Customer registration
- `GET /main_dashboard` - Customer main dashboard
- `GET/POST /loan_application` - Loan application process
- `GET /gemini_suggestions` - AI loan suggestions

### Manager Endpoints
- `GET/POST /manager_login` - Manager login
- `GET /manager_dashboard` - Manager dashboard
- `POST /approve_application/<app_id>` - Approve/reject applications

## Security Features

- Password hashing using Werkzeug
- Session management
- Role-based access control
- Input validation and sanitization
- CSRF protection (can be added)

## Future Enhancements

1. **Email Notifications**: Send application status updates
2. **Document Upload**: File upload for supporting documents
3. **Payment Integration**: EMI payment tracking
4. **Advanced Analytics**: Detailed reporting and insights
5. **Mobile App**: React Native or Flutter mobile application
6. **API Documentation**: Swagger/OpenAPI documentation
7. **Testing**: Unit and integration tests
8. **Deployment**: Docker containerization and cloud deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
# loan-approval-application
