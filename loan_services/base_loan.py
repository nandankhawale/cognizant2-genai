from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os
import joblib
import pandas as pd
from openai import OpenAI

class BaseLoanService(ABC):
    """Base class for all loan services"""
    
    def __init__(self, model_path: str, openai_api_key: Optional[str] = None):
        self.model_path = model_path
        self.models = {}
        self.client = None
        
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        
        self.load_models()
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required fields for this loan type"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this loan type"""
        pass
    
    @abstractmethod
    def predict_loan(self, user_input: Dict[str, Any]) -> tuple:
        """Predict loan amount and interest rate"""
        pass
    
    def load_models(self):
        """Load ML models from the specified path"""
        try:
            model_files = self.get_model_files()
            for key, filename in model_files.items():
                full_path = os.path.join(self.model_path, filename)
                if os.path.exists(full_path):
                    self.models[key] = joblib.load(full_path)
                    print(f"Loaded {key} model from {full_path}")
                else:
                    print(f"Warning: Model file {full_path} not found")
                    self.models[key] = None
        except Exception as e:
            print(f"Error loading models: {e}")
    
    @abstractmethod
    def get_model_files(self) -> Dict[str, str]:
        """Return dictionary of model files needed"""
        pass
    
    def extract_info_from_response(self, user_text: str, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract information from user response using OpenAI or fallback logic"""
        # Try OpenAI first
        if self.client:
            extraction_prompt = self.get_extraction_prompt(user_text, conversation)
            
            try:
                resp = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0
                )
                extracted_text = resp.choices[0].message.content.strip()
                import re, json
                m = re.search(r"\{.*\}", extracted_text, re.DOTALL)
                if m:
                    return json.loads(m.group())
            except Exception as e:
                print(f"OpenAI extraction failed: {e}")
        
        # Fallback to simple pattern matching for basic fields
        return self._fallback_extraction(user_text, conversation)
    
    def _fallback_extraction(self, user_text: str, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fallback extraction using simple pattern matching"""
        extracted = {}
        text_lower = user_text.lower().strip()
        
        # Extract name patterns
        import re
        name_patterns = [
            r"my name is\s+([a-zA-Z\s]+)",
            r"i am\s+([a-zA-Z\s]+)",
            r"call me\s+([a-zA-Z\s]+)",
            r"i'm\s+([a-zA-Z\s]+)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip().title()
                if len(name) > 1 and not any(word in name.lower() for word in ['years', 'old', 'work', 'job', 'salary']):
                    extracted['Customer_Name'] = name
                    break
        
        # If no pattern matched but it looks like just a name (when asked for name)
        if not extracted.get('Customer_Name'):
            # Check if previous message was asking for name
            if len(conversation) > 0:
                last_assistant_msg = ""
                for msg in reversed(conversation):
                    if msg.get('role') == 'assistant':
                        last_assistant_msg = msg.get('content', '').lower()
                        break
                
                if 'name' in last_assistant_msg and len(text_lower.split()) <= 3:
                    # Simple name check - only letters and spaces, reasonable length
                    if re.match(r'^[a-zA-Z\s]+$', user_text.strip()) and 2 <= len(user_text.strip()) <= 50:
                        extracted['Customer_Name'] = user_text.strip().title()
        
        # Extract phone numbers
        phone_pattern = r'(\+?91[-\s]?)?([6-9]\d{9})'
        phone_match = re.search(phone_pattern, user_text)
        if phone_match:
            extracted['Customer_Phone'] = phone_match.group(2)
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, user_text)
        if email_match:
            extracted['Customer_Email'] = email_match.group(0)
        
        # Extract age
        age_patterns = [
            r'i am\s+(\d{1,2})\s+years?\s+old',
            r'my age is\s+(\d{1,2})',
            r'age\s*:?\s*(\d{1,2})',
            r'(\d{1,2})\s+years?\s+old'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age = int(match.group(1))
                if 18 <= age <= 80:  # Reasonable age range
                    extracted['Age'] = age
                    break
        
        return extracted
    
    @abstractmethod
    def get_extraction_prompt(self, user_text: str, conversation: List[Dict[str, str]]) -> str:
        """Get extraction prompt for this loan type"""
        pass
    
    def assistant_greeting(self, conversation: List[Dict[str, str]]) -> str:
        """Generate greeting message"""
        if not self.client:
            return self.get_fallback_greeting()
        
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                temperature=0.7
            )
            return resp.choices[0].message.content
        except Exception:
            return self.get_fallback_greeting()
    
    @abstractmethod
    def get_fallback_greeting(self) -> str:
        """Fallback greeting when OpenAI is not available"""
        pass
    
    def assistant_followup(self, conversation: List[Dict[str, str]], user_profile: Dict[str, Any], missing_fields: List[str]) -> str:
        """Generate followup message"""
        if not self.client:
            return self.get_fallback_followup(missing_fields)
        
        context_info = f"""
        Current user profile: {user_profile}
        Missing fields: {missing_fields}
        
        Continue the conversation naturally to collect the missing information.
        If you have all required fields, respond with "INFORMATION_COMPLETE".
        """
        conversation.append({"role": "system", "content": context_info})
        
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                temperature=0.7
            )
            return resp.choices[0].message.content
        except Exception:
            return self.get_fallback_followup(missing_fields)
    
    def get_fallback_followup(self, missing_fields: List[str]) -> str:
        """Fallback followup when OpenAI is not available"""
        if missing_fields:
            return f"I'd like to know more about your {missing_fields[0].replace('_',' ').lower()}. Could you please provide that information?"
        return "Thank you for providing all the information!"