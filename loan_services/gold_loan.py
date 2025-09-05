from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
import joblib
from .base_loan import BaseLoanService

class GoldLoanService(BaseLoanService):
    """Gold Loan Service with ML Model Integration"""
    
    def get_required_fields(self) -> List[str]:
        return [
            # Customer Contact Information
            "Customer_Name",
            "Customer_Email", 
            "Customer_Phone",
            # Model Prediction Fields
            "Age",
            "Occupation",
            "Monthly_Income",
            "CIBIL_Score",
            "Gold_Value",
            "Existing_EMI",
            "Loan_Tenure_Years",
        ]
    
    def get_model_files(self) -> Dict[str, str]:
        return {
            "gold_loan_model": "gold_loan_model.pkl",
        }
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and professional gold loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Customer Information:
- Customer_Name (full name)
- Customer_Email (email address)
- Customer_Phone (10-digit phone number)

Required Loan Information:
- Age (21-75 years for gold loans)
- Occupation: exactly one of ["Salaried", "Retired", "Business", "Self-employed"]
- Monthly_Income (monthly income in INR)
- CIBIL_Score (credit score, 300-900, minimum 600 for gold loans)
- Gold_Value (estimated value of gold to be pledged in INR)
- Existing_EMI (current monthly EMI obligations in INR, can be 0)
- Loan_Tenure_Years (repayment period in years, typically 1-3 for gold loans)

Guidelines:
1) Be conversational and friendly, like a helpful gold loan specialist.
2) Ask 1-2 related questions at a time to avoid overwhelming the customer.
3) Provide brief explanations when needed (e.g., "Gold value is the current market value of your gold").
4) If user provides partial info, acknowledge it positively and ask for missing details.
5) Validate responses and ask for clarification if unclear.
6) For Occupation, provide the exact options: Salaried, Retired, Business, Self-employed.
7) When you have ALL information, say exactly: INFORMATION_COMPLETE
8) Do NOT provide loan predictions - only collect information professionally.

Start by introducing yourself as a gold loan specialist."""
    
    def get_fallback_greeting(self) -> str:
        return "Hello! I'm a gold loan specialist here to help you with your gold loan application. Gold loans offer quick financing against your gold jewelry. Let's start with your full name - what should I call you?"
    
    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        return f"""
Based on the conversation history and the user's latest response, extract any gold loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if clearly mentioned):

Customer Information:
- Customer_Name: full name as string
- Customer_Email: email address as string  
- Customer_Phone: 10-digit phone number as string (remove +91, spaces, dashes)

Loan Information:
- Age: number (21-75)
- Occupation: exactly one of ["Salaried", "Retired", "Business", "Self-employed"]
- Monthly_Income: number in INR (monthly income, must be positive)
- CIBIL_Score: number (300-900, minimum 600 for gold loans)
- Gold_Value: number in INR (estimated value of gold to be pledged)
- Existing_EMI: number in INR (current monthly EMI obligations, 0 if none)
- Loan_Tenure_Years: number (years, typically 1-3 for gold loans)

