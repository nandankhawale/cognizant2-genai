import os
import time
import uuid
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from loan_services.loan_factory import LoanServiceFactory
from customer_data.storage_manager import CustomerDataManager

# Load environment variables
load_dotenv()

# ---------- Config ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
storage_manager = CustomerDataManager()

# ---------- FastAPI app ----------
app = FastAPI(title="Multi-Loan Chatbot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- In-memory session store ----------
SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------- Schemas ----------
class StartChatRequest(BaseModel):
    loan_type: str = Field(..., description="Type of loan: education, home, or personal")

class StartChatResponse(BaseModel):
    session_id: str
    loan_type: str
    message: str
    required_fields: List[str]

class MessageRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier returned by /chat/start")
    message: str = Field(..., description="User message")

class MessageResponse(BaseModel):
    message: str
    recorded: Dict[str, Any] = {}
    missing_fields: List[str] = []
    prediction: Optional[Dict[str, Any]] = None

class LoanTypesResponse(BaseModel):
    available_types: List[str]
    descriptions: Dict[str, str]

# ---------- Helper Functions ----------
def init_session(loan_type: str) -> str:
    """Initialize a new chat session"""
    service = LoanServiceFactory.get_service(loan_type, OPENAI_API_KEY)
    
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = {
        "loan_type": loan_type,
        "conversation": [{"role": "system", "content": service.get_system_prompt()}],
        "user_profile": {},
        "created_at": time.time(),
    }
    return session_id

def _to_float(v):
    """Convert various string formats to float"""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").strip().lower()
    # Handle Indian number formats
    if s.endswith("l"):
        return float(s[:-1]) * 100000
    if s.endswith("lac") or s.endswith("lakh"):
        import re
        num = re.sub(r"[^\d.]", "", s)
        return float(num) * 100000
    if s.endswith("cr") or s.endswith("crore"):
        import re
        num = re.sub(r"[^\d.]", "", s)
        return float(num) * 10000000
    # Normal float conversion
    import re
    return float(re.sub(r"[^\d.]", "", s) or 0)

# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/loan-types", response_model=LoanTypesResponse)
def get_loan_types():
    """Get available loan types and their descriptions"""
    descriptions = {
        "education": "Loans for higher education, courses, and academic expenses",
        "home": "Loans for purchasing, constructing, or renovating residential properties", 
        "personal": "Unsecured loans for personal expenses like medical, travel, wedding, etc."
    }
    
    return LoanTypesResponse(
        available_types=LoanServiceFactory.get_available_loan_types(),
        descriptions=descriptions
    )

@app.post("/chat/start", response_model=StartChatResponse)
def chat_start(request: StartChatRequest):
    """Start a new chat session for a specific loan type"""
    loan_type = request.loan_type.lower()
    
    if loan_type not in LoanServiceFactory.get_available_loan_types():
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid loan type. Available types: {LoanServiceFactory.get_available_loan_types()}"
        )
    
    try:
        service = LoanServiceFactory.get_service(loan_type, OPENAI_API_KEY)
        session_id = init_session(loan_type)
        
        conv = SESSIONS[session_id]["conversation"]
        greeting = service.assistant_greeting(conv)
        conv.append({"role": "assistant", "content": greeting})
        
        return StartChatResponse(
            session_id=session_id,
            loan_type=loan_type,
            message=greeting,
            required_fields=service.get_required_fields()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting chat: {str(e)}")

@app.post("/chat/message", response_model=MessageResponse)
def chat_message(req: MessageRequest):
    """Send a message in an existing chat session"""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session_id.")

    state = SESSIONS[req.session_id]
    loan_type = state["loan_type"]
    conversation = state["conversation"]
    user_profile = state["user_profile"]
    
    try:
        service = LoanServiceFactory.get_service(loan_type, OPENAI_API_KEY)
        required_fields = service.get_required_fields()
        
        # Append user message
        conversation.append({"role": "user", "content": req.message})

        # Extract fields from user response
        extracted = service.extract_info_from_response(req.message, conversation)
        recorded_now = {}
        validation_errors = []
        
        for k, v in extracted.items():
            if k in required_fields and v is not None:
                # Validate the field if the service has validation method
                if hasattr(service, 'validate_field'):
                    is_valid, error_msg = service.validate_field(k, v)
                    if not is_valid:
                        validation_errors.append(error_msg)
                        continue
                
                # Handle academic score conversion for education loans
                if k == "Academic_Score" and hasattr(service, 'convert_academic_score_to_performance'):
                    # Store both score and performance
                    user_profile[k] = v
                    user_profile["Academic_Performance"] = service.convert_academic_score_to_performance(float(v))
                    recorded_now[k] = v
                else:
                    user_profile[k] = v
                    recorded_now[k] = v
        
        # Check business logic validation for business loans
        if loan_type == "business" and hasattr(service, 'validate_business_logic'):
            is_valid, error_msg = service.validate_business_logic(user_profile)
            if not is_valid:
                validation_errors.append(error_msg)
        
        # If there are validation errors, return them immediately
        if validation_errors:
            error_message = "\n".join(validation_errors)
            conversation.append({"role": "assistant", "content": error_message})
            return MessageResponse(
                message=error_message,
                recorded={},
                missing_fields=[f for f in required_fields if f not in user_profile]
            )

        # Check completeness - for education loans, Academic_Performance is derived from Academic_Score
        missing_fields = []
        for f in required_fields:
            if f not in user_profile:
                # For education loans, if we have Academic_Score, we don't need Academic_Performance separately
                if f == "Academic_Performance" and "Academic_Score" in user_profile and loan_type == "education":
                    continue
                missing_fields.append(f)

        print(f"DEBUG - Required fields: {required_fields}")
        print(f"DEBUG - User profile keys: {list(user_profile.keys())}")
        print(f"DEBUG - Missing fields: {missing_fields}")

        # If complete -> run prediction and present result
        if not missing_fields:
            print("All fields collected, processing prediction...")
            # Don't add INFORMATION_COMPLETE to conversation - process prediction instead

            try:
                # Convert string values to appropriate numeric types
                typed = user_profile.copy()
                
                # Get numeric fields based on loan type
                numeric_fields = []
                if loan_type == "education":
                    numeric_fields = ["Age", "Academic_Score", "Coapplicant_Income", "Guarantor_Networth", 
                                    "CIBIL_Score", "Loan_Term", "Expected_Loan_Amount"]
                elif loan_type == "home":
                    numeric_fields = ["Age", "Income", "Guarantor_income", "Tenure", 
                                    "CIBIL_score", "Down_payment", "Existing_total_EMI", 
                                    "Loan_amount_requested", "Property_value"]
                elif loan_type == "personal":
                    numeric_fields = ["Age", "Employment_Duration_Years", "Annual_Income", 
                                    "CIBIL_Score", "Existing_EMIs", "Loan_Term_Years", "Expected_Loan_Amount"]
                elif loan_type == "business":
                    numeric_fields = ["Business_Age_Years", "Annual_Revenue", "Net_Profit", "CIBIL_Score",
                                    "Existing_Loan_Amount", "Loan_Tenure_Years", "Expected_Loan_Amount"]
                
                for field in numeric_fields:
                    if field in typed:
                        typed[field] = _to_float(typed[field])

                # Create prediction input without customer fields
                prediction_input = {k: v for k, v in typed.items() 
                                  if not k.startswith("Customer_")}
                
                print(f"DEBUG - Prediction input for {loan_type}: {prediction_input}")
                
                # Make prediction
                predicted_loan, predicted_interest = service.predict_loan(prediction_input)

                # Get requested amount for summary based on loan type
                if loan_type == "education":
                    summary_requested_amount = int(typed["Expected_Loan_Amount"])
                elif loan_type == "home":
                    summary_requested_amount = int(typed["Loan_amount_requested"])
                elif loan_type == "personal":
                    summary_requested_amount = int(typed["Expected_Loan_Amount"])
                elif loan_type == "business":
                    summary_requested_amount = int(typed["Expected_Loan_Amount"])
                else:
                    summary_requested_amount = int(typed.get("Expected_Loan_Amount", typed.get("Loan_amount_requested", 500000)))

                # Build summary
                summary = {
                    "loan_type": loan_type,
                    "profile": {k: (int(v) if isinstance(v, float) and k in numeric_fields else v) 
                              for k, v in typed.items()},
                    "result": {
                        "eligible_amount": int(predicted_loan),
                        "interest_rate": float(predicted_interest),
                        "requested_amount": summary_requested_amount,
                        "status": "APPROVED" if predicted_loan >= summary_requested_amount else "PARTIAL_APPROVAL"
                    }
                }

                # Extract customer info from collected data
                customer_info = {
                    "name": typed.get("Customer_Name", "Unknown"),
                    "email": typed.get("Customer_Email", ""),
                    "phone": typed.get("Customer_Phone", "")
                }
                
                # Remove customer info from loan data for prediction
                loan_data_for_prediction = {k: v for k, v in typed.items() 
                                          if not k.startswith("Customer_")}
                
                # Save customer application data
                try:
                    file_path = storage_manager.save_customer_application(
                        loan_type=loan_type,
                        session_id=req.session_id,
                        customer_info=customer_info,
                        loan_data=loan_data_for_prediction,
                        prediction_result=summary
                    )
                    print(f"Customer application saved: {file_path}")
                except Exception as e:
                    print(f"WARNING: Failed to save customer data: {e}")

                # Reset for new prediction but keep conversation
                SESSIONS[req.session_id]["user_profile"] = {}

                # Generate marketing-friendly response message
                customer_name = customer_info.get("name", "")
                loan_type_title = loan_type.title()
                
                # Get requested amount based on loan type
                if loan_type == "education":
                    requested_amount = int(typed['Expected_Loan_Amount'])
                elif loan_type == "home":
                    requested_amount = int(typed['Loan_amount_requested'])
                elif loan_type == "personal":
                    requested_amount = int(typed['Expected_Loan_Amount'])
                else:
                    requested_amount = int(typed.get('Expected_Loan_Amount', typed.get('Loan_amount_requested', predicted_loan)))
                
                if predicted_loan >= requested_amount:
                    # Full approval - customer gets what they asked for
                    assistant_msg = (
                        f"🎉 Fantastic news {customer_name}! You're PRE-APPROVED for your {loan_type_title} Loan!\n\n"
                        f"✅ YES! You are eligible for ₹{requested_amount:,} at {predicted_interest}% per annum\n\n"
                        f"🚀 What happens next:\n"
                        f"• Your loan is pre-approved and ready for processing\n"
                        f"• Competitive interest rate of {predicted_interest}% per annum\n"
                        f"• Fast-track processing with minimal documentation\n"
                        f"• Our relationship manager will contact you within 24 hours\n\n"
                        f"📞 We'll reach out to you at {customer_info.get('email', '')} or {customer_info.get('phone', '')} soon!"
                    )
                else:
                    # Partial approval - focus on what they can get
                    assistant_msg = (
                        f"💡 Great news {customer_name}! You're ELIGIBLE for a {loan_type_title} Loan!\n\n"
                        f"✅ You can get up to ₹{predicted_loan:,.0f} at {predicted_interest}% per annum\n\n"
                        f"🎯 Your loan offer:\n"
                        f"• Approved Amount: ₹{predicted_loan:,.0f}\n"
                        f"• Interest Rate: {predicted_interest}% per annum\n"
                        f"• Pre-approved offer valid for 30 days\n"
                        f"• Flexible repayment options available\n\n"
                        f"💬 Want to discuss maximizing your loan amount? Our specialist will call you!\n\n"
                        f"📞 We'll contact you at {customer_info.get('email', '')} or {customer_info.get('phone', '')} within 24 hours."
                    )
                
                conversation.append({"role": "assistant", "content": assistant_msg})

                return MessageResponse(
                    message=assistant_msg,
                    recorded={},  # Don't show recorded fields to user
                    missing_fields=[],
                    prediction=summary
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

        # Otherwise, ask for missing information
        if missing_fields:
            followup = service.assistant_followup(conversation, user_profile, missing_fields)
            conversation.append({"role": "assistant", "content": followup})

            return MessageResponse(
                message=followup,
                recorded={},  # Don't show recorded fields to user
                missing_fields=missing_fields
            )
        else:
            # This should not happen as we handle complete cases above
            print("WARNING: No missing fields but prediction not processed")
            return MessageResponse(
                message="I have all the information. Let me process your loan application...",
                recorded={},
                missing_fields=[]
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/session/{session_id}")
def get_session_info(session_id: str):
    """Get information about a chat session"""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = SESSIONS[session_id]
    service = LoanServiceFactory.get_service(state["loan_type"], OPENAI_API_KEY)
    
    return {
        "session_id": session_id,
        "loan_type": state["loan_type"],
        "required_fields": service.get_required_fields(),
        "collected_fields": list(state["user_profile"].keys()),
        "missing_fields": [f for f in service.get_required_fields() if f not in state["user_profile"]],
        "created_at": state["created_at"]
    }

@app.get("/admin/stats/{loan_type}")
def get_loan_stats(loan_type: str):
    """Get statistics for a specific loan type (admin endpoint)"""
    if loan_type not in LoanServiceFactory.get_available_loan_types():
        raise HTTPException(status_code=400, detail="Invalid loan type")
    
    try:
        stats = storage_manager.get_application_stats(loan_type)
        return {
            "loan_type": loan_type,
            "statistics": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/admin/applications/{loan_type}")
def get_recent_applications(loan_type: str, limit: int = 10):
    """Get recent applications for a loan type (admin endpoint)"""
    if loan_type not in LoanServiceFactory.get_available_loan_types():
        raise HTTPException(status_code=400, detail="Invalid loan type")
    
    try:
        applications = storage_manager.get_customer_applications(loan_type, limit)
        # Remove sensitive customer info for API response
        sanitized_apps = []
        for app in applications:
            sanitized = app.copy()
            if "customer_info" in sanitized:
                # Keep only initials and partial contact info
                customer = sanitized["customer_info"]
                sanitized["customer_info"] = {
                    "name_initial": customer.get("name", "")[:2] + "***",
                    "email_domain": customer.get("email", "").split("@")[-1] if "@" in customer.get("email", "") else "***",
                    "phone_partial": "***" + customer.get("phone", "")[-4:] if len(customer.get("phone", "")) > 4 else "***"
                }
            sanitized_apps.append(sanitized)
        
        return {
            "loan_type": loan_type,
            "applications": sanitized_apps,
            "count": len(sanitized_apps)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applications: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("loan_app:app", host="0.0.0.0", port=8001, reload=True)