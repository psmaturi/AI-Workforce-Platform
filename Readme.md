# AI Workforce Intelligence Platform

## Tata Steel — AI/ML Internship Training Project

An AI-powered **Workforce Intelligence Platform** developed as part of the **AI/ML Internship Training at Tata Steel**.

The project combines **Agentic AI, LangGraph, Retrieval-Augmented Generation (RAG), Machine Learning, PostgreSQL, FastAPI, and React** to create an intelligent workforce assistant for Employees, Managers, and HR.

> **Project Status:** Functional prototype / internship project  
> **Data Status:** Synthetic demonstration data; architecture supports future authorized enterprise data integration.

---

## 1. Internship Context

**Organization:** Tata Steel  
**Training Area:** Artificial Intelligence & Machine Learning (AI/ML)  
**Project:** Unlocking Future Workforce with AI  
**Domain:** Workforce Intelligence, Learning & Development, Skill Intelligence, Workforce Planning

The project was developed to explore how AI/ML can support workforce development by connecting employee skills, training, career goals, organizational knowledge, and workforce predictions in a single intelligent platform.

---

## 2. Problem Statement

Traditional Learning & Development systems mainly focus on course delivery and completion tracking. They often provide limited visibility into:

- Current employee skill levels
- Skill gaps against future roles
- Personalized training requirements
- Employee readiness for target roles
- Future skill demand
- Workforce shortages and risks
- Organizational knowledge access
- Manager-level team capability

The objective of this project is to build an intelligent layer that can combine structured workforce data, enterprise knowledge, machine learning predictions, and conversational AI to provide actionable workforce insights.

---

## 3. Objectives

The main objectives are:

1. Build an AI-powered workforce assistant.
2. Provide personalized employee skill and training insights.
3. Identify skill gaps between employees and target roles.
4. Calculate employee readiness for future roles.
5. Recommend relevant training based on skill gaps.
6. Retrieve organizational policies and knowledge using RAG.
7. Predict future skill demand.
8. Forecast workforce requirements.
9. Identify workforce skill risks.
10. Support Employee, Manager, and HR use cases.
11. Implement role-aware access to workforce information.
12. Provide a scalable foundation for future enterprise-data integration.

---

# 4. Key Features

## Employee Features

Employees can interact with the AI assistant to ask questions such as:

- Show me my employee profile.
- Show me my training progress.
- What skills am I missing for the EAF Mechanical Specialist role?
- How ready am I for the EAF Mechanical Specialist role?
- What training should I complete next?
- Which skills should I develop for my career goal?

The system combines employee data, skills, training records, role requirements, ML analysis, and AI reasoning to generate personalized responses.

---

## Manager Features

Managers can access information related to their teams, including:

- Team training progress
- Team skill gaps
- Employee readiness
- Training requirements
- Skill risks
- Workforce planning insights

Manager access is designed around the manager-report hierarchy rather than unrestricted employee access.

---

## HR Features

HR-oriented functionality includes:

- Organization-level workforce insights
- Future skill demand
- Workforce forecasts
- Skill-risk analysis
- Training analytics
- Workforce readiness insights

---

# 5. AI Assistant

The platform uses an Agentic AI architecture rather than a simple chatbot.

### High-Level Flow

```text
User
  |
  v
React Frontend
  |
  v
FastAPI /chat API
  |
  v
Chat Service
  |
  v
LangGraph Workforce Agent
  |
  +--------------------+
  |                    |
  v                    v
Intent Classification  Tool Selection
  |                    |
  +----------+---------+
             |
             v
       Tool Execution
             |
     +-------+-------+----------------+
     |               |                |
     v               v                v
PostgreSQL          RAG              ML Models
     |               |                |
     +-------+-------+----------------+
             |
             v
       Response Generation
             |
             v
          Qwen LLM
             |
             v
        Final Response
```

---

# 6. Agentic AI Architecture

The Agentic AI layer is implemented using **LangGraph**.

The agent can:

1. Understand the user's request.
2. Classify the intent.
3. Identify the required information.
4. Select the appropriate tool or data source.
5. Execute the tool.
6. Combine the returned information.
7. Generate a contextual response.

Example:

```text
"I am Gareth. Analyze my skills, skill gaps,
readiness and recommended training for
the EAF Mechanical Specialist role."

                    |
                    v
             Intent Analysis
                    |
                    v
          Employee Identification
                    |
                    v
             Profile Retrieval
                    |
                    v
              Skill Analysis
                    |
                    v
               Skill Gap
                    |
                    v
               Readiness
                    |
                    v
         Training Recommendation
                    |
                    v
             AI Response
```