Important:
- For Occupation, map variations like "salaried employee", "business owner", "retired person" to exact options
- Convert lakhs/crores to actual numbers (e.g., "5 lakhs gold" = 500000)
- For gold value, this is the current market value of gold they want to pledge
- Extract only information that is clearly stated

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Age": 45, "Occupation": "Salaried", "Monthly_Income": 75000, "Gold_Value": 400000}}
""".strip()
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """Validate individual field values with strict eligibility criteria"""
        try:
            if field_name == "Age":
                age = float(value)
                if age < 21:
                    return False, "INELIGIBLE: You must be at least 21 years old to apply for a gold loan. Unfortunately, we cannot process your application at this time."
                elif age > 75:
                    return False, "INELIGIBLE: Gold loans are available only for applicants up to 75 years of age. Unfortunately, we cannot process your application at this time."
                    
            elif field_name == "CIBIL_Score":
                cibil = float(value)
                if cibil < 600:
                    return False, "INELIGIBLE: A minimum CIBIL score of 600 is required for gold loan approval. Your current score does not meet our eligibility criteria."
                elif not (300 <= cibil <= 900):
                    return False, "Please provide a valid CIBIL score between 300 and 900. Could you check and confirm your credit score?"
                    
            elif field_name == "Occupation":
                valid_occupations = ["Salaried", "Retired", "Business", "Self-employed"]
                if value not in valid_occupations:
                    return False, f"Please select your occupation from: {', '.join(valid_occupations)}. Which category best describes your occupation?"
                    
            elif field_name == "Monthly_Income":
                income = float(value)
                if income <= 0:
                    return False, "Monthly income must be a positive amount. Please provide your monthly income."
                elif income < 15000:  # Minimum 15k per month
                    return False, "INELIGIBLE: Minimum monthly income of ₹15,000 is required for gold loan eligibility."
                elif income > 5000000:  # Maximum 50 lakhs per month (reasonable upper limit)
                    return False, "Please verify your monthly income. The amount seems unusually high. Could you confirm?"
                    
            elif field_name == "Gold_Value":
                gold_value = float(value)
                if gold_value <= 0:
                    return False, "Gold value must be a positive amount. Please provide the estimated value of your gold."
                elif gold_value < 10000:
                    return False, "INELIGIBLE: Minimum gold value of ₹10,000 is required for gold loan processing."
                elif gold_value > 50000000:  # Maximum 5 crores (reasonable upper limit)
                    return False, "Please verify your gold value. The amount seems unusually high. Could you confirm the current market value of your gold?"
                    
            elif field_name == "Loan_Tenure_Years":
                tenure = float(value)
                if tenure < 1:
                    return False, "INELIGIBLE: Gold loan tenure must be at least 1 year. Please specify a tenure between 1 and 3 years."
                elif tenure > 3:
                    return False, "INELIGIBLE: Gold loan tenure cannot exceed 3 years. Please specify a tenure between 1 and 3 years."
                    
            elif field_name == "Existing_EMI":
                emi = float(value)
                if emi < 0:
                    return False, "EMI amount cannot be negative. Please provide your current monthly EMI obligations (enter 0 if none)."
                    
            elif field_name == "Customer_Phone":
                # Remove any spaces, dashes, or other characters
                phone_clean = str(value).replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+91", "")
                if not phone_clean.isdigit() or len(phone_clean) != 10:
                    return False, "Please provide a valid 10-digit phone number (e.g., 9876543210)."
                    
            return True, ""
            
        except (ValueError, TypeError):
            field_display = field_name.replace('_', ' ').lower()
            return False, f"Please provide a valid {field_display} in the correct format."

    def prepare_model_input(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        """Prepare input data for the gold loan model"""
        try:
            # Create input dataframe matching your model's expected features
            # Based on your model: Age, Occupation, Monthly_Income, CIBIL_Score, Gold_Value, Existing_EMI, Loan_Tenure_Years
            
            input_data = {
                'Age': float(user_input['Age']),
                'Occupation': user_input['Occupation'],  # Will be encoded later
                'Monthly_Income': float(user_input['Monthly_Income']),
                'CIBIL_Score': float(user_input['CIBIL_Score']),
                'Gold_Value': float(user_input['Gold_Value']),
                'Existing_EMI': float(user_input.get('Existing_EMI', 0)),
                'Loan_Tenure_Years': float(user_input['Loan_Tenure_Years'])
            }
            
            print(f"Gold Loan Input data prepared: {input_data}")
            
            input_df = pd.DataFrame([input_data])
            
            print(f"Prepared input dataframe shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            return input_df
            
        except Exception as e:
            print(f"Error in prepare_model_input: {e}")
            raise e
    
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict gold loan amount and interest rate using ML model"""
        try:
            print(f"Gold Loan Prediction - Input: {user_input}")
            
            # Prepare input data
            input_df = self.prepare_model_input(user_input)
            print(f"Prepared input shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            # Try to use actual ML model if available
            if self.models.get("gold_loan_model"):
                try:
                    print("Using ML model for prediction...")
                    
                    # Load the model package - matching your structure exactly
                    package = self.models["gold_loan_model"]
                    model = package["model"]
                    scaler = package["scaler"]
                    encoder = package["encoder"]  # Label encoder for Occupation
                    features = package["features"]  # Feature order
                    targets = package["targets"]  # Target names
                    
                    print("Model components loaded successfully")
                    print(f"Expected features: {features}")
                    print(f"Target variables: {targets}")
                    
                    # Prepare data for prediction
                    df_input = input_df.copy()
                    
                    # Encode Occupation using your label encoder
                    df_input["Occupation"] = encoder.transform(df_input["Occupation"])
                    print(f"After encoding Occupation: {df_input['Occupation'].values}")
                    
                    # Select features in the correct order
                    df_input = df_input[features]
                    print(f"After feature selection: {list(df_input.columns)}")
                    
                    # Scale features using your scaler
                    df_scaled = scaler.transform(df_input)
                    print(f"Scaled features shape: {df_scaled.shape}")
                    
                    # Make predictions
                    prediction = model.predict(df_scaled)[0]
                    print(f"Raw predictions: {prediction}")
                    
                    # Handle predictions as per your structure
                    # prediction[0] = Loan_Amount
                    # prediction[1] = Rate_of_Interest
                    loan_amount = float(prediction[0])
                    interest_rate = float(prediction[1])
                    
                    print(f"ML Prediction - Loan: Rs.{loan_amount:,.0f}, Rate: {interest_rate:.2f}%")
                    
                    # Ensure reasonable bounds for gold loans
                    # Gold loans typically offer 70-80% of gold value
                    max_loan_based_on_gold = float(user_input['Gold_Value']) * 0.8
                    loan_amount = min(loan_amount, max_loan_based_on_gold)
                    loan_amount = max(loan_amount, 5000)    # Min 5k
                    interest_rate = max(8.0, min(24.0, interest_rate))   # Between 8% and 24%
                    
                    print(f"Final ML Prediction - Loan: Rs.{loan_amount:,.0f}, Rate: {interest_rate:.2f}%")
                    return round(float(loan_amount), 0), round(float(interest_rate), 2)
                    
                except Exception as e:
                    print(f"Model prediction error: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"ML model prediction failed: {str(e)}")
            else:
                raise Exception("Gold loan ML model not available. Cannot process loan prediction.")
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Gold loan prediction failed: {str(e)}")