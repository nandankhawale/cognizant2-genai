from typing import Dict, Optional
import os
from .education_loan import EducationLoanService
from .home_loan import HomeLoanService
from .personal_loan import PersonalLoanService
from .gold_loan import GoldLoanService
from .business_loan import BusinessLoanService
from .base_loan import BaseLoanService

class LoanServiceFactory:
    """Factory class to create appropriate loan service instances"""
    
    _services: Dict[str, BaseLoanService] = {}
    
    @classmethod
    def get_service(cls, loan_type: str, openai_api_key: Optional[str] = None) -> BaseLoanService:
        """Get loan service instance for the specified loan type"""
        
        if loan_type not in cls._services:
            cls._services[loan_type] = cls._create_service(loan_type, openai_api_key)
        
        return cls._services[loan_type]
    
    @classmethod
    def _create_service(cls, loan_type: str, openai_api_key: Optional[str] = None) -> BaseLoanService:
        """Create a new loan service instance"""
        
        model_paths = {
            "education": "models/education _loan_models",
            "home": "models/home_loan_models", 
            "personal": "models/personal_loan_models",
            "gold": "models/gold_loan_models",
            "business": "models/business_loan_models"
        }
        
        service_classes = {
            "education": EducationLoanService,
            "home": HomeLoanService,
            "personal": PersonalLoanService,
            "gold": GoldLoanService,
            "business": BusinessLoanService
        }
        
        if loan_type not in service_classes:
            raise ValueError(f"Unsupported loan type: {loan_type}")
        
        model_path = model_paths[loan_type]
        service_class = service_classes[loan_type]
        
        return service_class(model_path, openai_api_key)
    
    @classmethod
    def get_available_loan_types(cls) -> list:
        """Get list of available loan types"""
        return ["education", "home", "personal", "gold", "business"]
    
    @classmethod
    def clear_cache(cls):
        """Clear cached service instances"""
        cls._services.clear()