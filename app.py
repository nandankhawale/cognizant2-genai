# app.py
import os
import re
import json
import time
import uuid
import joblib
import pandas as pd
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------- Config ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # set this in your env
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. OpenAI features will be disabled.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

MODEL_PATH = "models/education _loan_models"
MODEL_FILES = {
    "xgb_loan": os.path.join(MODEL_PATH, "xgb_loan_amount_v2.pkl"),
    "xgb_interest": os.path.join(MODEL_PATH, "xgb_interest_rate_v2.pkl"),
    "encoders": os.path.join(MODEL_PATH, "encoders_v2.pkl"),
    "scaler": os.path.join(MODEL_PATH, "scaler_v2.pkl"),
}

# ---------- Load models at startup ----------
try:
    xgb_loan = joblib.load(MODEL_FILES["xgb_loan"])
    xgb_interest = joblib.load(MODEL_FILES["xgb_interest"])
    encoders: Dict[str, Any] = joblib.load(MODEL_FILES["encoders"])
    scaler = joblib.load(MODEL_FILES["scaler"])
    print("All model files loaded successfully")
except Exception as e:
    print(f"Warning: Failed to load model artifacts: {e}")
    print("Model prediction features will be disabled until model files are available")
    xgb_loan = xgb_interest = encoders = scaler = None

# ---------- FastAPI app ----------
app = FastAPI(title="Education Loan Chatbot API", version="1.0.0")

# Allow browser file:// or any origin while you test locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- In-memory session store ----------
SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------- Domain logic ----------
REQUIRED_FIELDS = [
    "Age",
    "Academic_Performance",
    "Intended_Course",
    "University_Tier",
    "Coapplicant_Income",
    "Guarantor_Networth",
    "CIBIL_Score",
    "Loan_Type",
    "Loan_Term",
    "Expected_Loan_Amount",
]

SYSTEM_PROMPT = """You are a friendly and professional education loan advisor chatbot.

Your task is to systematically collect the following information from users through natural conversation:

Required Fields:
- Age (18-100)
- Academic_Performance: one of ["Excellent","Good","Average","Poor"]
- Intended_Course: one of ["STEM","MBA","Medicine","Finance","Law","Arts","Other"]
- University_Tier: one of ["Tier1","Tier2","Tier3"]
- Coapplicant_Income (annual income in INR)
- Guarantor_Networth (total assets value in INR)
- CIBIL_Score (300-900)
- Loan_Type: one of ["Secured","Unsecured"]
- Loan_Term (repayment period in years)
- Expected_Loan_Amount (desired loan amount in INR)

Guidelines:
1) Be conversational and friendly, not robotic.
2) Ask 1-2 related questions at a time, don't overwhelm.
3) Provide brief explanations when needed (e.g., what is CIBIL score).
4) If user provides partial info, acknowledge it and ask for missing details.
5) Validate responses and ask for clarification if unclear.
6) When you have ALL information, say exactly: INFORMATION_COMPLETE
7) Do NOT provide loan advice or predictions - only collect information.

Start by introducing yourself and asking about their educational plans.
"""

def repayment_capacity(income: float, networth: float, cibil: float) -> float:
    return (income * 4) + (networth * 0.05) + (cibil / 2)

def predict_loan(user_input: Dict[str, Any]):
    # computed feature
    user_input["Repayment_Capacity"] = repayment_capacity(
        user_input["Coapplicant_Income"],
        user_input["Guarantor_Networth"],
        user_input["CIBIL_Score"]
    )

    # encode categoricals
    for col in ["Academic_Performance", "Intended_Course", "University_Tier", "Loan_Type"]:
        if col not in encoders:
            raise ValueError(f"Encoder for {col} not found.")
        user_input[col] = encoders[col].transform([user_input[col]])[0]

    # features & scaling
    features = [
        "Age", "Academic_Performance", "Intended_Course", "University_Tier",
        "Coapplicant_Income", "Guarantor_Networth", "CIBIL_Score",
        "Loan_Type", "Repayment_Capacity", "Loan_Term"
    ]

    X = pd.DataFrame([{k: user_input[k] for k in features}])
    numeric_cols = ["Age", "Coapplicant_Income", "Guarantor_Networth", "CIBIL_Score", "Repayment_Capacity", "Loan_Term"]
    X[numeric_cols] = scaler.transform(X[numeric_cols])

    loan_amt = xgb_loan.predict(X)[0]
    interest = xgb_interest.predict(X)[0]
    return round(float(loan_amt)), round(float(interest), 2)

