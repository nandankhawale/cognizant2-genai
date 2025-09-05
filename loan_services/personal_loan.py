from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
import joblib
from .base_loan import BaseLoanService

class PersonalLoanService(BaseLoanService):
    """Personal Loan Service with ML Model Integration"""
    
    def get_required_fields(self) -> List[str]:
        return [
            # Customer Contact Information
            "Customer_Name",
            "Customer_Email", 
            "Customer_Phone",
            # Model Prediction Fields
            "Age",
            "Employment_Type",
            "Employment_Duration_Years",
            "Annual_Income",
            "CIBIL_Score",
            "Existing_EMIs",
            "Loan_Term_Years",
            "Expected_Loan_Amount",  # Added for frontend compatibility
        ]
    
    def get_model_files(self) -> Dict[str, str]:
        return {
            "personal_loan_model": "personal_loan_model.pkl",
        }
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and professional personal loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Customer Information:
- Customer_Name (full name)
- Customer_Email (email address)
- Customer_Phone (10-digit phone number)

Required Loan Information:
- Age (21-65 years)
- Employment_Type: exactly one of ["Self-Employed", "Salaried"]
- Employment_Duration_Years (how many years working in current employment type)
- Annual_Income (yearly income in INR)
- CIBIL_Score (credit score, 300-900, minimum 650 recommended)
- Existing_EMIs (current monthly EMI obligations in INR, can be 0)
- Loan_Term_Years (repayment period in years, typically 1-7)
- Expected_Loan_Amount (desired loan amount in INR)

Guidelines:
1) Be conversational and friendly, like a helpful loan specialist.
2) Ask 1-2 related questions at a time to avoid overwhelming the customer.
3) Provide brief explanations when needed (e.g., "CIBIL score is your credit score").
4) If user provides partial info, acknowledge it positively and ask for missing details.
5) Validate responses and ask for clarification if unclear.
6) For categorical fields, ensure exact match with the specified options.
7) When you have ALL information, say exactly: INFORMATION_COMPLETE
8) Do NOT provide loan predictions - only collect information professionally.

Start by introducing yourself as a personal loan specialist."""
    
    def get_fallback_greeting(self) -> str:
        return "Hello! I'm a personal loan specialist here to help you with your loan application. Let's start with your full name - what should I call you?"
    
    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        return f"""
Based on the conversation history and the user's latest response, extract any personal loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if clearly mentioned):

Customer Information:
- Customer_Name: full name as string
- Customer_Email: email address as string  
- Customer_Phone: 10-digit phone number as string (remove +91, spaces, dashes)

Loan Information:
- Age: number (21-65)
- Employment_Type: exactly one of ["Self-Employed", "Salaried"]
- Employment_Duration_Years: number (years in current employment type)
- Annual_Income: number in INR (yearly income, must be positive)
- CIBIL_Score: number (300-900, minimum 650 recommended)
- Existing_EMIs: number in INR (current monthly EMI obligations, 0 if none)
- Loan_Term_Years: number (years, typically 1-7)
- Expected_Loan_Amount: number in INR (desired loan amount)

