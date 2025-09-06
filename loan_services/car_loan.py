from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
import pickle
import re
from .base_loan import BaseLoanService

class CarLoanService(BaseLoanService):
    """Car Loan Service with ML Model Integration"""
    
    def get_required_fields(self) -> List[str]:
        return [
            # Customer Contact Information
            "Customer_Name",
            "Customer_Email", 
            "Customer_Phone",
            # Model Prediction Fields
            "Age",
            "applicant_annual_salary",
            "Coapplicant_Annual_Income",
            "CIBIL",
            "Car_Type",
            "down_payment_percent",
            "Tenure",
            "loan_amount",
        ]
    
    def get_model_files(self) -> Dict[str, str]:
        return {
            "car_loan_model": "car_loan_models.pkl",
        }
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and professional car loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Customer Information:
- Customer_Name (full name)
- Customer_Email (email address)
- Customer_Phone (10-digit phone number)

Required Car Loan Information:
- Age (applicant's age in years, 18-80)
- applicant_annual_salary (primary applicant's yearly salary in INR)
- Coapplicant_Annual_Income (co-applicant's yearly income in INR, can be 0 if no co-applicant)
- CIBIL (credit score, 300-900, minimum 650 for car loans)
- Car_Type: exactly one of ["Sedan", "SUV", "Hatchback", "Coupe"]
- down_payment_percent (down payment as percentage, 10-50%)
- Tenure (loan repayment period in years, typically 1-7 years)
- loan_amount (desired loan amount in INR)

Guidelines:
1) Be conversational and friendly, like a helpful car loan specialist.
2) Ask 1-2 related questions at a time to avoid overwhelming the customer.
3) Provide brief explanations when needed (e.g., "Down payment is the upfront amount you pay").
4) If user provides partial info, acknowledge it positively and ask for missing details.
5) Validate responses and ask for clarification if unclear.
6) For categorical fields, provide the exact options to choose from.
7) When you have ALL information, say exactly: INFORMATION_COMPLETE
8) Do NOT provide loan predictions - only collect information professionally.

Start by introducing yourself as a car loan specialist."""
    
    def get_fallback_greeting(self) -> str:
        return "Hello! I'm a car loan specialist here to help you with your car loan application. Car loans can help you purchase your dream vehicle with flexible repayment options. Let's start with your full name - what should I call you?"
    
    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        return f"""
Based on the conversation history and the user's latest response, extract any car loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if clearly mentioned):

Customer Information:
- Customer_Name: full name as string
- Customer_Email: email address as string  
- Customer_Phone: 10-digit phone number as string (remove +91, spaces, dashes)

