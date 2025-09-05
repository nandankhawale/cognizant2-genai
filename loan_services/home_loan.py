from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from .base_loan import BaseLoanService

class HomeLoanService(BaseLoanService):
    """Home Loan Service with XGBoost Model Integration"""
    
    def get_required_fields(self) -> List[str]:
        return [
            "Customer_Name",
            "Customer_Email",
            "Customer_Phone",
            "Age",
            "Income",  # Changed from Monthly_Income to match model
            "Guarantor_income",
            "Tenure",  # Changed from Loan_Term to match model
            "CIBIL_score",  # Changed from CIBIL_Score to match model
            "Employment_type",  # Changed from Employment_Type to match model
            "Down_payment",
            "Existing_total_EMI",  # Changed from Existing_EMI to match model
            "Loan_amount_requested",  # Changed from Expected_Loan_Amount to match model
            "Property_value",  # Changed from Property_Value to match model
        ]
    
    def get_model_files(self) -> Dict[str, str]:
        return {
            "loan_amount_model": "loan_amount_model.pkl",
            "interest_rate_model": "interest_rate_model.pkl",
        }
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and professional home loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Customer Information:
- Customer_Name (full name)
- Customer_Email (email address)
- Customer_Phone (10-digit phone number)

Required Loan Information:
- Age (21-50 years - strict eligibility criteria)
- Income (monthly income in INR)
- Guarantor_income (guarantor's monthly income in INR, can be 0 if no guarantor)
- Tenure (loan repayment period in years, typically 5-30)
- CIBIL_score (credit score minimum 650 required for eligibility)
- Employment_type: exactly one of ["Business Owner", "Salaried", "Government Employee", "Self-Employed"]
- Down_payment (amount you can pay upfront in INR)
- Existing_total_EMI (current monthly EMI obligations in INR, can be 0)
- Loan_amount_requested (desired loan amount in INR)
- Property_value (total property value in INR)

Guidelines:
1) Be conversational and friendly, like a helpful bank representative.
2) Ask 1-2 related questions at a time to avoid overwhelming the customer.
3) Provide brief explanations when needed (e.g., "CIBIL score is your credit score", "LTV is loan-to-value ratio").
4) If user provides partial info, acknowledge it positively and ask for missing details.
5) Validate responses and ask for clarification if unclear.
6) For Employment_type, ensure it's exactly one of the four options.
7) When you have ALL information, say exactly: INFORMATION_COMPLETE
8) Do NOT provide loan predictions - only collect information professionally.

Start by introducing yourself as a home loan specialist and asking about their home buying plans."""
    
    def get_fallback_greeting(self) -> str:
        return "Hello! I'm a home loan specialist. I'm here to help you with your home loan application. Let's start with your full name - what should I call you?"
    
    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        return f"""
Based on the conversation history and the user's latest response, extract any home loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if clearly mentioned):

Customer Information:
- Customer_Name: full name as string
- Customer_Email: email address as string  
- Customer_Phone: 10-digit phone number as string (remove +91, spaces, dashes)