Important:
- For Employment_Type, map variations like "self employed", "salaried employee" to exact options
- Convert lakhs/crores to actual numbers (e.g., "12 lakhs annual" = 1200000)
- For Employment_Duration_Years, ask about years in current employment type, not total experience
- Extract only information that is clearly stated

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Customer_Name": "John Doe", "Age": 35, "Employment_Type": "Salaried", "Annual_Income": 1200000, "Employment_Duration_Years": 12}}
""".strip()
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """Validate individual field values with strict eligibility criteria"""
        try:
            if field_name == "Age":
                age = float(value)
                if age < 21:
                    return False, "INELIGIBLE: You must be at least 21 years old to apply for a personal loan. Unfortunately, we cannot process your application at this time."
                elif age > 65:
                    return False, "INELIGIBLE: Personal loans are available only for applicants up to 65 years of age. Unfortunately, we cannot process your application at this time."
                    
            elif field_name == "CIBIL_Score":
                cibil = float(value)
                if cibil < 650:
                    return False, "INELIGIBLE: A minimum CIBIL score of 650 is required for personal loan approval. Your current score does not meet our eligibility criteria."
                elif not (300 <= cibil <= 900):
                    return False, "Please provide a valid CIBIL score between 300 and 900. Could you check and confirm your credit score?"
                    
            elif field_name == "Employment_Duration_Years":
                duration = float(value)
                if duration < 0:
                    return False, "INELIGIBLE: Employment duration cannot be negative. Please provide valid employment experience."
                elif duration < 1:
                    return False, "INELIGIBLE: You must have at least 1 year of employment experience to qualify for a personal loan."
                elif duration > 45:
                    return False, "Employment duration seems unusually high. Could you please confirm how many years you've been in your current employment type?"
                    
            elif field_name == "Annual_Income":
                income = float(value)
                if income <= 0:
                    return False, "Annual income must be a positive amount. Please provide your yearly income."
                elif income < 200000:  # Minimum 2 lakhs per year
                    return False, "INELIGIBLE: Minimum annual income of ₹2,00,000 is required for personal loan eligibility."
                elif income > 50000000:  # Maximum 5 crores (reasonable upper limit)
                    return False, "Please verify your annual income. The amount seems unusually high. Could you confirm?"
                    
            elif field_name == "Employment_Type":
                valid_types = ["Self-Employed", "Salaried"]
                if value not in valid_types:
                    return False, f"Please select your employment type from: {', '.join(valid_types)}. Which category describes your employment?"
                    
            elif field_name == "Loan_Term_Years":
                term = float(value)
                if not (1 <= term <= 7):
                    return False, "Loan term must be between 1 and 7 years. Please specify your preferred repayment period."
                    
            elif field_name == "Expected_Loan_Amount":
                amount = float(value)
                if amount <= 0:
                    return False, "Loan amount must be a positive value. Please specify your loan requirement."
                elif amount < 50000:
                    return False, "Minimum loan amount is ₹50,000. Please specify an amount of at least ₹50,000."
                elif amount > 2000000:
                    return False, "Maximum loan amount is ₹20,00,000. Please specify an amount within this limit."
                    
            elif field_name == "Existing_EMIs":
                amount = float(value)
                if amount < 0:
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

    def calculate_debt_to_income_ratio(self, annual_income: float, existing_emi: float, proposed_emi: float) -> float:
        """Calculate Debt-to-Income ratio"""
        monthly_income = annual_income / 12
        total_debt = existing_emi + proposed_emi
        return (total_debt / monthly_income) * 100 if monthly_income > 0 else 0

    def prepare_model_input(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        """Prepare input data for the personal loan model based on your exact model structure"""
        try:
            # Create input dataframe matching your model's expected features
            # Based on your code: Age, Employment_Type, Employment_Duration_Years, Annual_Income, CIBIL_Score, Existing_EMIs, Loan_Term_Years
            
            input_data = {
                'Age': float(user_input['Age']),
                'Employment_Type': user_input['Employment_Type'],  # Will be encoded later
                'Employment_Duration_Years': float(user_input['Employment_Duration_Years']),
                'Annual_Income': float(user_input['Annual_Income']),
                'CIBIL_Score': float(user_input['CIBIL_Score']),
                'Existing_EMIs': float(user_input.get('Existing_EMIs', 0)),
                'Loan_Term_Years': float(user_input['Loan_Term_Years'])
            }
            
            print(f"Personal Loan Input data prepared: {input_data}")
            
            input_df = pd.DataFrame([input_data])
            
            print(f"Prepared input dataframe shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            return input_df
            
        except Exception as e:
            print(f"Error in prepare_model_input: {e}")
            raise e
    
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict personal loan amount and interest rate using ML model"""
        try:
            print(f"Personal Loan Prediction - Input: {user_input}")
            
            # Prepare input data
            input_df = self.prepare_model_input(user_input)
            print(f"Prepared input shape: {input_df.shape}")
            print(f"Input columns: {list(input_df.columns)}")
            
            # Try to use actual ML model if available
            if self.models.get("personal_loan_model"):
                try:
                    print("Using ML model for prediction...")
                    
                    # Load the model package - matching your structure exactly
                    package = self.models["personal_loan_model"]
                    model = package["model"]
                    scaler = package["scaler"]
                    le = package["encoder"]  # Label encoder for Employment_Type
                    features = package["features"]  # Feature order
                    
                    print("Model components loaded successfully")
                    print(f"Expected features: {features}")
                    
                    # Prepare data for prediction
                    df_input = input_df.copy()
                    
                    # Encode Employment_Type using your label encoder
                    df_input["Employment_Type"] = le.transform(df_input["Employment_Type"])
                    print(f"After encoding Employment_Type: {df_input['Employment_Type'].values}")
                    
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
                    # prediction[0] = log-transformed loan amount
                    # prediction[1] = interest rate
                    loan_amount = np.expm1(prediction[0])  # inverse log transformation
                    interest_rate = float(prediction[1])
                    
                    print(f"After transformation - Loan: Rs.{loan_amount:,.0f}, Rate: {interest_rate:.2f}%")
                    
                    # Ensure reasonable bounds
                    loan_amount = max(50000, min(2000000, loan_amount))  # Between 50k and 20L
                    interest_rate = max(8.0, min(18.0, interest_rate))   # Between 8% and 18%
                    
                    print(f"Final ML Prediction - Loan: Rs.{loan_amount:,.0f}, Rate: {interest_rate:.2f}%")
                    return round(float(loan_amount), 0), round(float(interest_rate), 2)
                    
                except Exception as e:
                    print(f"Model prediction error: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"ML model prediction failed: {str(e)}")
            else:
                raise Exception("Personal loan ML model not available. Cannot process loan prediction.")
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Personal loan prediction failed: {str(e)}")
    
