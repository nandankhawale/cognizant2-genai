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
            "Annual_Income",
            "CIBIL_Score",
            "Occupation",
            "Gold_Value",
            "Loan_Amount",
            "Loan_Tenure",
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
- Annual_Income (yearly income in INR)
- CIBIL_Score (credit score, 300-900, minimum 600 for gold loans)
- Occupation: exactly one of ["Salaried", "Retired", "Business", "Self-employed"]
- Gold_Value (current market value of your gold in INR - we'll assess the actual value during verification)
- Loan_Amount (desired loan amount in INR)
- Loan_Tenure (repayment period in years, typically 1-3 for gold loans)

Guidelines:
1) Be conversational and friendly, like a helpful gold loan specialist.
2) Ask 1-2 related questions at a time to avoid overwhelming the customer.
3) For Gold_Value, ask for the approximate current market value of their gold in INR.
4) Do NOT ask for gold weight, purity, or rate per gram - only ask for the total gold value.
5) If user provides partial info, acknowledge it positively and ask for missing details.
6) Validate responses and ask for clarification if unclear.
7) For Occupation, provide the exact options: Salaried, Retired, Business, Self-employed.
8) When you have ALL information, say exactly: INFORMATION_COMPLETE
9) Do NOT provide loan predictions - only collect information professionally.

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
- Annual_Income: number in INR (yearly income, must be positive)
- CIBIL_Score: number (300-900, minimum 600 for gold loans)
- Occupation: exactly one of ["Salaried", "Retired", "Business", "Self-employed"]
- Gold_Value: number (current market value of gold in INR)
- Loan_Amount: number (desired loan amount in INR)
- Loan_Tenure: number (years, typically 1-3 for gold loans)

Important:
- For Occupation, map variations like "salaried employee", "business owner", "retired person" to exact options
- Convert lakhs/crores to actual numbers (e.g., "5 lakhs income" = 500000)
- Extract only information that is clearly stated
- Do NOT extract Gold_Weight, Gold_Purity, or Gold_Rate_Per_Gram - only Gold_Value

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Age": 45, "Annual_Income": 900000, "Occupation": "Salaried", "Gold_Value": 400000, "Loan_Amount": 300000, "Loan_Tenure": 2}}
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
                    
            elif field_name == "Annual_Income":
                income = float(value)
                if income <= 0:
                    return False, "Annual income must be a positive amount. Please provide your yearly income."
                elif income < 180000:  # Minimum 1.8 lakhs per year
                    return False, "INELIGIBLE: Minimum annual income of ₹1,80,000 is required for gold loan eligibility."
                elif income > 60000000:  # Maximum 6 crores per year (reasonable upper limit)
                    return False, "Please verify your annual income. The amount seems unusually high. Could you confirm?"
                    
            elif field_name == "Gold_Value":
                value_amount = float(value)
                if value_amount <= 0:
                    return False, "Gold value must be a positive amount. Please provide the current market value of your gold in INR."
                elif value_amount < 10000:  # Minimum 10k gold value
                    return False, "INELIGIBLE: Minimum gold value of ₹10,000 is required for gold loan eligibility."
                elif value_amount > 50000000:  # Maximum 5 crores (reasonable upper limit)
                    return False, "Please verify your gold value. The amount seems unusually high. Could you confirm the current market value?"
                    
            elif field_name == "Loan_Amount":
                amount = float(value)
                if amount <= 0:
                    return False, "Loan amount must be a positive amount. Please provide your desired loan amount in INR."
                elif amount < 5000:  # Minimum 5k loan
                    return False, "INELIGIBLE: Minimum loan amount of ₹5,000 is required."
                elif amount > 10000000:  # Maximum 1 crore
                    return False, "Please verify your loan amount. The amount seems unusually high for a gold loan."
                    
            elif field_name == "Loan_Tenure":
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
            # Convert Annual Income to Monthly Income
            monthly_income = float(user_input['Annual_Income']) / 12
            
            # Create input dataframe matching your model's expected features
            # Model expects: ['Age', 'Occupation', 'Monthly_Income', 'CIBIL_Score', 'Gold_Value', 'Existing_EMI', 'Loan_Tenure_Years']
            input_data = {
                'Age': float(user_input['Age']),
                'Occupation': user_input['Occupation'],  # Will be encoded later
                'Monthly_Income': monthly_income,
                'CIBIL_Score': float(user_input['CIBIL_Score']),
                'Gold_Value': float(user_input['Gold_Value']),
                'Existing_EMI': 0.0,  # Default to 0 since we don't collect this anymore
                'Loan_Tenure_Years': float(user_input['Loan_Tenure'])
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