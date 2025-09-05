import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class CustomerDataManager:
    """Manages customer data storage by loan type"""
    
    def __init__(self, base_path: str = "customer_data"):
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories for each loan type"""
        loan_types = ["education", "home", "personal", "gold", "business"]
        
        for loan_type in loan_types:
            loan_dir = self.base_path / loan_type
            loan_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (loan_dir / "applications").mkdir(exist_ok=True)
            (loan_dir / "reports").mkdir(exist_ok=True)
    
    def save_customer_application(self, loan_type: str, session_id: str, 
                                customer_info: Dict[str, Any], 
                                loan_data: Dict[str, Any],
                                prediction_result: Optional[Dict[str, Any]] = None) -> str:
        """Save complete customer application data"""
        
        # Create application record
        application = {
            "session_id": session_id,
            "loan_type": loan_type,
            "timestamp": datetime.now().isoformat(),
            "customer_info": customer_info,
            "loan_data": loan_data,
            "prediction_result": prediction_result,
            "status": "completed" if prediction_result else "incomplete"
        }
        
        # Generate filename with timestamp and customer name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        customer_name = customer_info.get("name", "unknown").replace(" ", "_")
        filename = f"{timestamp}_{customer_name}_{session_id[:8]}.json"
        
        # Save to loan type directory
        file_path = self.base_path / loan_type / "applications" / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(application, f, indent=2, ensure_ascii=False)
        
        # Also update CSV summary
        self.update_csv_summary(loan_type, application)
        
        return str(file_path)
    
    def update_csv_summary(self, loan_type: str, application: Dict[str, Any]):
        """Update CSV summary file for the loan type"""
        csv_path = self.base_path / loan_type / "reports" / f"{loan_type}_applications.csv"
        
        # Prepare row data
        row_data = {
            "timestamp": application["timestamp"],
            "session_id": application["session_id"],
            "customer_name": application["customer_info"].get("name", ""),
            "customer_email": application["customer_info"].get("email", ""),
            "customer_phone": application["customer_info"].get("phone", ""),
            "status": application["status"]
        }
        
        # Add loan-specific fields
        if application["prediction_result"]:
            result = application["prediction_result"]["result"]
            row_data.update({
                "eligible_amount": result.get("eligible_amount", 0),
                "interest_rate": result.get("interest_rate", 0),
                "requested_amount": result.get("requested_amount", 0),
                "approval_status": result.get("status", "")
            })
        
        # Add key loan parameters
        loan_data = application["loan_data"]
        if loan_type == "education":
            row_data.update({
                "age": loan_data.get("Age", ""),
                "academic_performance": loan_data.get("Academic_Performance", ""),
                "intended_course": loan_data.get("Intended_Course", ""),
                "cibil_score": loan_data.get("CIBIL_Score", "")
            })
        elif loan_type == "home":
            row_data.update({
                "age": loan_data.get("Age", ""),
                "monthly_income": loan_data.get("Monthly_Income", ""),
                "property_value": loan_data.get("Property_Value", ""),
                "cibil_score": loan_data.get("CIBIL_Score", "")
            })
        elif loan_type == "personal":
            row_data.update({
                "age": loan_data.get("Age", ""),
                "monthly_income": loan_data.get("Monthly_Income", ""),
                "employment_type": loan_data.get("Employment_Type", ""),
                "cibil_score": loan_data.get("CIBIL_Score", "")
            })
        elif loan_type == "gold":
            row_data.update({
                "age": loan_data.get("Age", ""),
                "occupation": loan_data.get("Occupation", ""),
                "monthly_income": loan_data.get("Monthly_Income", ""),
                "cibil_score": loan_data.get("CIBIL_Score", ""),
                "gold_value": loan_data.get("Gold_Value", ""),
                "loan_tenure_years": loan_data.get("Loan_Tenure_Years", "")
            })
        elif loan_type == "business":
            row_data.update({
                "business_age_years": loan_data.get("Business_Age_Years", ""),
                "annual_revenue": loan_data.get("Annual_Revenue", ""),
                "net_profit": loan_data.get("Net_Profit", ""),
                "cibil_score": loan_data.get("CIBIL_Score", ""),
                "business_type": loan_data.get("Business_Type", ""),
                "has_collateral": loan_data.get("Has_Collateral", ""),
                "industry_risk_rating": loan_data.get("Industry_Risk_Rating", ""),
                "location_tier": loan_data.get("Location_Tier", "")
            })
        
        # Write to CSV
        file_exists = csv_path.exists()
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(row_data)
    
    def get_customer_applications(self, loan_type: str, limit: int = 10) -> list:
        """Get recent customer applications for a loan type"""
        applications_dir = self.base_path / loan_type / "applications"
        
        if not applications_dir.exists():
            return []
        
        # Get all JSON files, sorted by modification time (newest first)
        json_files = sorted(
            applications_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        applications = []
        for file_path in json_files[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    applications.append(json.load(f))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return applications
    
    def get_application_stats(self, loan_type: str) -> Dict[str, Any]:
        """Get statistics for a loan type"""
        applications = self.get_customer_applications(loan_type, limit=1000)
        
        if not applications:
            return {"total": 0, "completed": 0, "approved": 0, "partial": 0}
        
        stats = {
            "total": len(applications),
            "completed": len([app for app in applications if app["status"] == "completed"]),
            "approved": 0,
            "partial": 0,
            "average_amount": 0,
            "average_interest": 0
        }
        
        completed_apps = [app for app in applications if app["prediction_result"]]
        
        if completed_apps:
            stats["approved"] = len([app for app in completed_apps 
                                   if app["prediction_result"]["result"]["status"] == "APPROVED"])
            stats["partial"] = len([app for app in completed_apps 
                                  if app["prediction_result"]["result"]["status"] == "PARTIAL_APPROVAL"])
            
            # Calculate averages
            amounts = [app["prediction_result"]["result"]["eligible_amount"] for app in completed_apps]
            interests = [app["prediction_result"]["result"]["interest_rate"] for app in completed_apps]
            
            if amounts:
                stats["average_amount"] = sum(amounts) / len(amounts)
            if interests:
                stats["average_interest"] = sum(interests) / len(interests)
        
        return stats