Car Loan Information:
- Age: number (applicant's age in years, 18-80)
- applicant_annual_salary: number in INR (primary applicant's yearly salary, must be positive)
- Coapplicant_Annual_Income: number in INR (co-applicant's yearly income, 0 if none)
- CIBIL: number (300-900, minimum 650 for car loans)
- Car_Type: exactly one of ["Sedan", "SUV", "Hatchback", "Coupe"]
- down_payment_percent: number (down payment percentage, 10-50)
- Tenure: number (loan tenure in years, 1-7)
- loan_amount: number in INR (desired loan amount, must be positive)

Important conversion rules:
- Convert lakhs/crores to actual numbers: "20 lakh" = 2000000, "5 lakh" = 500000, "1.5 crore" = 15000000
- For Car_Type, map variations like "sedan car", "SUV vehicle" to exact options
- Extract only information that is clearly stated

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Age": 30, "applicant_annual_salary": 800000, "Car_Type": "Sedan", "CIBIL": 750}}
""".strip()
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """Validate individual field values with strict eligibility criteria"""
        try:
            if field_name == "Age":
                age = float(value)
                if age < 18:
                    return False, "INELIGIBLE: You must be at least 18 years old to apply for a car loan."
                elif age > 80:
                    return False, "INELIGIBLE: Maximum age limit for car loan is 80 years."
                    
            elif field_name == "CIBIL":
                cibil = float(value)
                if cibil < 650:
                    return False, "INELIGIBLE: A minimum CIBIL score of 650 is required for car loan approval. Your current score does not meet our eligibility criteria."
                elif not (300 <= cibil <= 900):
                    return False, "Please provide a valid CIBIL score between 300 and 900. Could you check and confirm your credit score?"
                    
            elif field_name == "applicant_annual_salary":
                salary = float(value)
                if salary <= 0:
                    return False, "Annual salary must be a positive amount. Please provide your yearly salary."
                elif salary < 300000:  # Minimum 3 lakhs per year
                    return False, "INELIGIBLE: Minimum annual salary of ₹3,00,000 is required for car loan eligibility."
                elif salary > 100000000:  # Maximum 10 crores (reasonable upper limit)
                    return False, "Please verify your annual salary. The amount seems unusually high. Could you confirm your yearly income?"
                    
            elif field_name == "Coapplicant_Annual_Income":
                income = float(value)
                if income < 0:
                    return False, "Co-applicant income cannot be negative. Please provide the co-applicant's yearly income (enter 0 if no co-applicant)."
                elif income > 100000000:  # Maximum 10 crores
                    return False, "Please verify the co-applicant's income. The amount seems unusually high."
                    

                    
            elif field_name == "Car_Type":
                valid_types = ["Sedan", "SUV", "Hatchback", "Coupe"]
                if value not in valid_types:
                    return False, f"Please select your car type from: {', '.join(valid_types)}. Which type of car are you planning to purchase?"
                    
            elif field_name == "down_payment_percent":
                percent = float(value)
                if not (10 <= percent <= 50):
                    return False, "Down payment percentage must be between 10% and 50%. Please specify your down payment percentage."
                    
            elif field_name == "Tenure":
                tenure = float(value)
                if not (1 <= tenure <= 7):
                    return False, "Car loan tenure must be between 1 and 7 years. Please specify your preferred repayment period."
                    
            elif field_name == "loan_amount":
                amount = float(value)
                if amount <= 0:
                    return False, "Loan amount must be a positive amount. Please specify how much loan you need."
                elif amount < 100000:  # Minimum 1 lakh
                    return False, "INELIGIBLE: Minimum loan amount is ₹1,00,000 for car loans."
                elif amount > 50000000:  # Maximum 5 crores
                    return False, "Please verify your loan requirement. The amount seems unusually high for a car loan. Could you confirm the loan amount needed?"
                    
            elif field_name == "Customer_Phone":
                # Remove any spaces, dashes, or other characters
                phone_clean = str(value).replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+91", "")
                if not phone_clean.isdigit() or len(phone_clean) != 10:
                    return False, "Please provide a valid 10-digit phone number (e.g., 9876543210)."
                    
            return True, ""
            
        except (ValueError, TypeError):
            field_display = field_name.replace('_', ' ').lower()
            return False, f"Please provide a valid {field_display} in the correct format."

    def extract_info_from_response(self, user_text: str, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract information from user response with car loan-specific fallback logic"""
        # Try OpenAI first
        if self.client:
            extraction_prompt = self.get_extraction_prompt(user_text, conversation)
            
            try:
                resp = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0,
                    timeout=8  # 8 second timeout for extraction
                )
                extracted_text = resp.choices[0].message.content.strip()
                import json
                m = re.search(r"\{.*\}", extracted_text, re.DOTALL)
                if m:
                    return json.loads(m.group())
            except Exception as e:
                print(f"OpenAI extraction failed: {e}")
        
        # Fallback extraction logic
        extracted = {}
        text_lower = user_text.lower()
        
        # Extract name
        name_patterns = [
            r'my name is ([a-zA-Z\s]+)',
            r'i am ([a-zA-Z\s]+)',
            r'i\'m ([a-zA-Z\s]+)',
            r'call me ([a-zA-Z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip().title()
                if len(name) > 1 and not any(char.isdigit() for char in name):
                    extracted['Customer_Name'] = name
                    break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_text)
        if email_match:
            extracted['Customer_Email'] = email_match.group()
        
        # Extract phone
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
        
        # Extract age
        age_patterns = [
            r'i am (\d+) years? old',
            r'my age is (\d+)',
            r'age.*?(\d+)',
            r'(\d+)\s+years?\s+old'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age = int(match.group(1))
                if 18 <= age <= 80:
                    extracted['Age'] = age
                    break
        
        # Check what the last assistant message was asking for
        last_assistant_msg = ""
        if len(conversation) > 0:
            for msg in reversed(conversation):
                if msg.get('role') == 'assistant':
                    last_assistant_msg = msg.get('content', '').lower()
                    break
        
        # Extract salary/income with lakh/crore conversion
        def convert_amount(amount_str):
            """Convert lakh/crore amounts to numbers"""
            amount_str = amount_str.lower().strip()
            
            # Extract number and unit - handle commas in numbers
            number_match = re.search(r'([\d,]+(?:\.[\d,]+)?)', amount_str)
            if not number_match:
                return None
            
            # Remove commas and convert to float
            number_str = number_match.group(1).replace(',', '')
            try:
                number = float(number_str)
            except ValueError:
                return None
            
            if 'crore' in amount_str:
                return int(number * 10000000)  # 1 crore = 1,00,00,000
            elif 'lakh' in amount_str:
                return int(number * 100000)    # 1 lakh = 1,00,000
            else:
                return int(number)
        
        # Extract salary patterns
        salary_patterns = [
            r'salary.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'earn.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'income.*?([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)',
            r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?).*?salary'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount = convert_amount(match.group(1))
                if amount and amount >= 300000:  # Minimum reasonable salary
                    if 'co' in last_assistant_msg or 'coapplicant' in last_assistant_msg:
                        extracted['Coapplicant_Annual_Income'] = amount
                    else:
                        extracted['applicant_annual_salary'] = amount
                    break
        
        # If asking about salary and user just gives amount
        if any(word in last_assistant_msg for word in ['salary', 'income', 'earn']):
            amount_match = re.search(r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)', text_lower)
            if amount_match:
                amount = convert_amount(amount_match.group(1))
                if amount and amount >= 100000:
                    if 'co' in last_assistant_msg or 'coapplicant' in last_assistant_msg:
                        extracted['Coapplicant_Annual_Income'] = amount
                    else:
                        extracted['applicant_annual_salary'] = amount
        
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
                    extracted['CIBIL'] = score
                    break
        
        # Employment type is not collected from user but will use default in model
        
        # Extract car type
        car_type_map = {
            'sedan': 'Sedan',
            'suv': 'SUV',
            'hatchback': 'Hatchback',
            'coupe': 'Coupe'
        }
        
        for key, value in car_type_map.items():
            if key in text_lower:
                extracted['Car_Type'] = value
                break
        
        # Extract down payment percentage
        down_payment_patterns = [
            r'down.*?payment.*?(\d+)%',
            r'(\d+)%.*?down.*?payment',
            r'down.*?(\d+)\s*percent'
        ]
        
        for pattern in down_payment_patterns:
            match = re.search(pattern, text_lower)
            if match:
                percent = int(match.group(1))
                if 10 <= percent <= 50:
                    extracted['down_payment_percent'] = percent
                    break
        
        # Extract tenure
        tenure_patterns = [
            r'(\d+)\s+years?.*?tenure',
            r'tenure.*?(\d+)\s+years?',
            r'(\d+)\s+years?.*?loan',
            r'repay.*?(\d+)\s+years?'
        ]
        
        for pattern in tenure_patterns:
            match = re.search(pattern, text_lower)
            if match:
                tenure = int(match.group(1))
                if 1 <= tenure <= 7:
                    extracted['Tenure'] = tenure
                    break
        
        # Extract loan amount
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
                if amount and amount >= 100000:  # Minimum 1 lakh
                    extracted['loan_amount'] = amount
                    break
        
        # If asking about loan amount and user just gives amount
        if any(word in last_assistant_msg for word in ['loan amount', 'how much', 'amount need']):
            amount_match = re.search(r'([\d,]+(?:\.[\d,]+)?\s*(?:lakh|crore|lakhs|crores)?)', text_lower)
            if amount_match:
                amount = convert_amount(amount_match.group(1))
                if amount and amount >= 100000:
                    extracted['loan_amount'] = amount
        
        return extracted

    def prepare_model_input(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        """Prepare input data for the car loan model"""
        try:
            # Map categorical values to model format
            car_type_map = {
                "Sedan": 0,
                "SUV": 1,
                "Hatchback": 2,
                "Coupe": 3
            }
            
            # Calculate Total_Annual_Income
            applicant_salary = float(user_input['applicant_annual_salary'])
            coapplicant_income = float(user_input.get('Coapplicant_Annual_Income', 0))
            total_annual_income = applicant_salary + coapplicant_income
            
            # Use default employment type (Salaried = 0) since we don't ask user
            default_employment_type = 0  # Salaried is most common
            
            # Create input dataframe matching your model's expected features
            input_data = {
                'applicant_annual_salary': applicant_salary,
                'Coapplicant_Annual_Income': coapplicant_income,
                'Total_Annual_Income': total_annual_income,
                'CIBIL': float(user_input['CIBIL']),
                'Employment_Type': default_employment_type,  # Default to Salaried
                'Car_Type': car_type_map[user_input['Car_Type']],
                'down_payment_percent': float(user_input['down_payment_percent']),
                'Tenure': float(user_input['Tenure']),
                'Age': float(user_input['Age'])
            }
            
            print(f"Car Loan Input data prepared: {input_data}")
            
            input_df = pd.DataFrame([input_data])
            
            print(f"Prepared input dataframe shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            return input_df
            
        except Exception as e:
            print(f"Error in prepare_model_input: {e}")
            raise e
    
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict car loan amount and interest rate using ML model"""
        try:
            print(f"Car Loan Prediction - Input: {user_input}")
            
            # Prepare input data
            input_df = self.prepare_model_input(user_input)
            print(f"Prepared input shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            # Try to use actual ML model if available
            if self.models.get("car_loan_model"):
                try:
                    print("Using ML model for prediction...")
                    
                    # Load the model bundle
                    bundle = self.models["car_loan_model"]
                    model_max_amt = bundle["model_max_amt"]
                    model_rate = bundle["model_rate"]
                    scaler = bundle["scaler"]
                    label_encoders = bundle["label_encoders"]
                    features = bundle["features"]
                    
                    print("Model components loaded successfully")
                    print(f"Expected features: {features}")
                    
                    # Prepare data for prediction - ensure correct column order
                    df_input = input_df[features]
                    print(f"After feature selection: {list(df_input.columns)}")
                    
                    # Scale the features
                    df_scaled = scaler.transform(df_input)
                    print(f"Data scaled successfully")
                    
                    # Make predictions
                    max_loan_amount = model_max_amt.predict(df_scaled)[0]
                    interest_rate = model_rate.predict(df_scaled)[0]
                    
                    print(f"Raw predictions - Max Loan: {max_loan_amount}, Interest Rate: {interest_rate}")
                    
                    # Ensure reasonable bounds for car loans
                    max_loan_amount = max(max_loan_amount, 100000)    # Min 1 lakh
                    max_loan_amount = min(max_loan_amount, 50000000)  # Max 5 crores
                    interest_rate = max(7.0, min(20.0, interest_rate)) # Between 7% and 20%
                    
                    print(f"Final ML Prediction - Loan: Rs.{max_loan_amount:,.0f}, Rate: {interest_rate:.2f}%")
                    return round(float(max_loan_amount), 0), round(float(interest_rate), 2)
                    
                except Exception as e:
                    print(f"Model prediction error: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"ML model prediction failed: {str(e)}")
            else:
                raise Exception("Car loan ML model not available. Cannot process loan prediction.")
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Car loan prediction failed: {str(e)}")