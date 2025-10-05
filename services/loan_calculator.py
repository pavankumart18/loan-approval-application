import math
from datetime import date

class LoanCalculator:
    """Loan calculation service with all financial formulas"""
    
    def calculate_emi(self, principal, annual_rate_percent, tenure_years):
        """
        Calculate EMI using the standard formula
        EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        
        Args:
            principal: Loan amount (P)
            annual_rate_percent: Annual interest rate in percentage (e.g., 7.5 for 7.5%)
            tenure_years: Loan tenure in years
            
        Returns:
            EMI amount rounded to 2 decimal places
        """
        if principal <= 0:
            return 0.0
        
        if annual_rate_percent <= 0:
            # Zero interest case
            months = tenure_years * 12
            return round(principal / months, 2)
        
        # Convert to monthly rate
        monthly_rate = annual_rate_percent / 100 / 12
        months = tenure_years * 12
        
        # Calculate EMI
        power_factor = (1 + monthly_rate) ** months
        emi = principal * monthly_rate * power_factor / (power_factor - 1)
        
        return round(emi, 2)
    
    def calculate_total_interest(self, principal, annual_rate_percent, tenure_years):
        """Calculate total interest payable over the loan tenure"""
        emi = self.calculate_emi(principal, annual_rate_percent, tenure_years)
        months = tenure_years * 12
        total_payable = emi * months
        total_interest = total_payable - principal
        
        return round(max(0, total_interest), 2)
    
    def calculate_total_payable(self, principal, annual_rate_percent, tenure_years):
        """Calculate total amount payable (principal + interest)"""
        emi = self.calculate_emi(principal, annual_rate_percent, tenure_years)
        months = tenure_years * 12
        
        return round(emi * months, 2)
    
    def calculate_ltv(self, loan_amount, down_payment, property_value):
        """
        Calculate Loan-to-Value ratio
        LTV = (Loan Amount - Down Payment) / Property Value
        """
        if property_value <= 0:
            return 0.0
        
        loan_after_down = max(0, loan_amount - down_payment)
        ltv = loan_after_down / property_value
        
        return round(min(1.0, max(0.0, ltv)), 3)
    
    def calculate_dti(self, total_monthly_income, existing_emi, other_obligations, new_emi):
        """
        Calculate Debt-to-Income ratio
        DTI = (Existing EMI + Other Obligations + New EMI) / Total Monthly Income
        """
        if total_monthly_income <= 0:
            return 1.0  # Max DTI if no income
        
        total_debt = existing_emi + other_obligations + new_emi
        dti = total_debt / total_monthly_income
        
        return round(min(1.0, max(0.0, dti)), 3)
    
    def calculate_dscr(self, net_operating_income, annual_debt_service):
        """
        Calculate Debt Service Coverage Ratio (for business loans)
        DSCR = Net Operating Income / Annual Debt Service
        """
        if annual_debt_service <= 0:
            return 0.0
        
        dscr = net_operating_income / annual_debt_service
        
        return round(max(0.0, dscr), 2)
    
    def calculate_age_at_maturity(self, birth_date, tenure_years):
        """Calculate age at loan maturity"""
        today = date.today()
        maturity_date = date(today.year + tenure_years, today.month, today.day)
        
        age = maturity_date.year - birth_date.year
        if (maturity_date.month, maturity_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    def calculate_effective_collateral_value(self, reported_value, haircut_percent):
        """
        Calculate effective collateral value after applying haircut
        """
        if reported_value <= 0:
            return 0.0
        
        haircut = haircut_percent / 100
        effective_value = reported_value * (1 - haircut)
        
        return round(max(0.0, effective_value), 2)
    
    def generate_amortization_schedule(self, principal, annual_rate_percent, tenure_years):
        """
        Generate monthly amortization schedule
        Returns list of dictionaries with payment details
        """
        if principal <= 0 or annual_rate_percent < 0 or tenure_years <= 0:
            return []
        
        monthly_rate = annual_rate_percent / 100 / 12 if annual_rate_percent > 0 else 0
        months = tenure_years * 12
        
        if monthly_rate == 0:
            # Zero interest case
            monthly_payment = principal / months
            schedule = []
            remaining_balance = principal
            
            for month in range(1, months + 1):
                interest_payment = 0
                principal_payment = monthly_payment
                remaining_balance -= principal_payment
                
                schedule.append({
                    'month': month,
                    'payment': round(monthly_payment, 2),
                    'principal': round(principal_payment, 2),
                    'interest': round(interest_payment, 2),
                    'balance': round(max(0, remaining_balance), 2)
                })
            
            return schedule
        
        # Standard amortization calculation
        emi = self.calculate_emi(principal, annual_rate_percent, tenure_years)
        schedule = []
        remaining_balance = principal
        
        for month in range(1, months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = emi - interest_payment
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': round(emi, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'balance': round(max(0, remaining_balance), 2)
            })
        
        return schedule
    
    def calculate_loan_eligibility(self, monthly_income, monthly_obligations, 
                                 annual_rate_percent, tenure_years, max_dti=0.50):
        """
        Calculate maximum loan amount based on DTI criteria
        """
        if monthly_income <= 0:
            return 0.0
        
        max_monthly_payment = (monthly_income * max_dti) - monthly_obligations
        
        if max_monthly_payment <= 0:
            return 0.0
        
        monthly_rate = annual_rate_percent / 100 / 12 if annual_rate_percent > 0 else 0
        months = tenure_years * 12
        
        if monthly_rate == 0:
            return max_monthly_payment * months
        
        # Calculate principal from EMI using reverse formula
        power_factor = (1 + monthly_rate) ** months
        max_principal = max_monthly_payment * (power_factor - 1) / (monthly_rate * power_factor)
        
        return round(max(0, max_principal), 2)
    
    def calculate_interest_savings(self, principal, tenure_years, rate1, rate2):
        """
        Calculate interest savings between two interest rates
        """
        interest1 = self.calculate_total_interest(principal, rate1, tenure_years)
        interest2 = self.calculate_total_interest(principal, rate2, tenure_years)
        
        savings = interest1 - interest2
        return round(savings, 2)
    
    def calculate_prepayment_savings(self, principal, annual_rate_percent, 
                                   tenure_years, prepayment_amount, prepayment_month):
        """
        Calculate savings from making a prepayment
        """
        # Original schedule
        original_emi = self.calculate_emi(principal, annual_rate_percent, tenure_years)
        original_total = original_emi * (tenure_years * 12)
        
        # Calculate remaining balance at prepayment month
        monthly_rate = annual_rate_percent / 100 / 12
        months = tenure_years * 12
        
        if prepayment_month >= months:
            return 0.0
        
        remaining_balance = principal
        for month in range(1, prepayment_month + 1):
            interest = remaining_balance * monthly_rate
            principal_payment = original_emi - interest
            remaining_balance -= principal_payment
        
        # Apply prepayment
        remaining_balance -= prepayment_amount
        
        if remaining_balance <= 0:
            # Loan fully paid off
            new_emi = original_emi
            new_months = prepayment_month
        else:
            # Recalculate EMI for remaining balance and tenure
            remaining_months = months - prepayment_month
            power_factor = (1 + monthly_rate) ** remaining_months
            new_emi = remaining_balance * monthly_rate * power_factor / (power_factor - 1)
            new_months = remaining_months
        
        new_total = (original_emi * prepayment_month) + (new_emi * new_months)
        savings = original_total - new_total
        
        return round(max(0, savings), 2)
