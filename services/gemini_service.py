import json
import google.generativeai as genai
from datetime import datetime
import os

class GeminiService:
    """Service for Gemini AI integration and loan recommendations"""
    
    def __init__(self):
        # Configure Gemini API (you'll need to set GOOGLE_API_KEY environment variable)
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != 'your-api-key-here':
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.api_available = True
            except Exception as e:
                print(f"Gemini API configuration failed: {e}")
                self.api_available = False
        else:
            self.api_available = False
        
        # Hardcoded loan data for suggestions
        self.LOAN_DATA = {
            'personal': {
                'banks': [
                    {'name': 'Stark Bank', 'rate': 7.5, 'tenure': '1-7 years', 'amount': '₹10K-50L', 'approval_time': '24 hours'},
                    {'name': 'Iron Financial', 'rate': 8.2, 'tenure': '1-5 years', 'amount': '₹25K-30L', 'approval_time': '48 hours'},
                    {'name': 'Captain Credit', 'rate': 7.8, 'tenure': '1-6 years', 'amount': '₹15K-40L', 'approval_time': '24 hours'}
                ],
                'benefits': ['No collateral required', 'Quick approval', 'Flexible usage', 'Competitive rates'],
                'requirements': ['Good credit score', 'Stable income', 'Employment proof', 'Bank statements']
            },
            'home': {
                'banks': [
                    {'name': 'Stark Bank', 'rate': 6.8, 'tenure': '5-30 years', 'amount': '₹1L-1Cr', 'approval_time': '7-10 days'},
                    {'name': 'Captain Credit', 'rate': 6.5, 'tenure': '5-25 years', 'amount': '₹2L-2Cr', 'approval_time': '10-14 days'},
                    {'name': 'Iron Financial', 'rate': 7.2, 'tenure': '5-20 years', 'amount': '₹1L-75L', 'approval_time': '5-7 days'}
                ],
                'benefits': ['Lowest interest rates', 'Long repayment tenure', 'Tax benefits', 'Property ownership'],
                'requirements': ['Property documents', 'Income proof', 'Down payment', 'Credit score 620+']
            },
            'auto': {
                'banks': [
                    {'name': 'Hulk Holdings', 'rate': 7.8, 'tenure': '1-7 years', 'amount': '₹50K-20L', 'approval_time': '2-3 days'},
                    {'name': 'Stark Bank', 'rate': 8.0, 'tenure': '1-5 years', 'amount': '₹1L-25L', 'approval_time': '1-2 days'},
                    {'name': 'Iron Financial', 'rate': 8.5, 'tenure': '1-6 years', 'amount': '₹75K-15L', 'approval_time': '2-4 days'}
                ],
                'benefits': ['Quick processing', 'Vehicle as collateral', 'Competitive rates', 'Flexible tenure'],
                'requirements': ['Vehicle quotation', 'Driving license', 'Income proof', 'Down payment']
            },
            'business': {
                'banks': [
                    {'name': 'Thor Trust', 'rate': 9.1, 'tenure': '1-15 years', 'amount': '₹1L-2Cr', 'approval_time': '10-15 days'},
                    {'name': 'Stark Bank', 'rate': 8.8, 'tenure': '2-12 years', 'amount': '₹5L-1Cr', 'approval_time': '7-12 days'},
                    {'name': 'Iron Financial', 'rate': 9.5, 'tenure': '1-10 years', 'amount': '₹2L-50L', 'approval_time': '5-10 days'}
                ],
                'benefits': ['Business growth support', 'Flexible repayment', 'Working capital', 'Equipment financing'],
                'requirements': ['Business registration', 'Financial statements', 'GST returns', 'Business plan']
            },
            'education': {
                'banks': [
                    {'name': 'Stark Bank', 'rate': 8.5, 'tenure': '1-15 years', 'amount': '₹50K-40L', 'approval_time': '7-10 days'},
                    {'name': 'Captain Credit', 'rate': 9.0, 'tenure': '1-12 years', 'amount': '₹25K-30L', 'approval_time': '5-7 days'},
                    {'name': 'Iron Financial', 'rate': 9.2, 'tenure': '1-10 years', 'amount': '₹1L-25L', 'approval_time': '7-12 days'}
                ],
                'benefits': ['Education investment', 'Moratorium period', 'Low rates', 'Co-signer options'],
                'requirements': ['Admission letter', 'Fee structure', 'Academic records', 'Co-signer income']
            },
            'medical': {
                'banks': [
                    {'name': 'Stark Bank', 'rate': 10.0, 'tenure': '1-5 years', 'amount': '₹10K-20L', 'approval_time': '24 hours'},
                    {'name': 'Iron Financial', 'rate': 11.5, 'tenure': '1-3 years', 'amount': '₹5K-15L', 'approval_time': '48 hours'},
                    {'name': 'Captain Credit', 'rate': 10.5, 'tenure': '1-4 years', 'amount': '₹15K-25L', 'approval_time': '24-48 hours'}
                ],
                'benefits': ['Emergency funding', 'Quick approval', 'No collateral', 'Flexible repayment'],
                'requirements': ['Medical reports', 'Hospital bills', 'Income proof', 'Identity documents']
            }
        }
    
    def get_loan_suggestions(self, user):
        """
        Get personalized loan suggestions based on user profile
        """
        try:
            # Analyze user profile
            user_profile = self._analyze_user_profile(user)
            
            # Get suggestions based on profile
            suggestions = self._generate_personalized_suggestions(user, user_profile)
            
            # Use Gemini for additional insights
            gemini_insights = self._get_gemini_insights(user, user_profile)
            
            return {
                'status': 'success',
                'user_profile': user_profile,
                'suggestions': suggestions,
                'gemini_insights': gemini_insights,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error generating suggestions: {str(e)}',
                'fallback_suggestions': self._get_fallback_suggestions(user)
            }
    
    def _analyze_user_profile(self, user):
        """Analyze user profile and categorize them"""
        profile = {
            'credit_category': self._categorize_credit_score(user.credit_score),
            'income_category': self._categorize_income(user.monthly_income),
            'employment_stability': self._assess_employment_stability(user),
            'risk_profile': self._assess_risk_profile(user),
            'loan_eligibility': self._assess_loan_eligibility(user)
        }
        
        return profile
    
    def _categorize_credit_score(self, credit_score):
        """Categorize credit score"""
        if credit_score >= 750:
            return 'excellent'
        elif credit_score >= 700:
            return 'good'
        elif credit_score >= 650:
            return 'fair'
        elif credit_score >= 600:
            return 'poor'
        else:
            return 'very_poor'
    
    def _categorize_income(self, monthly_income):
        """Categorize monthly income"""
        if monthly_income >= 100000:
            return 'high'
        elif monthly_income >= 50000:
            return 'medium_high'
        elif monthly_income >= 25000:
            return 'medium'
        elif monthly_income >= 15000:
            return 'low_medium'
        else:
            return 'low'
    
    def _assess_employment_stability(self, user):
        """Assess employment stability"""
        if user.employment_tenure_years >= 5:
            return 'very_stable'
        elif user.employment_tenure_years >= 3:
            return 'stable'
        elif user.employment_tenure_years >= 1:
            return 'moderate'
        else:
            return 'unstable'
    
    def _assess_risk_profile(self, user):
        """Assess overall risk profile"""
        score = 0
        
        # Credit score contribution
        credit_category = self._categorize_credit_score(user.credit_score)
        credit_scores = {'excellent': 5, 'good': 4, 'fair': 3, 'poor': 2, 'very_poor': 1}
        score += credit_scores[credit_category]
        
        # Income contribution
        income_category = self._categorize_income(user.monthly_income)
        income_scores = {'high': 5, 'medium_high': 4, 'medium': 3, 'low_medium': 2, 'low': 1}
        score += income_scores[income_category]
        
        # Employment stability contribution
        stability_category = self._assess_employment_stability(user)
        stability_scores = {'very_stable': 5, 'stable': 4, 'moderate': 3, 'unstable': 2}
        score += stability_scores[stability_category]
        
        # DTI contribution
        if user.existing_emi and user.monthly_income:
            dti = user.existing_emi / user.monthly_income
            if dti <= 0.3:
                score += 5
            elif dti <= 0.5:
                score += 4
            elif dti <= 0.7:
                score += 3
            else:
                score += 2
        
        # Categorize risk
        if score >= 18:
            return 'low_risk'
        elif score >= 14:
            return 'medium_risk'
        elif score >= 10:
            return 'high_risk'
        else:
            return 'very_high_risk'
    
    def _assess_loan_eligibility(self, user):
        """Assess loan eligibility across different types"""
        eligibility = {}
        
        for loan_type, data in self.LOAN_DATA.items():
            score = 0
            
            # Credit score check
            min_credit_requirements = {
                'personal': 600, 'home': 620, 'auto': 600,
                'business': 640, 'education': 550, 'medical': 0
            }
            if user.credit_score >= min_credit_requirements[loan_type]:
                score += 3
            
            # Income check
            min_income_requirements = {
                'personal': 12000, 'home': 25000, 'auto': 18000,
                'business': 35000, 'education': 0, 'medical': 8000
            }
            if user.monthly_income >= min_income_requirements[loan_type]:
                score += 2
            
            # Employment stability
            if user.employment_tenure_years >= 1:
                score += 2
            
            # Categorize eligibility
            if score >= 6:
                eligibility[loan_type] = 'high'
            elif score >= 4:
                eligibility[loan_type] = 'medium'
            elif score >= 2:
                eligibility[loan_type] = 'low'
            else:
                eligibility[loan_type] = 'very_low'
        
        return eligibility
    
    def _generate_personalized_suggestions(self, user, profile):
        """Generate personalized loan suggestions"""
        suggestions = []
        
        # Get user's risk profile and eligibility
        risk_profile = profile['risk_profile']
        eligibility = profile['loan_eligibility']
        
        # Recommend loans based on eligibility and risk
        for loan_type, eligibility_level in eligibility.items():
            if eligibility_level in ['high', 'medium']:
                loan_data = self.LOAN_DATA[loan_type]
                
                # Get top 3 banks for this loan type
                top_banks = loan_data['banks'][:3]
                
                for bank in top_banks:
                    suggestion = {
                        'loan_type': loan_type,
                        'bank_name': bank['name'],
                        'interest_rate': bank['rate'],
                        'tenure_range': bank['tenure'],
                        'amount_range': bank['amount'],
                        'approval_time': bank['approval_time'],
                        'eligibility_score': eligibility_level,
                        'benefits': loan_data['benefits'],
                        'requirements': loan_data['requirements'],
                        'personalized_reason': self._get_personalized_reason(user, loan_type, bank)
                    }
                    suggestions.append(suggestion)
        
        # Sort by eligibility score and interest rate
        suggestions.sort(key=lambda x: (
            0 if x['eligibility_score'] == 'high' else 1,
            x['interest_rate']
        ))
        
        return suggestions[:6]  # Return top 6 suggestions
    
    def _get_personalized_reason(self, user, loan_type, bank):
        """Get personalized reason for recommendation"""
        reasons = {
            'personal': f"Based on your ₹{user.monthly_income:,.0f} monthly income and {user.credit_score} credit score, {bank['name']} offers competitive rates for personal loans.",
            'home': f"With your stable income and credit profile, {bank['name']} provides excellent home loan rates starting at {bank['rate']}%.",
            'auto': f"Your employment stability and credit score make you eligible for {bank['name']}'s auto loan at just {bank['rate']}% interest.",
            'business': f"Your business profile qualifies for {bank['name']}'s business loan with {bank['rate']}% interest and flexible tenure.",
            'education': f"Education loans from {bank['name']} at {bank['rate']}% are perfect for your academic goals with your current profile.",
            'medical': f"Emergency medical loans from {bank['name']} are available at {bank['rate']}% with quick approval."
        }
        
        return reasons.get(loan_type, f"{bank['name']} offers competitive rates for your profile.")
    
    def _get_gemini_insights(self, user, profile):
        """Get AI insights from Gemini"""
        if not self.api_available:
            return self._get_fallback_insights(user, profile)
            
        try:
            prompt = f"""
            As a financial advisor, analyze this loan applicant's profile and provide insights:
            
            Profile:
            - Monthly Income: ₹{user.monthly_income:,.0f}
            - Credit Score: {user.credit_score}
            - Employment Type: {user.employment_type}
            - Employment Tenure: {user.employment_tenure_years} years
            - Risk Profile: {profile['risk_profile']}
            - Existing EMI: ₹{user.existing_emi:,.0f}
            
            Provide:
            1. Overall financial health assessment (2-3 sentences)
            2. Top 3 loan recommendations with brief reasons
            3. Key areas to improve for better loan terms
            4. Risk factors to consider
            
            Keep response concise and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return self._get_fallback_insights(user, profile)
    
    def _get_fallback_insights(self, user, profile):
        """Get fallback insights when AI is unavailable"""
        risk_profile = profile['risk_profile']
        income = user.monthly_income
        credit_score = user.credit_score
        
        insights = f"""
        **Financial Health Assessment:**
        Based on your ₹{income:,.0f} monthly income and {credit_score} credit score, you have a {risk_profile.replace('_', ' ')} risk profile. Your financial foundation looks solid for loan applications.

        **Top Loan Recommendations:**
        1. **Personal Loan** - Best for your current profile with competitive rates
        2. **Home Loan** - Consider if you have property as collateral
        3. **Auto Loan** - Good option if you need vehicle financing

        **Improvement Areas:**
        - Maintain consistent income growth
        - Keep credit utilization below 30%
        - Build emergency fund for 6 months expenses

        **Risk Factors:**
        - Monitor existing debt obligations
        - Ensure stable employment history
        - Regular credit score monitoring recommended
        """
        
        return insights
    
    def _get_fallback_suggestions(self, user):
        """Get fallback suggestions when AI is unavailable"""
        suggestions = []
        
        # Basic suggestions based on user profile
        if user.credit_score >= 650 and user.monthly_income >= 25000:
            suggestions.append({
                'loan_type': 'home',
                'bank_name': 'Stark Bank',
                'interest_rate': 6.8,
                'reason': 'Good credit score and income for home loan',
                'eligibility_score': 'high'
            })
        
        if user.credit_score >= 600:
            suggestions.append({
                'loan_type': 'personal',
                'bank_name': 'Iron Financial',
                'interest_rate': 8.2,
                'reason': 'Qualified for personal loan',
                'eligibility_score': 'medium'
            })
        
        return suggestions
    
    def chat_with_gemini(self, user_id, message, session_id=None):
        """Chat interface with Gemini for loan advice"""
        if not self.api_available:
            return {
                'status': 'success',
                'response': 'AI chat service is currently unavailable. Please contact our support team for loan advice.',
                'session_id': session_id or f"chat_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat()
            }
            
        try:
            # Create or get chat session
            if not session_id:
                session_id = f"chat_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare context for Gemini
            context = f"""
            You are a financial advisor helping with loan applications. 
            The user has asked: {message}
            
            Provide helpful, accurate advice about loans, interest rates, and financial planning.
            Keep responses concise and actionable.
            """
            
            response = self.model.generate_content(context)
            
            return {
                'status': 'success',
                'response': response.text,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Chat service unavailable: {str(e)}',
                'session_id': session_id
            }