def extract_info_from_response(user_text: str, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
    if not client:
        return {}  # Return empty dict if OpenAI client not available
        
    extraction_prompt = f"""
Based on the conversation history and the user's latest response, extract any loan-related information.

Conversation so far: {conversation[-3:] if len(conversation) > 3 else conversation}

User's latest response: "{user_text}"

Extract information for these fields (only if mentioned):
- Age: number (18-100)
- Academic_Performance: exactly one of ["Excellent","Good","Average","Poor"]
- Intended_Course: exactly one of ["STEM","MBA","Medicine","Finance","Law","Arts","Other"]
- University_Tier: exactly one of ["Tier1","Tier2","Tier3"]
- Coapplicant_Income: number in INR (annual income)
- Guarantor_Networth: number in INR
- CIBIL_Score: number (300-900)
- Loan_Type: exactly one of ["Secured","Unsecured"]
- Loan_Term: number (years, typically 1-20)
- Expected_Loan_Amount: number in INR

Return ONLY a JSON object with the extracted fields. If no information is found, return empty JSON {{}}.
Example: {{"Age": 25, "Academic_Performance": "Good", "Coapplicant_Income": 500000}}
""".strip()

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0
        )
        extracted_text = resp.choices[0].message.content.strip()
        m = re.search(r"\{.*\}", extracted_text, re.DOTALL)
        if m:
            return json.loads(m.group())
        return {}
    except Exception:
        return {}

# ---------- Schemas ----------
class StartChatResponse(BaseModel):
    session_id: str
    message: str

class MessageRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier returned by /chat/start")
    message: str = Field(..., description="User message")

class MessageResponse(BaseModel):
    message: str
    recorded: Dict[str, Any] = {}
    missing_fields: List[str] = []
    prediction: Optional[Dict[str, Any]] = None

# ---------- Helpers ----------
def init_session() -> str:
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = {
        "conversation": [{"role": "system", "content": SYSTEM_PROMPT}],
        "user_profile": {},
        "created_at": time.time(),
    }
    return session_id

def assistant_greeting(conversation: List[Dict[str, str]]) -> str:
    if not client:
        return "Hello! I'm here to help you with your education loan prediction. What course are you planning to pursue?"
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception:
        return "Hello! I'm here to help you with your education loan prediction. What course are you planning to pursue?"

def assistant_followup(conversation: List[Dict[str, str]], user_profile: Dict[str, Any], missing_fields: List[str]) -> str:
    if not client:
        # fallback single-question when OpenAI not available
        return f"I'd like to know more about your {missing_fields[0].replace('_',' ').lower()}. Could you please provide that information?"
        
    context_info = f"""
    Current user profile: {user_profile}
    Missing fields: {missing_fields}

    Continue the conversation naturally to collect the missing information.
    If you have all required fields, respond with "INFORMATION_COMPLETE".
    """
    conversation.append({"role": "system", "content": context_info})
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception:
        # fallback single-question
        return f"I'd like to know more about your {missing_fields[0].replace('_',' ').lower()}. Could you please provide that information?"

# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat/start", response_model=StartChatResponse)
def chat_start():
    session_id = init_session()
    conv = SESSIONS[session_id]["conversation"]
    greeting = assistant_greeting(conv)
    conv.append({"role": "assistant", "content": greeting})
    return StartChatResponse(session_id=session_id, message=greeting)