---

# 7. Large Language Model

The project uses a locally hosted LLM through **Ollama**.

### Model

```text
Qwen 2.5 7B
```

### Runtime

```text
Ollama
```

Using a local model during development reduces dependency on external model APIs and avoids API quota limitations during the internship prototype.

---

# 8. Retrieval-Augmented Generation (RAG)

RAG is used for enterprise knowledge and policy-related questions.

### RAG Pipeline

```text
Company Documents
       |
       v
Document Processing
       |
       v
Chunking
       |
       v
Embeddings
       |
       v
ChromaDB
       |
       v
Retriever
       |
       v
Relevant Context
       |
       v
Qwen
       |
       v
Grounded Response
```

RAG is used for questions such as:

```text
"What is the company's training approval process?"
```

The system retrieves relevant information from the knowledge base instead of relying only on the LLM's pretrained knowledge.

---

# 9. Structured Data vs RAG

The architecture deliberately separates structured workforce data from document knowledge.

### PostgreSQL

Used for:

- Employee profiles
- Skills
- Training records
- Roles
- Career goals
- Performance records
- Workforce analytics

### RAG / ChromaDB

Used for:

- HR policies
- Training policies
- Organizational knowledge
- Documentation
- Reference information

For example:

```text
"Show me my training progress."
        |
        v
PostgreSQL
```

while:

```text
"What is the training approval process?"
        |
        v
RAG / ChromaDB
```

This prevents structured employee information from being incorrectly answered through document retrieval.

---

# 10. Machine Learning Layer

The ML layer provides workforce intelligence beyond conversational generation.

### Major ML components

```text
Skill Gap Analysis
        |
        v
Readiness Scoring
        |
        v
Training Recommendation
        |
        v
Future Skill Demand Prediction
        |
        v
Workforce Forecasting
        |
        v
Skill Risk Analysis
```

---

## 10.1 Skill Gap Analysis

Compares:

```text
Employee Current Skills
          VS
Target Role Required Skills
```

and identifies:

- Missing skills
- Skills requiring improvement
- Capability gaps

---

## 10.2 Employee Readiness

Estimates how prepared an employee is for a target role based on current capabilities versus role requirements.

Example question:

```text
"How ready am I for the EAF Mechanical Specialist role?"
```

---

## 10.3 Training Recommendation

Training recommendations are linked to identified skill gaps.

```text
Skill Gap
   |
   v
Missing Skill
   |
   v
Relevant Training
   |
   v
Personalized Recommendation
```

---

## 10.4 Future Skill Demand Prediction

A Random Forest classification model is used for future skill-demand prediction.

Example question:

```text
"Which skills will become important in the future?"
```

---

## 10.5 Workforce Forecasting

An XGBoost regression model is used for workforce forecasting.

Example question:

```text
"Which departments are expected to have workforce gaps?"
```

---

## 10.6 Skill Risk Analysis

The system identifies workforce risks such as:

- Skill deficiencies
- Single-person skill dependencies
- Potential capability shortages

---

# 11. ML Model Management

A centralized `ModelManager` is used to load and cache trained models.

This avoids repeatedly loading model binaries during requests.

Trained models are stored using:

```text
.joblib
```

The ML service layer connects:

```text
Repositories
     |
     v
ML Engines
     |
     v
Predictive Models
     |
     v
Agent / API
```

---

# 12. Backend Architecture

The backend is built using:

```text
Python
FastAPI
LangGraph
LangChain
Ollama
Qwen
PostgreSQL
SQLAlchemy
Alembic
ChromaDB
Scikit-learn
XGBoost
Pandas
NumPy
Pytest
```

### Main backend responsibilities

- API routing
- Chat processing
- Agent orchestration
- Tool execution
- Database access
- RAG retrieval
- ML inference
- Authentication context
- Authorization
- Logging
- Testing

---

# 13. Database

PostgreSQL is used as the primary structured workforce database.

### Main data entities

```text
Employees
Departments
Job Roles
Skills
Employee Skills
Training Courses
Employee Training
Career Goals
Performance Reviews
```

### ML-related entities

```text
Model Metadata
Skill Predictions
Workforce Forecasts
Employee Readiness
Skill Risks
```

---

# 14. Synthetic Workforce Dataset

Because authorized enterprise workforce data was not used in the internship prototype, realistic synthetic data was generated for development and demonstration.

A data-source field distinguishes:

