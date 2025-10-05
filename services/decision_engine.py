import json
from datetime import date
from .loan_calculator import LoanCalculator

class DecisionEngine:
    """Loan decision engine with business rules and scoring"""
    
    def __init__(self):
        self.calculator = LoanCalculator()
        
        # Policy thresholds
        self.POLICIES = {
            "personal": {
                "min_income": 12000,
                "max_dti": 0.50,
                "max_ltv": None,
                "min_credit": 600,
                "min_tenure_years": 0.5,
                "max_loan_multiple": 20,
                "min_age": 21,
                "max_age": 65
            },
            "home": {
                "min_income": 25000,
                "max_dti": 0.50,
                "max_ltv": 0.85,
                "min_credit": 620,
                "min_tenure_years": 1,
                "max_tenure_years": 30,
                "min_age": 21,
                "max_age": 65
            },
            "auto": {
                "min_income": 18000,
                "max_dti": 0.50,
                "max_ltv": 0.85,
                "min_credit": 600,
                "min_tenure_years": 0.5,
                "max_tenure_years": 7,
                "min_age": 21,
                "max_age": 65
            },
            "business": {
                "min_income": 35000,
                "max_dti": 0.45,
                "max_ltv": None,
                "min_credit": 640,
                "min_tenure_years": 2,
                "max_tenure_years": 15,
                "min_age": 21,
                "max_age": 65,
                "min_dscr": 1.2
            },
            "education": {
                "min_income": 0,
                "max_dti": 0.60,
                "max_ltv": None,
                "min_credit": 550,
                "min_tenure_years": 0,
                "max_tenure_years": 15,
                "min_age": 18,
                "max_age": 65
            },
            "medical": {
                "min_income": 8000,
                "max_dti": 0.60,
                "max_ltv": None,
                "min_credit": 0,
                "min_tenure_years": 0,
                "max_tenure_years": 5,
                "min_age": 18,
                "max_age": 80
            }
        }
        
        # Tolerances for borderline cases
        self.DTI_TOLERANCE = 0.05
        self.LTV_TOLERANCE = 0.05
        self.CREDIT_TOLERANCE = 20
        
        # Scoring weights
        self.SCORING_WEIGHTS = {
            'credit_index': 0.35,
            'dti_index': 0.30,
            'tenure_index': 0.10,
            'ltv_index': 0.10,
            'income_index': 0.15
        }
    
    def evaluate_application(self, application, user):
        """
        Main decision function - evaluates loan application
        
        Args:
            application: Application object
            user: User object
            
        Returns:
            dict with decision details
        """
        loan_type = application.loan_type
        policy = self.POLICIES.get(loan_type, self.POLICIES['personal'])
        
        # Calculate basic metrics
        metrics = self._calculate_metrics(application, user, policy)
        
        # Run policy checks
        failed_checks = self._run_policy_checks(application, user, policy, metrics)
        
        # Determine decision
        decision = self._make_decision(failed_checks, metrics, policy)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(failed_checks, application, user, policy, metrics)
        
        # Calculate approval probability
        probability = self._calculate_approval_probability(metrics, failed_checks)
        
        return {
            'status': decision['status'],
            'reason': decision['reason'],
            'probability': probability,
            'suggestions': suggestions,
            'metrics': metrics,
            'failed_checks': failed_checks
        }
    
    def _calculate_metrics(self, application, user, policy):
        """Calculate all financial metrics"""
        # Basic calculations
        projected_emi = self.calculator.calculate_emi(
            application.amount_requested,
            7.5,  # Default interest rate - should come from bank/product
            application.tenure_years
        )
        
        total_income = user.total_monthly_income
        total_liabilities = user.total_monthly_liabilities
        
        dti = self.calculator.calculate_dti(
            total_income,
            user.existing_emi,
            user.other_monthly_obligations or 0,
            projected_emi
        )
        
        ltv = self.calculator.calculate_ltv(
            application.amount_requested,
            application.down_payment or 0,
            application.property_value or 0
        ) if application.property_value else None
        
        age_at_maturity = self.calculator.calculate_age_at_maturity(
            user.dob,
            application.tenure_years
        )
        
        # Calculate indices for scoring
        credit_index = self._normalize_credit_score(user.credit_score)
        dti_index = self._calculate_dti_index(dti, policy['max_dti'])
        tenure_index = self._calculate_tenure_index(user.employment_tenure_years)
        ltv_index = self._calculate_ltv_index(ltv, policy.get('max_ltv')) if ltv else 1.0
        income_index = self._calculate_income_index(total_income, policy['min_income'])
        
        return {
            'projected_emi': projected_emi,
            'total_income': total_income,
            'total_liabilities': total_liabilities,
            'dti': dti,
            'ltv': ltv,
            'age_at_maturity': age_at_maturity,
            'credit_index': credit_index,
            'dti_index': dti_index,
            'tenure_index': tenure_index,
            'ltv_index': ltv_index,
            'income_index': income_index
        }
    
    def _run_policy_checks(self, application, user, policy, metrics):
        """Run all policy checks and return failed ones"""
        failed_checks = []
        
        # Age check
        if metrics['age_at_maturity'] < policy['min_age']:
            failed_checks.append({
                'check': 'age_maturity',
                'value': metrics['age_at_maturity'],
                'threshold': policy['min_age'],
                'message': f"Age at maturity ({metrics['age_at_maturity']}) is below minimum ({policy['min_age']})"
            })
        elif metrics['age_at_maturity'] > policy['max_age']:
            failed_checks.append({
                'check': 'age_maturity',
                'value': metrics['age_at_maturity'],
                'threshold': policy['max_age'],
                'message': f"Age at maturity ({metrics['age_at_maturity']}) exceeds maximum ({policy['max_age']})"
            })
        
        # Income check
        if policy['min_income'] > 0 and metrics['total_income'] < policy['min_income']:
            failed_checks.append({
                'check': 'min_income',
                'value': metrics['total_income'],
                'threshold': policy['min_income'],
                'message': f"Monthly income (₹{metrics['total_income']:,.0f}) is below minimum (₹{policy['min_income']:,.0f})"
            })
        
        # Employment tenure check
        if user.employment_tenure_years < policy['min_tenure_years']:
            failed_checks.append({
                'check': 'min_tenure',
                'value': user.employment_tenure_years,
                'threshold': policy['min_tenure_years'],
                'message': f"Employment tenure ({user.employment_tenure_years} years) is below minimum ({policy['min_tenure_years']} years)"
            })
        
        # Credit score check
        if user.credit_score < policy['min_credit']:
            failed_checks.append({
                'check': 'min_credit',
                'value': user.credit_score,
                'threshold': policy['min_credit'],
                'message': f"Credit score ({user.credit_score}) is below minimum ({policy['min_credit']})"
            })
        
        # DTI check
        if metrics['dti'] > policy['max_dti']:
            failed_checks.append({
                'check': 'dti',
                'value': metrics['dti'],
                'threshold': policy['max_dti'],
                'message': f"Debt-to-Income ratio ({metrics['dti']:.1%}) exceeds maximum ({policy['max_dti']:.1%})"
            })
        
        # LTV check (for secured loans)
        if policy['max_ltv'] and metrics['ltv'] and metrics['ltv'] > policy['max_ltv']:
            failed_checks.append({
                'check': 'ltv',
                'value': metrics['ltv'],
                'threshold': policy['max_ltv'],
                'message': f"Loan-to-Value ratio ({metrics['ltv']:.1%}) exceeds maximum ({policy['max_ltv']:.1%})"
            })
        
        # Tenure check
        if 'max_tenure_years' in policy and application.tenure_years > policy['max_tenure_years']:
            failed_checks.append({
                'check': 'max_tenure',
                'value': application.tenure_years,
                'threshold': policy['max_tenure_years'],
                'message': f"Loan tenure ({application.tenure_years} years) exceeds maximum ({policy['max_tenure_years']} years)"
            })
        
        return failed_checks
    
    def _make_decision(self, failed_checks, metrics, policy):
        """Make final decision based on failed checks"""
        if not failed_checks:
            return {
                'status': 'APPROVED',
                'reason': 'All policy checks passed'
            }
        
        # Identify borderline cases
        borderline = []
        hard_fails = []
        
        for check in failed_checks:
            if self._is_borderline(check, policy):
                borderline.append(check)
            else:
                hard_fails.append(check)
        
        if hard_fails:
            reasons = [check['message'] for check in hard_fails]
            return {
                'status': 'REJECTED',
                'reason': '; '.join(reasons)
            }
        
        if borderline:
            # Calculate partial approval amount
            approved_amount = min(
                metrics.get('projected_emi', 0) * 60,  # 60 months cap
                metrics['total_income'] * 20  # 20x monthly income cap
            )
            
            reasons = [check['message'] for check in borderline]
            return {
                'status': 'PARTIAL',
                'reason': 'Borderline case - partial approval possible: ' + '; '.join(reasons),
                'approved_amount': approved_amount
            }
        
        return {
            'status': 'REJECTED',
            'reason': 'Policy checks failed'
        }
    
    def _is_borderline(self, check, policy):
        """Check if a failed check is borderline (within tolerance)"""
        check_type = check['check']
        
        if check_type == 'dti' and check['value'] <= policy['max_dti'] + self.DTI_TOLERANCE:
            return True
        elif check_type == 'ltv' and policy['max_ltv'] and check['value'] <= policy['max_ltv'] + self.LTV_TOLERANCE:
            return True
        elif check_type == 'min_credit' and check['value'] >= policy['min_credit'] - self.CREDIT_TOLERANCE:
            return True
        
        return False
    
    def _generate_suggestions(self, failed_checks, application, user, policy, metrics):
        """Generate actionable suggestions to improve approval chances"""
        suggestions = []
        
        for check in failed_checks:
            if check['check'] == 'dti':
                suggestions.append({
                    'type': 'reduce_tenure',
                    'title': 'Reduce Loan Tenure',
                    'description': f"Reduce tenure by 2-3 years to lower EMI and improve DTI ratio",
                    'impact': 'High',
                    'actionable': True
                })
                suggestions.append({
                    'type': 'reduce_amount',
                    'title': 'Reduce Loan Amount',
                    'description': f"Consider reducing loan amount by 10-15% to improve approval chances",
                    'impact': 'High',
                    'actionable': True
                })
            
            elif check['check'] == 'min_income':
                suggestions.append({
                    'type': 'add_coapplicant',
                    'title': 'Add Co-applicant',
                    'description': 'Add a co-applicant with income to meet minimum income requirements',
                    'impact': 'High',
                    'actionable': True
                })
            
            elif check['check'] == 'ltv':
                suggestions.append({
                    'type': 'increase_down_payment',
                    'title': 'Increase Down Payment',
                    'description': f"Increase down payment by ₹{int(application.property_value * 0.1):,} to improve LTV ratio",
                    'impact': 'High',
                    'actionable': True
                })
            
            elif check['check'] == 'min_credit':
                suggestions.append({
                    'type': 'improve_credit',
                    'title': 'Improve Credit Score',
                    'description': 'Work on improving credit score by paying existing debts on time',
                    'impact': 'Medium',
                    'actionable': False
                })
        
        # Add general suggestions
        if not suggestions:
            suggestions.append({
                'type': 'standard',
                'title': 'Application Looks Good',
                'description': 'Your application meets all basic requirements',
                'impact': 'Low',
                'actionable': False
            })
        
        return suggestions
    
    def _calculate_approval_probability(self, metrics, failed_checks):
        """Calculate approval probability based on scoring"""
        if not failed_checks:
            return 95.0  # High probability if no failed checks
        
        # Calculate weighted score
        score = (
            metrics['credit_index'] * self.SCORING_WEIGHTS['credit_index'] +
            metrics['dti_index'] * self.SCORING_WEIGHTS['dti_index'] +
            metrics['tenure_index'] * self.SCORING_WEIGHTS['tenure_index'] +
            metrics['ltv_index'] * self.SCORING_WEIGHTS['ltv_index'] +
            metrics['income_index'] * self.SCORING_WEIGHTS['income_index']
        )
        
        # Convert to percentage and adjust based on failed checks
        base_probability = score * 100
        
        # Reduce probability based on number and severity of failed checks
        penalty = len(failed_checks) * 15
        probability = max(0, base_probability - penalty)
        
        return round(probability, 1)
    
    # Helper methods for index calculations
    def _normalize_credit_score(self, credit_score):
        """Normalize credit score to 0-1 index"""
        return max(0, min(1, (credit_score - 300) / (850 - 300)))
    
    def _calculate_dti_index(self, dti, max_dti):
        """Calculate DTI goodness index (lower DTI = higher index)"""
        if max_dti is None:
            return 1.0
        return max(0, min(1, 1 - (dti / max_dti)))
    
    def _calculate_tenure_index(self, employment_tenure_years):
        """Calculate employment tenure index"""
        return min(1.0, employment_tenure_years / 5.0)
    
    def _calculate_ltv_index(self, ltv, max_ltv):
        """Calculate LTV goodness index (lower LTV = higher index)"""
        if max_ltv is None or ltv is None:
            return 1.0
        return max(0, min(1, 1 - (ltv / max_ltv)))
    
    def _calculate_income_index(self, income, min_income):
        """Calculate income adequacy index"""
        if min_income <= 0:
            return 1.0
        return min(1.0, income / (min_income * 1.5))  # 1.5x minimum is considered excellent
