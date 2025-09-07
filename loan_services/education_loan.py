



from typing import Dict, List, Any
import pandas as pd
from .base_loan import BaseLoanService

class EducationLoanService(BaseLoanService):
    """Education Loan Service"""
    
    def get_required_fields(self) -> List[str]:
        return [
            "Customer_Name",
            "Customer_Email", 
            "Customer_Phone",
            "Age",
            "Academic_Score",  # Changed from Academic_Performance to Academic_Score
            "Intended_Course",
            "University_Tier",
            "Coapplicant_Income",
            "Guarantor_Networth",
            "CIBIL_Score",
            "Loan_Type",
            "Loan_Term",
            "Expected_Loan_Amount",
        ]
    
    def get_model_files(self) -> Dict[str, str]:
        return {
            "xgb_loan": "xgb_loan_amount_v2.pkl",
            "xgb_interest": "xgb_interest_rate_v2.pkl", 
            "encoders": "encoders_v2.pkl",
            "scaler": "scaler_v2.pkl",
        }
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and professional education loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Fields (collect in this order):
1. Customer_Name (full name)
2. Customer_Email (email address)
3. Customer_Phone (phone number - MUST be exactly 10 digits)
4. Age (MUST be between 18-35 for education loan applicants)
5. Academic_Score (ask for score out of 100, NOT performance level)
6. Intended_Course: one of ["STEM","MBA","Medicine","Finance","Law","Arts","Other"]
7. University_Tier: one of ["Tier1","Tier2","Tier3"]
8. Coapplicant_Income (annual income in INR - MUST be positive)
9. Guarantor_Networth (total assets value in INR - MUST be positive)
10. CIBIL_Score (MUST be between 650-900 for eligibility)
11. Loan_Type: "Secured" (requires collateral) or "Unsecured" (no collateral needed)
12. Loan_Term (MUST be between 1-15 years for education loans)
13. Expected_Loan_Amount (MUST be positive and not exceed ₹3,00,00,000)

VALIDATION RULES - STRICTLY ENFORCE:
- Phone: Exactly 10 digits, reject if invalid
- Age: 18-35 only, reject if outside range
- Academic Score: Ask for number 0-100, convert to grade (90-100=Excellent, 75-89=Good, 60-74=Average, <60=Poor)
- CIBIL: 650-900 required, reject if below 650 (not eligible)
- Loan Amount: Max ₹3,00,00,000, reject if exceeded (not eligible)
- Loan Term: 1-15 years only, reject if outside range
- All monetary values: Must be positive (no negative numbers like -56418)
- Always explain secured vs unsecured: "Secured loans require collateral, unsecured loans don't"

Guidelines:
1) ALWAYS start by asking for their name, email, and phone number first
2) Be conversational and friendly, not robotic
3) Ask 1-2 related questions at a time, don't overwhelm
4) VALIDATE each response according to rules above
5) If invalid, explain why and ask again
6) For academic performance, ask "What's your academic score out of 100?"
7) When you have ALL valid information, say exactly: INFORMATION_COMPLETE
8) Do NOT provide loan advice or predictions - only collect information