```text
SYNTHETIC_DEMO
```

from the future option:

```text
AUTHORIZED_ENTERPRISE_DATA
```

### Dataset

| Entity | Quantity |
|---|---:|
| Departments | 10 |
| Job Roles | 71 |
| Skills | 200 |
| Training Courses | 100 |
| Employees | 500 |
| Employee-Skill Relationships | 3000 |
| Employee-Training Records | 3000 |
| Career Goals | 500 |
| Performance Reviews | 1000 |
| Readiness Records | 50 |
| Workforce Forecasts | 10 |
| Skill Predictions | 20 |
| Skill Risks | 10 |

Skills are distributed across categories including:

- Technical
- Safety
- Leadership
- Digital
- Behavioral

---

# 15. Data Generation & Ingestion

Synthetic CSV generation:

```text
scripts/generate_synthetic_csvs.py
```

Data ingestion:

```text
scripts/import_workforce_data.py
```

The ingestion process handles:

- Schema recreation
- Field validation
- Data cleaning
- Manager hierarchy resolution
- Database insertion
- PostgreSQL/SQLite workflows

---

# 16. Security & Personalization

Employee context is passed from the frontend to the backend using session information.

The frontend sends:

```text
X-Employee-Id
X-Employee-Number
```

The backend passes this context through:

```text
FastAPI
   |
   v
Chat Service
   |
   v
Workforce Agent
   |
   v
LangGraph State / RunnableConfig
   |
   v
Agent Tools
```

This allows the system to personalize responses and enforce authorization.

---

# 17. Training Progress Security

Training progress is handled using actual structured records.

### Employee

Can access:

```text
Own training records
```

### Manager

Can access:

```text
Training records of authorized/direct reports
```

### Unauthorized access

Returns:

```text
Access Denied
```

This prevents the AI assistant from becoming an unrestricted employee-data lookup system.

---

# 18. Training Progress Routing

Training-progress requests use a dedicated tool:

```text
TrainingProgressTool
```

The flow is:

```text
User Question
      |
      v
Training Progress Intent
      |
      v
TrainingProgressTool
      |
      v
PostgreSQL Employee Training Records
      |
      v
Progress Calculation
      |
      v
Formatted Response
```

RAG is intentionally bypassed for this use case.

---

# 19. Training Status Handling

Training records support status categories such as:

```text
Completed
In Progress
Not Started
```

Expired/overdue courses are also categorized appropriately:

- If hours have been completed → `In Progress`
- If no hours have been completed → `Not Started`

This prevents overdue courses from disappearing from progress calculations.

---

# 20. Frontend

The frontend is built with:

```text
React
TypeScript
```

The frontend provides:

- Authentication/session context
- Role-specific views
- AI chat interface
- Workforce dashboards
- Employee information
- Training information
- Analytics views

The frontend communicates with the backend through REST APIs.

---

# 21. React AI Assistant

The chat UI maintains messages using:

```typescript
type ChatMessage = {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
};
```

API response:

```json
{
  "response": "..."
}
```

---

# 22. Frontend Debugging

During development, an empty AI response bubble appeared in the React interface.

### Root cause

The backend successfully generated a knowledge response but failed to assign it to:

```text
final_answer
```

Therefore the API returned:

```json
{
  "response": ""
}
```

The React UI correctly rendered that empty response.

### Fix

The response content was explicitly assigned:

```text
final_answer = str(response.content)
```

After the backend fix, the empty bubble and apparent duplication behavior disappeared.

---

# 23. Testing

### Backend Agent Tests

Command:

```bash
..\venv\Scripts\python -m pytest tests/agent/test_training_progress.py
```

Result:

```text
47 tests passed
```

The tests cover areas including:

- Intent/target extraction
- Session metadata
- Employee authorization
- Manager authorization
- Training progress behavior

---

## Frontend Testing

### Lint

```bash
npm run lint
```

Result:

```text
0 errors
```

### Production Build

```bash
npm run build
```

Result:

```text
0 compile/TypeScript errors
```

---

# 24. Representative Test Queries

The following scenarios were used for end-to-end verification:

```text
Show me my employee profile.
```

```text
Show me my training progress.
```

```text
What skills am I missing for the EAF Mechanical Specialist role?
```

```text
How ready am I for the EAF Mechanical Specialist role?
```

```text
What training should I complete next?
```

```text
What is the company's training approval process?
```

```text
Which skills will become important in the future?
```

```text
Which departments are expected to have workforce gaps?
```

```text
What are our highest-risk skills?
```