Loan Information:
- Age: number (21-50, strict requirement)
- Income: number in INR (monthly income, must be positive)
- Guarantor_income: number in INR (guarantor's monthly income, 0 if none)
- Tenure: number (loan term in years, 5-30)
- CIBIL_score: number (minimum 650 required)
- Employment_type: exactly one of ["Business Owner", "Salaried", "Government Employee", "Self-Employed"]
- Down_payment: number in INR (upfront payment amount)
- Existing_total_EMI: number in INR (current monthly EMIs, 0 if none)
- Loan_amount_requested: number in INR (desired loan amount)
- Property_value: number in INR (total property value)

Important:
- For Employment_type, map variations like "business", "govt", "self employed" to exact options
- Convert lakhs/crores to actual numbers (e.g., "50 lakhs" = 5000000)
- Extract only information that is clearly stated

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Age": 35, "Employment_type": "Salaried", "Income": 80000, "Property_value": 5000000}}
""".strip()
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """Validate individual field values with user-friendly messages"""
        try:
            if field_name == "Age":
                age = float(value)
                if not (21 <= age <= 50):
                    return False, "I need your age to be between 21 and 50 years for home loan eligibility. Could you please confirm your age?"
                    
            elif field_name == "CIBIL_score":
                cibil = float(value)
                if cibil < 650:
                    return False, "Sorry, for home loans we require a minimum CIBIL score of 650. Unfortunately, your current score doesn't meet our eligibility criteria."
                elif not (300 <= cibil <= 900):
                    return False, "Your CIBIL score should be between 300 and 900. Could you please check and provide your correct credit score?"
                    
            elif field_name == "Employment_type":
                valid_types = ["Business Owner", "Salaried", "Government Employee", "Self-Employed"]
                if value not in valid_types:
                    return False, f"For employment type, please choose from: {', '.join(valid_types)}. Which category best describes your employment?"
                    
            elif field_name == "Tenure":
                tenure = float(value)
                if not (5 <= tenure <= 30):
                    return False, "Loan tenure should be between 5 and 30 years. How many years would you like to repay the loan?"
                    
            elif field_name == "Income":
                amount = float(value)
                if amount <= 0:
                    return False, "Could you please tell me your monthly income? This helps me calculate your loan eligibility."
                    
            elif field_name == "Property_value":
                amount = float(value)
                if amount <= 0:
                    return False, "What's the total value of the property you're planning to purchase? This is important for calculating your loan amount."
                    
            elif field_name == "Loan_amount_requested":
                amount = float(value)
                if amount <= 0:
                    return False, "How much loan amount are you looking for? Please share your expected loan requirement."
                    
            elif field_name == "Down_payment":
                amount = float(value)
                if amount < 0:
                    return False, "How much can you pay as down payment? Even if it's zero, please let me know."
                    
            elif field_name == "Customer_Phone":
                # Remove any spaces, dashes, or other characters
                phone_clean = str(value).replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+91", "")
                if not phone_clean.isdigit() or len(phone_clean) != 10:
                    return False, "Invalid phone number! Please provide exactly 10 digits (e.g., 9876543210). Your phone number should not contain any letters or special characters."
                    
            return True, ""
            
        except (ValueError, TypeError):
            field_display = field_name.replace('_', ' ').lower()
            return False, f"I didn't quite understand the {field_display}. Could you please provide it in a clear format?"
    
    def validate_complete_data(self, user_input: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate complete data including cross-field validations"""
        try:
            # Check if loan amount is greater than property value
            if 'Loan_amount_requested' in user_input and 'Property_value' in user_input:
                loan_amount = float(user_input['Loan_amount_requested'])
                property_value = float(user_input['Property_value'])
                
                if loan_amount > property_value:
                    return False, f"The loan amount requested (₹{loan_amount:,.0f}) cannot be more than the property value (₹{property_value:,.0f}). Please adjust your loan amount or property value."
            
            return True, ""
            
        except (ValueError, TypeError) as e:
            return False, "There was an error validating your information. Please check all the values you provided."
    
    def prepare_model_input(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        """Prepare input data for the XGBoost model with feature engineering"""
        try:
            # Validate complete data first
            is_valid, error_msg = self.validate_complete_data(user_input)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Create input dataframe
            input_data = {
                'Age': float(user_input['Age']),
                'Income': float(user_input['Income']),
                'Guarantor_income': float(user_input.get('Guarantor_income', 0)),
                'Tenure': float(user_input['Tenure']),
                'CIBIL_score': float(user_input['CIBIL_score']),
                'Down_payment': float(user_input['Down_payment']),
                'Existing_total_EMI': float(user_input.get('Existing_total_EMI', 0)),
                'Loan_amount_requested': float(user_input['Loan_amount_requested']),
                'Property_value': float(user_input['Property_value']),
                'Employment_type': user_input['Employment_type']
            }
            
            print(f"Home Loan Input data prepared: {input_data}")
            
            input_df = pd.DataFrame([input_data])
            
            # Ensure Guarantor_income is numeric
            input_df['Guarantor_income'] = pd.to_numeric(input_df['Guarantor_income'], errors='coerce').fillna(0)
            
            # Feature Engineering: Calculate ratios (matching training code)
            input_df['LTV'] = input_df['Loan_amount_requested'] / input_df['Property_value']
            input_df['EMI_to_income'] = input_df['Existing_total_EMI'] / input_df['Income']
            input_df['DP_ratio'] = input_df['Down_payment'] / input_df['Property_value']
            
            print(f"After feature engineering: LTV={input_df['LTV'].iloc[0]:.3f}, EMI_to_income={input_df['EMI_to_income'].iloc[0]:.3f}")
            
            # One-hot encode Employment_type (matching training code)
            input_df = pd.get_dummies(input_df, columns=['Employment_type'], drop_first=True)
            
            print(f"Final prepared dataframe shape: {input_df.shape}")
            return input_df
            
        except Exception as e:
            print(f"Error in prepare_model_input: {e}")
            raise e
    
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict home loan amount and interest rate using XGBoost models"""
        try:
            print(f"Home Loan Prediction - Input: {user_input}")
            
            # Prepare input data with feature engineering
            input_df = self.prepare_model_input(user_input)
            print(f"Prepared input shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            # Try to use actual ML models if available
            if self.models.get("loan_amount_model") and self.models.get("interest_rate_model"):
                try:
                    print("Using ML models for prediction...")
                    # Get the training columns from the first model to align features
                    loan_model = self.models["loan_amount_model"]
                    rate_model = self.models["interest_rate_model"]
                    
                    # Ensure input has all required columns (fill missing with 0)
                    if hasattr(loan_model, 'feature_names_in_'):
                        required_cols = loan_model.feature_names_in_
                        input_df = input_df.reindex(columns=required_cols, fill_value=0)
                        print(f"Aligned to model columns: {len(required_cols)} features")
                    
                    # Make predictions
                    predicted_loan = loan_model.predict(input_df)[0]
                    predicted_rate = rate_model.predict(input_df)[0]
                    
                    print(f"ML Prediction - Loan: Rs.{predicted_loan:,.0f}, Rate: {predicted_rate:.2f}%")
                    return round(float(predicted_loan), 0), round(float(predicted_rate), 2)
                    
                except Exception as e:
                    print(f"🏠 Model prediction error: {e}")
                    raise Exception(f"ML model prediction failed: {str(e)}")
            else:
                raise Exception("ML models not loaded. Please ensure loan_amount_model.pkl and interest_rate_model.pkl are available in models/home_loan_models/")
            
        except Exception as e:
            print(f"🏠 Prediction error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Home loan prediction failed: {str(e)}")