Start by introducing yourself and asking for their name first."""
    
    def get_fallback_greeting(self) -> str:
        return "Hello! I'm here to help you with your education loan application. To get started, may I have your full name please?"
    
    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """Validate individual field values according to education loan rules"""
        try:
            if field_name == "Customer_Phone":
                if not str(value).isdigit() or len(str(value)) != 10:
                    return False, "Invalid phone number. Phone number must be exactly 10 digits."
            
            elif field_name == "Age":
                age = int(value)
                if age < 18 or age > 35:
                    return False, "Invalid age. For education loan applicants, age must be between 18-35."
            
            elif field_name == "Academic_Score":
                score = float(value)
                if score < 0:
                    return False, "Invalid score. Please enter a real quantity (score cannot be negative)."
                elif score > 100:
                    return False, "Invalid score. Please enter a real quantity (score cannot exceed 100)."
            
            elif field_name == "CIBIL_Score":
                cibil = int(value)
                if cibil < 650:
                    return False, "You are not eligible. CIBIL score must be at least 650 for education loan."
                elif cibil > 900:
                    return False, "Invalid CIBIL score. CIBIL score cannot exceed 900."
            
            elif field_name == "Expected_Loan_Amount":
                amount = float(value)
                if amount <= 0:
                    return False, "Invalid loan amount. All values must be positive."
                elif amount > 30000000:  # 3 crores
                    return False, "Not eligible. Loan amount cannot exceed ₹3,00,00,000."
            
            elif field_name == "Loan_Term":
                term = int(value)
                if term <= 0:
                    return False, "Invalid loan term. All values must be positive."
                elif term < 1 or term > 15:
                    return False, "Invalid loan term. Education loan term must be between 1-15 years."
            
            elif field_name in ["Coapplicant_Income", "Guarantor_Networth"]:
                amount = float(value)
                if amount <= 0:
                    return False, f"Invalid {field_name.lower().replace('_', ' ')}. All values must be positive (negative values like -56418 are not possible)."
            
            return True, "Valid"
            
        except (ValueError, TypeError):
            return False, f"Invalid {field_name.lower().replace('_', ' ')}. Please enter a valid number."
    
    def convert_academic_score_to_performance(self, score: float) -> str:
        """Convert numeric academic score to performance grade"""
        if 90 <= score <= 100:
            return "Excellent"
        elif 75 <= score < 90:
            return "Good"
        elif 60 <= score < 75:
            return "Average"
        else:
            return "Poor"

    def extract_info_from_response(self, user_text: str, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Enhanced extraction for education loans with better pattern matching"""
        # Try OpenAI first
        if self.client:
            try:
                extraction_prompt = self.get_extraction_prompt(user_text, conversation)
                resp = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0,
                    timeout=8
                )
                extracted_text = resp.choices[0].message.content.strip()
                import json
                import re
                m = re.search(r"\{.*\}", extracted_text, re.DOTALL)
                if m:
                    return json.loads(m.group())
            except Exception as e:
                print(f"OpenAI extraction failed: {e}")
        
        # Enhanced fallback extraction
        extracted = {}
        text_lower = user_text.lower().strip()
        
        # Extract name - more flexible patterns
        name_patterns = [
            r'my name is ([a-zA-Z\s]+)',
            r'i am ([a-zA-Z\s]+)',
            r'i\'m ([a-zA-Z\s]+)',
            r'call me ([a-zA-Z\s]+)',
            r'name\s*:?\s*([a-zA-Z\s]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip().title()
                if len(name) > 1 and not any(char.isdigit() for char in name):
                    extracted['Customer_Name'] = name
                    break
        
        # If no pattern matched but looks like just a name
        if not extracted.get('Customer_Name'):
            last_assistant_msg = ""
            if len(conversation) > 0:
                for msg in reversed(conversation):
                    if msg.get('role') == 'assistant':
                        last_assistant_msg = msg.get('content', '').lower()
                        break
            
            if 'name' in last_assistant_msg and len(text_lower.split()) <= 3:
                if re.match(r'^[a-zA-Z\s]+$', user_text.strip()) and 2 <= len(user_text.strip()) <= 50:
                    extracted['Customer_Name'] = user_text.strip().title()
        
        # Extract email - improved pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_text)
        if email_match:
            extracted['Customer_Email'] = email_match.group(0)
        
        # Extract phone - handle various formats
        phone_patterns = [
            r'(\+91[\s-]?)?([6-9]\d{9})',
            r'(\d{10})',
            r'(\d{3}[\s-]\d{3}[\s-]\d{4})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, user_text)
            if match:
                phone = re.sub(r'[^\d]', '', match.group())
                if phone.startswith('91') and len(phone) == 12:
                    phone = phone[2:]
                if len(phone) == 10 and phone[0] in '6789':
                    extracted['Customer_Phone'] = phone
                    break
        
        # Extract age - multiple patterns
        age_patterns = [
            r'i am (\d+) years? old',
            r'my age is (\d+)',
            r'age\s*:?\s*(\d+)',
            r'(\d+)\s+years?\s+old',
            r'^(\d+)$'  # Just a number when asked for age
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age = int(match.group(1))
                if 18 <= age <= 35:
                    extracted['Age'] = age
                    break
        
        # Extract academic score
        score_patterns = [
            r'academic score.*?(\d+)',
            r'score.*?(\d+)',
            r'(\d+)%',
            r'(\d+)\s*percent',
            r'^(\d+)$'  # Just a number when asked for score
        ]
        
        last_assistant_msg = ""
        if len(conversation) > 0:
            for msg in reversed(conversation):
                if msg.get('role') == 'assistant':
                    last_assistant_msg = msg.get('content', '').lower()
                    break
        
        for pattern in score_patterns:
            match = re.search(pattern, text_lower)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    extracted['Academic_Score'] = score
                    break
        
        # If asking about score and user just gives number
        if 'score' in last_assistant_msg and re.match(r'^\d+$', user_text.strip()):
            score = int(user_text.strip())
            if 0 <= score <= 100:
                extracted['Academic_Score'] = score
        
        # Extract intended course
        course_map = {
            'stem': 'STEM',
            'mba': 'MBA', 
            'medicine': 'Medicine',
            'medical': 'Medicine',
            'finance': 'Finance',
            'law': 'Law',
            'arts': 'Arts',
            'other': 'Other'
        }
        
        for key, value in course_map.items():
            if key in text_lower:
                extracted['Intended_Course'] = value
                break
        
        # Extract university tier
        tier_patterns = [
            r'tier\s*(\d)',
            r'tier(\d)',
            r'(\d)\s*tier'
        ]
        
        for pattern in tier_patterns:
            match = re.search(pattern, text_lower)
            if match:
                tier_num = match.group(1)
                if tier_num in ['1', '2', '3']:
                    extracted['University_Tier'] = f'Tier{tier_num}'
                    break
        
        # Extract amounts with lakh/crore conversion
        def convert_amount(amount_str):
            amount_str = amount_str.lower().strip()
            number_match = re.search(r'([\d,]+(?:\.[\d,]+)?)', amount_str)
            if not number_match:
                return None
            
            number_str = number_match.group(1).replace(',', '')
            try:
                number = float(number_str)
            except ValueError:
                return None
            
            if 'crore' in amount_str:
                return int(number * 10000000)
            elif 'lakh' in amount_str:
                return int(number * 100000)
            else:
                return int(number)
        
        # Extract coapplicant income
        income_patterns = [
            r'coapplicant.*?income.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'co.*?applicant.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?).*?coapplicant'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount = convert_amount(match.group(1))
                if amount and amount > 0:
                    extracted['Coapplicant_Income'] = amount
                    break
        
        # Extract guarantor networth
        networth_patterns = [
            r'guarantor.*?networth.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'guarantor.*?assets.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'networth.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'assets.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)'
        ]
        
        for pattern in networth_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount = convert_amount(match.group(1))
                if amount and amount > 0:
                    extracted['Guarantor_Networth'] = amount
                    break
        
        # Extract CIBIL score
        cibil_patterns = [
            r'cibil.*?(\d{3})',
            r'credit.*?score.*?(\d{3})',
            r'(\d{3}).*?cibil',
            r'(\d{3}).*?credit.*?score'
        ]
        
        for pattern in cibil_patterns:
            match = re.search(pattern, text_lower)
            if match:
                score = int(match.group(1))
                if 300 <= score <= 900:
                    extracted['CIBIL_Score'] = score
                    break
        
        # Extract loan type
        if 'secured' in text_lower:
            extracted['Loan_Type'] = 'Secured'
        elif 'unsecured' in text_lower:
            extracted['Loan_Type'] = 'Unsecured'
        
        # Extract loan term
        term_patterns = [
            r'(\d+)\s+years?.*?term',
            r'term.*?(\d+)\s+years?',
            r'(\d+)\s+years?.*?loan',
            r'loan.*?(\d+)\s+years?'
        ]
        
        for pattern in term_patterns:
            match = re.search(pattern, text_lower)
            if match:
                term = int(match.group(1))
                if 1 <= term <= 15:
                    extracted['Loan_Term'] = term
                    break
        
        # If asking about term and user just gives number
        if 'term' in last_assistant_msg or 'years' in last_assistant_msg:
            if re.match(r'^\d+$', user_text.strip()):
                term = int(user_text.strip())
                if 1 <= term <= 15:
                    extracted['Loan_Term'] = term
        
        # Extract expected loan amount
        loan_amount_patterns = [
            r'need.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'want.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'loan.*?amount.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?).*?loan'
        ]
        
        for pattern in loan_amount_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount = convert_amount(match.group(1))
                if amount and amount > 0:
                    extracted['Expected_Loan_Amount'] = amount
                    break
        
        # If asking about loan amount and user just gives amount
        if 'loan amount' in last_assistant_msg or 'how much' in last_assistant_msg:
            amount_match = re.search(r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)', text_lower)
            if amount_match:
                amount = convert_amount(amount_match.group(1))
                if amount and amount > 0:
                    extracted['Expected_Loan_Amount'] = amount
        
        return extracted

    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        return f"""
Based on the conversation history and the user's latest response, extract any education loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if mentioned):
- Customer_Name: full name as text
- Customer_Email: email address as text
- Customer_Phone: phone number as text (must be 10 digits)
- Age: number (must be 18-35)
- Academic_Score: number (0-100, will be converted to performance grade)
- Intended_Course: exactly one of ["STEM","MBA","Medicine","Finance","Law","Arts","Other"]
- University_Tier: exactly one of ["Tier1","Tier2","Tier3"]
- Coapplicant_Income: number in INR (must be positive)
- Guarantor_Networth: number in INR (must be positive)
- CIBIL_Score: number (must be 650-900)
- Loan_Type: exactly one of ["Secured","Unsecured"]
- Loan_Term: number (must be 1-15 years)
- Expected_Loan_Amount: number in INR (must be positive, max 30000000)

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Customer_Email": "john@example.com", "Age": 25, "Academic_Score": 85}}
""".strip()
    
    def repayment_capacity(self, income: float, networth: float, cibil: float) -> float:
        """Calculate repayment capacity for education loans"""
        return (income * 4) + (networth * 0.05) + (cibil / 2)
    
    def convert_academic_score_to_performance(self, score: float) -> str:
        """Convert academic score (0-100) to performance category"""
        if score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Average"
        else:
            return "Poor"
    
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict education loan amount and interest rate"""
        if not all([self.models.get("xgb_loan"), self.models.get("xgb_interest"), 
                   self.models.get("encoders"), self.models.get("scaler")]):
            raise ValueError("Required models not loaded")
        
        # Create a copy to avoid modifying original
        processed_input = user_input.copy()
        
        # Convert Academic_Score to Academic_Performance if needed
        if "Academic_Score" in processed_input and "Academic_Performance" not in processed_input:
            processed_input["Academic_Performance"] = self.convert_academic_score_to_performance(
                float(processed_input["Academic_Score"])
            )
        
        # Add computed feature
        processed_input["Repayment_Capacity"] = self.repayment_capacity(
            processed_input["Coapplicant_Income"],
            processed_input["Guarantor_Networth"],
            processed_input["CIBIL_Score"]
        )
        
        # Encode categorical variables
        encoders = self.models["encoders"]
        for col in ["Academic_Performance", "Intended_Course", "University_Tier", "Loan_Type"]:
            if col not in encoders:
                raise ValueError(f"Encoder for {col} not found.")
            processed_input[col] = encoders[col].transform([processed_input[col]])[0]
        
        # Prepare features for prediction
        features = [
            "Age", "Academic_Performance", "Intended_Course", "University_Tier",
            "Coapplicant_Income", "Guarantor_Networth", "CIBIL_Score",
            "Loan_Type", "Repayment_Capacity", "Loan_Term"
        ]
        
        X = pd.DataFrame([{k: processed_input[k] for k in features}])
        
        # Scale numeric features
        numeric_cols = ["Age", "Coapplicant_Income", "Guarantor_Networth", 
                       "CIBIL_Score", "Repayment_Capacity", "Loan_Term"]
        X[numeric_cols] = self.models["scaler"].transform(X[numeric_cols])
        
        # Make predictions
        loan_amt = self.models["xgb_loan"].predict(X)[0]
        interest = self.models["xgb_interest"].predict(X)[0]
        
        return round(float(loan_amt)), round(float(interest), 2)