```text
I am Gareth. Analyze my current skills, skill gaps, readiness, and recommended training.
```

---

# 25. Development Issues Solved

Several real development issues were identified and resolved during implementation:

- Ollama port conflict
- External LLM API quota limitations
- Local LLM memory/runtime issues
- Windows terminal encoding issue
- Repository method mismatch
- Incorrect training-progress routing
- Incorrect employee target extraction
- Empty AI response
- Frontend empty-message rendering
- Apparent duplicate message behavior
- Expired training classification
- Employee/manager authorization handling

These debugging steps helped validate the complete request-to-response pipeline.

---

# 26. Project Structure

```text
AI-Workforce-Platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agent/
│   │   ├── database/
│   │   ├── llm/
│   │   ├── ml/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── tests/
│   │   └── agent/
│   │
│   ├── scripts/
│   │   ├── generate_synthetic_csvs.py
│   │   └── import_workforce_data.py
│   │
│   ├── data/
│   │   └── raw/
│   │
│   ├── train_models.py
│   └── scratch_test.py
│
└── frontend/
    └── src/
        ├── api/
        ├── components/
        ├── pages/
        └── ...
```

---

# 27. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript |
| Backend | FastAPI |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| LLM | Qwen 2.5 7B |
| Local LLM Runtime | Ollama |
| RAG | ChromaDB |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| ML | Scikit-learn, XGBoost |
| Data Processing | Pandas, NumPy |
| Model Serialization | Joblib |
| Testing | Pytest |
| API | REST |
| Version Control | Git |

---

# 28. Example End-to-End Flow

For:

> "What skills am I missing for the EAF Mechanical Specialist role?"

```text
React
  ↓
POST /chat
  ↓
FastAPI
  ↓
Chat Service
  ↓
LangGraph Agent
  ↓
Intent Classification
  ↓
Employee Identification
  ↓
Skill Gap Tool
  ↓
PostgreSQL
  ↓
Employee Skills + Role Requirements
  ↓
Skill Gap Analysis
  ↓
Qwen
  ↓
Personalized Response
  ↓
React
```

---

# 29. Example Training Flow

```text
"Show me my training progress."
            |
            v
     Intent Classification
            |
            v
    TrainingProgressTool
            |
            v
       PostgreSQL
            |
            v
    Employee Training Data
            |
            v
    Progress Calculation
            |
            v
     AI/Programmatic Response
```

---

# 30. Example RAG Flow

```text
"What is the training approval process?"
                  |
                  v
          Intent Classification
                  |
                  v
               RAG Tool
                  |
                  v
             ChromaDB
                  |
                  v
          Relevant Documents
                  |
                  v
               Qwen
                  |
                  v
        Grounded AI Response
```

---

# 31. Example ML Flow

```text
Employee + Role
       |
       v
Current Skills
       |
       v
Required Skills
       |
       +----------+
       |          |
       v          v
   Skill Gap   Readiness
       |
       v
Training Recommendation
```

---

# 32. Industry Relevance

The project is designed around workforce challenges relevant to large industrial organizations:

- Workforce capability visibility
- Reskilling and upskilling
- AI/automation readiness
- Personalized learning
- Skill gap identification
- Workforce planning
- Future skill demand
- Knowledge retention
- Manager decision support
- HR workforce strategy

The project therefore goes beyond a generic chatbot and demonstrates how AI/ML can become a workforce-intelligence layer over structured enterprise data and organizational knowledge.

---

# 33. Data Privacy & Enterprise Readiness

The current prototype uses synthetic data.

No real employee personal data should be inserted into the demo environment.

For future enterprise deployment, the architecture should integrate only:

```text
Authorized Enterprise Data
```

with appropriate:

- Authentication
- Authorization
- Data governance
- Privacy controls
- Audit logging
- Human oversight
- Model monitoring

The `data_source` field provides an explicit distinction between synthetic demonstration data and future authorized enterprise data.

---

# 34. Current Limitations

This is an internship prototype and has several limitations:

1. Workforce data is synthetic.
2. Production enterprise authentication is not yet integrated.
3. Production deployment of the local LLM requires a suitable inference environment.
4. Manager team-level routing requires final end-to-end verification for all team queries.
5. HR workflows require final production-style validation.
6. ML predictions are demonstration models trained on synthetic data.
7. Model performance on real Tata Steel workforce data has not been established.
8. Production monitoring and governance still need to be added.

---

# 35. Future Enhancements

Potential next steps include:

