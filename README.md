# NextBank - AI-Powered Loan Application System

A modern, integrated loan application system with professional Next.js frontend and FastAPI backend, supporting multiple loan types with AI-powered chatbot interface.

## 🌟 Key Features

- **🤖 AI-Powered Chatbot**: Natural conversation flow with instant loan eligibility
- **🏦 Multi-Loan Support**: Education, Home, and Personal loans
- **⚡ Real-time Predictions**: Instant loan amount and interest rate calculation
- **📱 Modern UI**: Professional Next.js frontend with responsive design
- **📊 Admin Dashboard**: View applications and statistics
- **🔒 Secure API**: FastAPI backend with comprehensive validation

## 🚀 Quick Start

### Integrated Startup (Recommended)
```bash
# Run both frontend and backend together
python start_integrated_app.py

# Or on Windows
start_integrated_app.bat
```

### Manual Startup
```bash
# Start backend (Terminal 1)
python loan_app.py

# Start frontend (Terminal 2)
cd Banking-Marketing-master
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000 (Next.js Banking Website)
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Admin Dashboard**: `python admin_dashboard.py`

## Project Structure

```
├── Banking-Marketing-master/    # Next.js Frontend
│   ├── components/             # React components
│   │   ├── Chatbot.jsx        # AI loan chatbot
│   │   ├── Hero.jsx           # Landing page
│   │   └── Services.jsx       # Banking services
│   ├── app/                   # Next.js app directory
│   └── config/                # API configuration
├── loan_services/             # Backend loan services
│   ├── base_loan.py          # Abstract base class
│   ├── education_loan.py     # Education loan logic
│   ├── home_loan.py          # Home loan logic
│   ├── personal_loan.py      # Personal loan logic
│   └── loan_factory.py       # Service factory
├── customer_data/             # Customer data storage
├── models/                    # ML models by loan type
├── loan_app.py               # FastAPI backend
├── start_integrated_app.py   # Integrated startup script
└── requirements.txt
```

## 🔒 Security & Setup

### ⚠️ IMPORTANT: Before GitHub Upload

**NEVER commit these sensitive files:**
- `.env` - Contains OpenAI API keys
- `Banking-Marketing-master/.env` - Frontend environment variables
- `customer_data/*/applications/` - Customer data
- Any files with API keys or personal information

**Safe files to commit:**
- `.env.example` - Template without real keys
- `Banking-Marketing-master/.env.example` - Frontend template
- All source code files
- Documentation and setup files

### Setup Instructions

1. **Activate virtual environment:**
   ```bash
   fastapi_env\Scripts\activate.bat
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup:**
   ```bash
   # Copy template files
   cp .env.example .env
   cp Banking-Marketing-master/.env.example Banking-Marketing-master/.env.local
   
   # Edit .env and add your actual OpenAI API key
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

4. **Model files (optional for full ML functionality):**
   - Education: Place models in `models/education _loan_models/`
   - Home: Place models in `models/home_loan_models/`
   - Personal: Place models in `models/personal_loan_models/`

📖 **For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Running Applications

### Multi-Loan App (Recommended)
```bash
uvicorn loan_app:app --reload --port 8001
```
Or:
```bash
python loan_app.py
```
**URL:** http://localhost:8001

### Education Loan App (Legacy)
```bash
uvicorn app:app --reload --port 8000
```
**URL:** http://localhost:8000

### Basic App
```bash
uvicorn main:app --reload --port 8000
```
**URL:** http://localhost:8000

## API Documentation

- **Multi-Loan API:** http://localhost:8001/docs
- **Education Loan API:** http://localhost:8000/docs

## Loan Types Supported

### 1. Education Loan
**Fields:** Age, Academic Performance, Course, University Tier, Income, Guarantor Networth, CIBIL Score, etc.
**Use Case:** Student loans for higher education

### 2. Home Loan  
**Fields:** Age, Employment Type, Income, Property Value, Property Type, Location, CIBIL Score, etc.
**Use Case:** Property purchase, construction, renovation

### 3. Personal Loan
**Fields:** Age, Employment, Income, Company Type, Experience, CIBIL Score, Loan Purpose, etc.
**Use Case:** Medical, travel, wedding, debt consolidation

## API Endpoints

### Multi-Loan App (`loan_app.py`)
- `GET /health` - Health check
- `GET /loan-types` - Get available loan types
- `POST /chat/start` - Start chat session (specify loan type)
- `POST /chat/message` - Send message to chatbot
- `GET /session/{session_id}` - Get session information

### Usage Example
```python
# Start a home loan chat with customer info
POST /chat/start
{
  "loan_type": "home",
  "customer_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210"
  }
}

# Send messages
POST /chat/message  
{
  "session_id": "abc123",
  "message": "I want a loan for buying a 2BHK apartment"
}
```

## Customer Data Management

### Data Storage Structure
```
customer_data/
├── education/
│   ├── applications/     # Individual JSON files
│   └── reports/         # CSV summaries
├── home/
│   ├── applications/
│   └── reports/
└── personal/
    ├── applications/
    └── reports/
```

### Admin Dashboard
```bash
python admin_dashboard.py
```
- View application statistics
- Browse recent applications
- Export CSV reports
- Customer data management

## Features

- **Modular Architecture:** Easy to add new loan types
- **AI-Powered:** Uses OpenAI for natural conversation
- **ML Predictions:** Loan amount and interest rate predictions
- **Customer Data Management:** Collects and stores customer information
- **File Storage:** Organized by loan type with JSON and CSV exports
- **Admin Dashboard:** View statistics and customer applications
- **Graceful Degradation:** Works without OpenAI/ML models (limited functionality)
- **Session Management:** Maintains conversation context
- **Input Validation:** Handles various number formats (lakhs, crores)

## Frontend Interface

A modern chatbot UI is available in the `frontend/` directory.

### Quick Start Frontend
```bash
# Terminal 1: Start backend
python loan_app.py

# Terminal 2: Start frontend (from frontend/ directory)
cd frontend
python server.py
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001

### Frontend Features
- 🤖 Interactive chatbot interface
- 🎯 Loan type selection (Education/Home/Personal)
- 📱 Responsive design for mobile/desktop
- 📊 Visual prediction results
- ⚡ Real-time chat with AI assistant

## Development

### Adding New Loan Type
1. Create new service class inheriting from `BaseLoanService`
2. Implement required abstract methods
3. Add to `LoanServiceFactory`
4. Create model directory structure
5. Update frontend loan options (optional)

### Project Structure
```
├── frontend/              # React-like chatbot UI
│   ├── index.html        # Main interface
│   ├── styles.css        # Modern styling
│   ├── script.js         # Chatbot logic
│   └── server.py         # Development server
├── loan_services/        # Modular backend services
├── models/              # ML models by loan type
└── *.py                 # FastAPI applications
```