@app.post("/chat/message", response_model=MessageResponse)
def chat_message(req: MessageRequest):
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session_id.")

    state = SESSIONS[req.session_id]
    conversation = state["conversation"]
    user_profile = state["user_profile"]

    # Append user message
    conversation.append({"role": "user", "content": req.message})

    # Extract fields
    extracted = extract_info_from_response(req.message, conversation)
    recorded_now = {}
    for k, v in extracted.items():
        if k in REQUIRED_FIELDS and v is not None:
            user_profile[k] = v
            recorded_now[k] = v

    # Check completeness
    missing_fields = [f for f in REQUIRED_FIELDS if f not in user_profile]

    # If complete -> run prediction and present result
    if not missing_fields:
        # Mark info complete so assistant can close out gracefully (optional)
        conversation.append({"role": "assistant", "content": "INFORMATION_COMPLETE"})

        try:
            if not all([xgb_loan, xgb_interest, encoders, scaler]):
                raise HTTPException(status_code=503, detail="ML models not available. Please ensure model files are loaded.")
                
            # Build a copy with numeric conversions where needed
            typed = user_profile.copy()

            # Coerce common numeric strings (e.g., "5L", "500,000") if user gave them
            def _to_float(v):
                if isinstance(v, (int, float)):
                    return float(v)
                s = str(v).replace(",", "").strip().lower()
                # crude "L" -> lakh
                if s.endswith("l"):
                    return float(s[:-1]) * 100000
                if s.endswith("lac") or s.endswith("lakh"):
                    num = re.sub(r"[^\d.]", "", s)
                    return float(num) * 100000
                # normal float
                return float(re.sub(r"[^\d.]", "", s) or 0)

            for num_field in [
                "Age", "Coapplicant_Income", "Guarantor_Networth",
                "CIBIL_Score", "Loan_Term", "Expected_Loan_Amount"
            ]:
                typed[num_field] = _to_float(typed[num_field])

            predicted_loan, predicted_interest = predict_loan(typed)

            # Build a friendly summary block
            summary = {
                "profile": {
                    "Age": int(typed["Age"]),
                    "Academic_Performance": user_profile["Academic_Performance"],
                    "Intended_Course": user_profile["Intended_Course"],
                    "University_Tier": user_profile["University_Tier"],
                    "Coapplicant_Income": int(typed["Coapplicant_Income"]),
                    "Guarantor_Networth": int(typed["Guarantor_Networth"]),
                    "CIBIL_Score": int(typed["CIBIL_Score"]),
                    "Loan_Type": user_profile["Loan_Type"],
                    "Loan_Term_years": int(typed["Loan_Term"]),
                    "Expected_Amount": int(typed["Expected_Loan_Amount"]),
                },
                "result": {
                    "eligible_amount": int(predicted_loan),
                    "interest_rate": float(predicted_interest),
                    "status": "APPROVED" if predicted_loan >= typed["Expected_Loan_Amount"] else "PARTIAL_APPROVAL"
                }
            }

            # Reset for a new run but keep conversation
            SESSIONS[req.session_id]["user_profile"] = {}

            # Assistant closing message (optional UX)
            assistant_msg = (
                f"Thanks! I have everything I need.\n\n"
                f"PREDICTION RESULTS\n"
                f"- Eligible Amount: ₹{predicted_loan:,.0f}\n"
                f"- Interest (annual): {predicted_interest}%\n"
                f"- Your requested amount: ₹{int(typed['Expected_Loan_Amount']):,}\n"
                f"{'🎉 APPROVED!' if predicted_loan >= typed['Expected_Loan_Amount'] else '⚠️ PARTIAL APPROVAL.'}"
            )
            conversation.append({"role": "assistant", "content": assistant_msg})

            return MessageResponse(
                message=assistant_msg,
                recorded=recorded_now,
                missing_fields=[],
                prediction=summary
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    # Otherwise, ask for the next missing fields
    followup = assistant_followup(conversation, user_profile, missing_fields)
    conversation.append({"role": "assistant", "content": followup})

    return MessageResponse(
        message=followup,
        recorded=recorded_now,
        missing_fields=missing_fields or []
    )

# Run: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