- Integration with authorized HRIS/LMS systems
- Real enterprise skill taxonomy
- Production-grade authentication
- Fine-grained RBAC
- Enterprise SSO
- Model monitoring
- Explainable ML
- Human-in-the-loop approval
- Automated training enrollment
- Internal talent marketplace integration
- Knowledge capture from experienced employees
- Mentor matching
- Advanced workforce simulations
- Real-time workforce dashboards
- Production cloud deployment
- LLM observability and evaluation
- Automated model retraining

---

# 36. How to Run the Project

## Prerequisites

Install:

- Python 3.x
- Node.js
- PostgreSQL
- Ollama
- Git

---

## Start Ollama

```bash
ollama serve
```

Pull the model:

```bash
ollama pull qwen2.5:7b
```

---

## Backend Setup

```bash
cd backend
```

Create/activate a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in `.env`.

Example:

```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database>
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

---

## Generate Synthetic Data

```bash
python scripts/generate_synthetic_csvs.py
```

Import the data:

```bash
python scripts/import_workforce_data.py
```

---

## Train ML Models

```bash
python train_models.py
```

---

## Run Tests

```bash
python -m pytest
```

Training-progress tests:

```bash
python -m pytest tests/agent/test_training_progress.py
```

---

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 37. Development Verification

Before deployment, verify:

```text
[ ] PostgreSQL connection
[ ] Ollama running
[ ] Qwen model available
[ ] Backend health endpoint
[ ] Chat API
[ ] Employee login/session
[ ] Employee AI assistant
[ ] Training progress
[ ] Skill gap
[ ] Readiness
[ ] Training recommendations
[ ] RAG policy queries
[ ] Future skill prediction
[ ] Workforce forecasting
[ ] Skill risk
[ ] Manager access
[ ] Manager team queries
[ ] HR access
[ ] HR analytics
[ ] Authorization boundaries
[ ] Backend tests
[ ] Frontend lint
[ ] Frontend build
[ ] Production environment variables
```

---

# 38. Project Outcome

The project demonstrates a working AI/ML workforce intelligence prototype that integrates:

```text
Agentic AI
    +
RAG
    +
Machine Learning
    +
Structured Workforce Data
    +
Role-Based Access
    +
React Frontend
    =
AI Workforce Intelligence Platform
```

The resulting system can answer workforce questions using the appropriate combination of:

- PostgreSQL data
- RAG knowledge
- ML predictions
- Agent tools
- LLM reasoning

rather than treating every question as a generic chatbot query.

---

# 39. Internship Learning Outcomes

Through this project, the internship provided practical exposure to:

### AI/ML

- Machine Learning pipelines
- Classification
- Regression
- Workforce prediction
- Feature-based analysis
- Model evaluation
- Model persistence

### Generative AI

- LLM integration
- Prompt engineering
- Local LLM deployment
- Qwen
- Ollama
- RAG

### Agentic AI

- LangGraph
- Agent state
- Intent classification
- Tool calling
- Multi-step workflows
- Context propagation

### Backend

- FastAPI
- REST APIs
- Service-layer architecture
- Dependency/context injection
- PostgreSQL
- SQLAlchemy
- Alembic

### Frontend

- React
- TypeScript
- API integration
- Chat interfaces
- Role-based UI

### Engineering

- Unit testing
- Integration testing
- Debugging
- Logging
- Data ingestion
- Synthetic data generation
- Security and authorization
- Production-readiness considerations

---

# 40. Internship Summary

This project was developed as part of the **AI/ML Internship Training at Tata Steel** with the objective of applying AI and machine learning concepts to a practical industrial workforce problem.

The project progressed from a basic AI assistant into a broader workforce intelligence platform by integrating:

```text
LLM
+
Agentic AI
+
RAG
+
Machine Learning
+
PostgreSQL
+
FastAPI
+
React
```

The final prototype demonstrates how AI can support workforce development through personalized skill analysis, training intelligence, readiness assessment, future skill prediction, workforce forecasting, and role-aware conversational assistance.

---

## Author

**Pardha Saradhi Maturi**

B.Tech — Computer Science & Engineering  
SRM University-AP

**AI/ML Trainee Intern — Tata Steel**

---

## Acknowledgement

This project was developed as part of the AI/ML internship training at **Tata Steel**.

Special thanks to Tata Steel for providing the opportunity to work on an industry-oriented AI/ML workforce intelligence problem and gain practical exposure to Agentic AI, Machine Learning, RAG, backend engineering, databases, and frontend integration.
