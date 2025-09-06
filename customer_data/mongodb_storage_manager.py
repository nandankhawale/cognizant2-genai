import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBStorageManager:
    """Manages customer data storage using MongoDB Atlas"""
    
    def __init__(self, mongodb_uri: str = None, database_name: str = "loan_applications"):
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE", "loan_applications")
        
        if not self.mongodb_uri:
            raise ValueError("MongoDB URI not provided. Set MONGODB_URI environment variable.")
        
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Try different connection approaches for Windows compatibility
            connection_configs = [
                # Standard connection with SSL
                {
                    "serverSelectionTimeoutMS": 10000,
                    "connectTimeoutMS": 20000,
                    "socketTimeoutMS": 30000,
                    "retryWrites": True,
                    "w": 'majority'
                },
                # Connection without explicit SSL settings
                {
                    "serverSelectionTimeoutMS": 15000,
                    "connectTimeoutMS": 30000,
                    "socketTimeoutMS": 45000,
                },
                # Minimal connection
                {
                    "serverSelectionTimeoutMS": 20000,
                }
            ]
            
            for i, config in enumerate(connection_configs):
                try:
                    logger.info(f"Attempting MongoDB connection (method {i+1})...")
                    self.client = MongoClient(self.mongodb_uri, **config)
                    
                    # Test the connection
                    self.client.admin.command('ping')
                    self.db = self.client[self.database_name]
                    
                    logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
                    
                    # Create indexes for better performance
                    self._create_indexes()
                    return
                    
                except Exception as e:
                    logger.warning(f"Connection method {i+1} failed: {e}")
                    if self.client:
                        self.client.close()
                        self.client = None
                    continue
            
            # If all methods fail, raise error
            raise ConnectionError("All MongoDB connection methods failed")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # Don't raise error - allow fallback to local storage
            logger.warning("MongoDB connection failed, will use fallback methods")
            self.client = None
            self.db = None
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        loan_types = ["education", "home", "personal", "gold", "business", "car"]
        
        for loan_type in loan_types:
            collection = self.db[f"{loan_type}_loans"]
            
            # Create indexes
            collection.create_index("session_id", unique=True)
            collection.create_index("timestamp")
            collection.create_index("status")
            collection.create_index("customer_info.email")
            collection.create_index("customer_info.phone")
    
    def _is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self.client is not None and self.db is not None
    
    def save_customer_application(self, loan_type: str, session_id: str, 
                                customer_info: Dict[str, Any], 
                                loan_data: Dict[str, Any],
                                prediction_result: Optional[Dict[str, Any]] = None) -> str:
        """Save complete customer application data to MongoDB"""
        
        if not self._is_connected():
            logger.warning("MongoDB not connected, skipping save")
            return session_id
        
        try:
            # Create application document
            application = {
                "session_id": session_id,
                "loan_type": loan_type,
                "timestamp": datetime.utcnow(),
                "customer_info": customer_info,
                "loan_data": loan_data,
                "prediction_result": prediction_result,
                "status": "completed" if prediction_result else "incomplete",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Get collection for this loan type
            collection = self.db[f"{loan_type}_loans"]
            
            # Insert or update the document
            result = collection.replace_one(
                {"session_id": session_id},
                application,
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"New application saved: {session_id} for {loan_type} loan")
                return str(result.upserted_id)
            else:
                logger.info(f"Application updated: {session_id} for {loan_type} loan")
                return session_id
                
        except Exception as e:
            logger.error(f"Error saving application to MongoDB: {e}")
            raise Exception(f"Failed to save application: {e}")
    
    def get_customer_applications(self, loan_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent customer applications for a loan type from MongoDB"""
        
        if not self._is_connected():
            logger.warning("MongoDB not connected, returning empty list")
            return []
        
        try:
            collection = self.db[f"{loan_type}_loans"]
            
            # Query applications, sorted by timestamp (newest first)
            cursor = collection.find().sort("timestamp", -1).limit(limit)
            
            applications = []
            for doc in cursor:
                # Convert ObjectId to string and datetime to ISO format
                doc["_id"] = str(doc["_id"])
                if isinstance(doc.get("timestamp"), datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                if isinstance(doc.get("created_at"), datetime):
                    doc["created_at"] = doc["created_at"].isoformat()
                if isinstance(doc.get("updated_at"), datetime):
                    doc["updated_at"] = doc["updated_at"].isoformat()
                
                applications.append(doc)
            
            logger.info(f"Retrieved {len(applications)} applications for {loan_type} loans")
            return applications
            
        except Exception as e:
            logger.error(f"Error retrieving applications from MongoDB: {e}")
            return []
    
    def get_application_stats(self, loan_type: str) -> Dict[str, Any]:
        """Get statistics for a loan type from MongoDB"""
        
        if not self._is_connected():
            logger.warning("MongoDB not connected, returning empty stats")
            return {"total": 0, "completed": 0, "approved": 0, "partial": 0, "average_amount": 0, "average_interest": 0}
        
        try:
            collection = self.db[f"{loan_type}_loans"]
            
            # Get total count
            total = collection.count_documents({})
            
            # Get completed applications
            completed = collection.count_documents({"status": "completed"})
            
            # Get approval statistics
            approved = collection.count_documents({
                "prediction_result.result.status": "APPROVED"
            })
            
            partial = collection.count_documents({
                "prediction_result.result.status": "PARTIAL_APPROVAL"
            })
            
            # Calculate averages for completed applications
            pipeline = [
                {"$match": {"status": "completed", "prediction_result": {"$exists": True}}},
                {"$group": {
                    "_id": None,
                    "avg_amount": {"$avg": {
                        "$ifNull": [
                            "$prediction_result.result.eligible_amount",
                            "$prediction_result.result.approved_amount"
                        ]
                    }},
                    "avg_interest": {"$avg": "$prediction_result.result.interest_rate"}
                }}
            ]
            
            avg_result = list(collection.aggregate(pipeline))
            
            stats = {
                "total": total,
                "completed": completed,
                "approved": approved,
                "partial": partial,
                "average_amount": avg_result[0]["avg_amount"] if avg_result else 0,
                "average_interest": avg_result[0]["avg_interest"] if avg_result else 0
            }
            
            logger.info(f"Retrieved stats for {loan_type} loans: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats from MongoDB: {e}")
            return {"total": 0, "completed": 0, "approved": 0, "partial": 0, "average_amount": 0, "average_interest": 0}
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all loan types"""
        loan_types = ["education", "home", "personal", "gold", "business", "car"]
        all_stats = {}
        
        for loan_type in loan_types:
            all_stats[loan_type] = self.get_application_stats(loan_type)
        
        return all_stats
    
    def export_to_csv(self, loan_type: str) -> str:
        """Generate CSV export and return file path (for compatibility with local storage)"""
        from pathlib import Path
        import csv
        
        # Create reports directory
        reports_dir = Path("customer_data") / loan_type / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        csv_path = reports_dir / f"{loan_type}_applications.csv"
        
        # Get data from MongoDB
        csv_data = self.export_to_csv_data(loan_type)
        
        if not csv_data:
            # Create empty CSV with headers
            headers = ["timestamp", "session_id", "customer_name", "customer_email", 
                      "customer_phone", "status", "eligible_amount", "interest_rate", 
                      "requested_amount", "approval_status"]
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
        else:
            # Write data to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if csv_data:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
        
        return str(csv_path)
    
    def export_to_csv_data(self, loan_type: str) -> List[Dict[str, Any]]:
        """Get all applications for CSV export"""
        
        try:
            collection = self.db[f"{loan_type}_loans"]
            
            # Get all completed applications
            cursor = collection.find({"status": "completed"}).sort("timestamp", 1)
            
            csv_data = []
            for doc in cursor:
                # Prepare row data
                row_data = {
                    "timestamp": doc["timestamp"].isoformat() if isinstance(doc["timestamp"], datetime) else doc["timestamp"],
                    "session_id": doc["session_id"],
                    "customer_name": doc["customer_info"].get("name", ""),
                    "customer_email": doc["customer_info"].get("email", ""),
                    "customer_phone": doc["customer_info"].get("phone", ""),
                    "status": doc["status"]
                }
                
                # Add prediction results
                if doc.get("prediction_result"):
                    result = doc["prediction_result"]["result"]
                    row_data.update({
                        "eligible_amount": result.get("eligible_amount", result.get("approved_amount", 0)),
                        "interest_rate": result.get("interest_rate", 0),
                        "requested_amount": result.get("requested_amount", 0),
                        "approval_status": result.get("status", "")
                    })
                
                # Add loan-specific fields
                loan_data = doc["loan_data"]
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
                        "income": loan_data.get("Income", ""),
                        "property_value": loan_data.get("Property_value", ""),
                        "cibil_score": loan_data.get("CIBIL_score", "")
                    })
                elif loan_type == "personal":
                    row_data.update({
                        "age": loan_data.get("Age", ""),
                        "annual_income": loan_data.get("Annual_Income", ""),
                        "employment_type": loan_data.get("Employment_Type", ""),
                        "cibil_score": loan_data.get("CIBIL_Score", "")
                    })
                elif loan_type == "gold":
                    row_data.update({
                        "age": loan_data.get("Age", ""),
                        "occupation": loan_data.get("Occupation", ""),
                        "annual_income": loan_data.get("Annual_Income", ""),
                        "cibil_score": loan_data.get("CIBIL_Score", ""),
                        "gold_value": loan_data.get("Gold_Value", ""),
                        "loan_tenure": loan_data.get("Loan_Tenure", "")
                    })
                elif loan_type == "business":
                    row_data.update({
                        "business_age_years": loan_data.get("Business_Age_Years", ""),
                        "annual_revenue": loan_data.get("Annual_Revenue", ""),
                        "net_profit": loan_data.get("Net_Profit", ""),
                        "cibil_score": loan_data.get("CIBIL_Score", ""),
                        "business_type": loan_data.get("Business_Type", ""),
                        "has_collateral": loan_data.get("Has_Collateral", "")
                    })
                
                csv_data.append(row_data)
            
            logger.info(f"Prepared {len(csv_data)} records for CSV export for {loan_type} loans")
            return csv_data
            
        except Exception as e:
            logger.error(f"Error preparing CSV data from MongoDB: {e}")
            return []
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Check MongoDB connection status"""
        try:
            # Ping the database
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command("dbstats")
            
            return {
                "connected": True,
                "database": self.database_name,
                "collections": self.db.list_collection_names(),
                "storage_size": stats.get("storageSize", 0),
                "data_size": stats.get("dataSize", 0)
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Test connection function
def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        manager = MongoDBStorageManager()
        status = manager.get_connection_status()
        print("MongoDB Connection Status:", json.dumps(status, indent=2))
        manager.close_connection()
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()