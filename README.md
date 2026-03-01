## Municipality AI Decision Support System
## AI Systems Engineering – Innovation Project

## Author: Nazish Pervaiz Gill
Master’s in Data Science
University of Naples Federico II

### 1. Abstract

This project presents a production-style AI-assisted municipal complaint prioritization system integrating supervised machine learning within an operational decision workflow.
The system processes free-text citizen complaints, generates priority predictions (LOW, MEDIUM, HIGH), and embeds them inside a structured human-in-the-loop validation pipeline. Final decisions remain under human authority to ensure governance, accountability, and responsible AI deployment.
The contribution of this project is not merely a classifier, but a fully integrated AI system including:

* RESTful backend architecture
* Database-backed inference pipeline
* Workflow state management
* Human override mechanisms
* Governance metrics and audit logging
* Reproducible demo deployment

### 2. System Objectives

The system aims to:
* Process unstructured complaint text
* Automatically classify complaint priority
* Provide probabilistic confidence estimates
* Enable human validation and override
* Track ticket lifecycle through structured workflow states
* Monitor model reliability using override metrics
* Provide a reproducible full-stack demonstration

### 3. System Architecture

Citizen Portal (Streamlit)
    → FastAPI Backend (REST API)
        → SQLite Database
            → ML Model (TF-IDF + Logistic Regression)

The architecture follows a layered separation of concerns:
* Presentation layer (Frontend)
* API and business logic layer (Backend)
* Data persistence layer (Database)
* ML inference module

The machine learning component is embedded within a REST architecture and is not deployed as an isolated script.

## 4. Core Components
### 4.1 Frontend (Streamlit)

Two operational interfaces are implemented.

#### Citizen Portal
* Submit complaint
* Automatic AI prediction
* Track ticket progress
* View workflow status

#### Office Portal
* View ticket inbox
* Run prediction manually
* Validate or override AI output
* Update workflow status
* Monitor override rate and review audit table
  
The frontend consumes backend APIs and does not contain ML logic.

### 4.2 Backend (FastAPI)

The backend exposes structured REST endpoints grouped into domains:
* System
* Tickets
* ML
* Review
* Workflow
* Metrics

Responsibilities include:
* Ticket creation
* Model inference
* Human review handling
* Workflow state transitions
* Metric computation
* Audit trail management

Interactive API documentation is available via Swagger.

### 4.3 Database (SQLite)

Three primary tables are implemented.
##### Tickets
Stores complaint data and workflow status.

##### Predictions
Stores AI outputs including:
* Predicted label
* Confidence score
* Model version
* Timestamp

#### Reviews
* Stores human validation decisions including:
* Final label
* Reviewer ID
* Timestamp
* Optional comment

This structure ensures traceability and reproducibility of decisions.

### 5. Machine Learning Component
#### Model Choice
TF-IDF Vectorization
Logistic Regression Classifier

##### Reasons for Selection
* Efficient for sparse text data
* Fast inference time
* Probabilistic output via predict_proba
* Suitable for lightweight production deployment
* Interpretable and computationally efficient

The ML model transforms unstructured complaint text into structured decision-support signals.

#### Example Output
{
  "ticket_id": 1,
  "predicted_label": "HIGH",
  "confidence": 0.87
}

Confidence values support risk-aware human oversight.

### 6. Human-in-the-Loop Design

The system enforces a structured decision pipeline:

NEW → REVIEWED → IN_PROGRESS → COMPLETED

AI predictions are advisory only. Human reviewers must validate or override the prediction before workflow progression. Overrides are explicitly recorded and measurable.

This design ensures:
* Accountability
* Transparency
* Responsible AI usage
* Governance compliance


### 7. Monitoring & Governance
Override Rate

override_rate = (AI ≠ Human decisions) / Total reviewed tickets
This metric measures alignment between model predictions and human decisions.
The system maintains:
* Full audit logs
* Prediction history
* Human review records
* Workflow transparency
* Model version tracking

#### 8. Project Structure
municipality-ai-system/
│
├── backend/
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── ml/
│   ├── priority_model.pkl
│   └── vectorizer.pkl
│
├── .gitignore
├── docker-compose.yml
└── README.md

### 9. Installation

Install required dependencies:
pip install fastapi uvicorn streamlit scikit-learn joblib

### 10. Running the System
All commands should be executed from the project root:

C:\Users\nazis\Desktop\municipality-ai-system
### Start Backend
uvicorn backend.main:app --reload

### Swagger documentation:

http://127.0.0.1:8000/docs
#### Start Frontend
Open a new terminal and run:
streamlit run frontend/app.py
Streamlit will open at:

http://localhost:8501

#### 11. API Overview
### System
GET /health
### Tickets

POST /tickets
GET /tickets/inbox
GET /tickets/{ticket_id}
DELETE /tickets/{ticket_id}

### ML

POST /tickets/{ticket_id}/predict

### Review

POST /tickets/{ticket_id}/review

### Workflow

PATCH /tickets/{ticket_id}/status

### Metrics

GET /metrics/override_rate
GET /metrics/review_audit

### 12. Non-Functional Requirements

The system addresses:
* Reliability (transaction-based database operations)
* Transparency (confidence visibility)
* Traceability (audit logging)
* Maintainability (modular architecture)
* Governance (mandatory human validation)

### 13. Limitations

* Prototype-level deployment
* SQLite database (not distributed)
* No authentication layer
* No automated retraining pipeline
* No drift detection mechanism

###14. Future Improvements
    
* JWT authentication
* Role-based access control
* Model drift monitoring
* Automated retraining
* Cloud deployment
* Docker containerization
* Real-time analytics dashboard

### 15. Academic Relevance

This project demonstrates:
* Supervised learning integration
* RESTful AI system architecture
* Human-centered AI design
* Workflow engineering
* Monitoring and governance metrics
* End-to-end AI system deployment

It reflects AI Systems Engineering principles by integrating modeling, architecture, decision control, and system-level monitoring within a unified operational framework.

