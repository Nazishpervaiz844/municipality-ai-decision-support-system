## Municipality AI Decision Support System
## AI Systems Engineering – Innovation Project

## Author: Nazish Pervaiz Gill
Master’s in Data Science
University of Naples Federico II

## 1. Abstract

This project presents a production-style AI-assisted municipal complaint prioritization system integrating supervised machine learning within an operational decision workflow.
The system processes free-text citizen complaints, generates priority predictions (LOW, MEDIUM, HIGH), and embeds them inside a controlled human-in-the-loop validation pipeline. Final decisions remain under human authority, ensuring governance, accountability, and responsible AI deployment.
The contribution of this project is not merely a classifier, but a fully integrated AI system including:

* RESTful backend architecture
* Database-backed inference pipeline
* Workflow state management
* Human override mechanisms
* Governance metrics and audit logging
* Reproducible demo deployment

## 3. System Objectives
The system aims to:
1. Process unstructured complaint text
2. Automatically classify complaint priority
3. Provide probabilistic confidence estimates
4. Enable human validation and override
5. Track ticket lifecycle through structured states
6. Monitor model reliability using override metrics
7. Provide a reproducible full-stack demo

4. System Architecture

Citizen Portal (Streamlit)
↓
FastAPI Backend (REST API Layer)
↓
SQLite Database
↓
Machine Learning Model (TF-IDF + Logistic Regression)

The architecture follows a layered separation of concerns:

Presentation layer (frontend)
API/business logic layer (backend)
Data persistence layer (database)
ML inference module

The ML component is embedded within a REST architecture and is not isolated as a standalone script.

## 5. Core Components
## 5.1 Frontend (Streamlit)
Two operational interfaces:

### Citizen Portal
* Submit complaint
* Automatic AI prediction
* Track ticket progress
* View workflow state

### Office Portal
* Ticket inbox
* Run prediction manually
* Validate or override AI output
* Update workflow status
* Monitor override rate and audit table
* The frontend consumes backend APIs and contains no ML logic.

## 5.2 Backend (FastAPI)
The backend exposes structured REST endpoints grouped into domains:
* System
* Tickets
* ML
* Review
* Workflow
* Metrics

### Responsibilities:
* Ticket creation
* Model inference
* Human review handling
* Workflow state transitions
* Metric computation
* Audit trail management
* Swagger documentation is available for interactive testing.

### 5.3 Database (SQLite)

Three primary tables:
Tickets
Stores complaint data and workflow status.
Predictions

### Stores AI outputs including:
Predicted label
Confidence score
Model version
Timestamp
Reviews

### Stores human validation decisions including:

Final label
Reviewer ID
Timestamp
Optional comment

This structure ensures traceability and reproducibility.

## 6. Machine Learning Component
Model Choice
TF-IDF Vectorization
Logistic Regression Classifier

### Reasons for selection:
Efficient for sparse text data
Fast inference
Probabilistic output via predict_proba
Suitable for production-level deployment
Interpretable and lightweight

The ML model transforms unstructured complaint text into structured priority signals.

### Example Output
{
  "ticket_id": 1,
  "predicted_label": "HIGH",
  "confidence": 0.87
}

Confidence values support risk-aware human oversight.

## 7. Human-in-the-Loop Design

The system enforces a controlled decision pipeline:

NEW
→ REVIEWED
→ IN_PROGRESS
→ COMPLETED

AI predictions are advisory only.

Human reviewers must validate or override the prediction before workflow progression.

Overrides are explicitly recorded and measurable.

This ensures:
Accountability
Transparency
Responsible AI usage
Governance compliance

### 8. Monitoring & Governance
Override Rate

override_rate= (AI ≠Human) / Total Reviewed

This metric measures alignment between model predictions and human decisions.

The system maintains:
* Full audit logs
* Prediction history
* Human review records
* Workflow transparency
* Model version tracking

** 9. Project Structure
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
10. Installation

** Install required dependencies:

pip install fastapi uvicorn streamlit scikit-learn joblib
11. Running the System
All commands should be executed from the project root:

C:\Users\nazis\Desktop\municipality-ai-system
* Start Backend
uvicorn backend.main:app --reload

Swagger documentation:

http://127.0.0.1:8000/docs
* Start Frontend

Open a new terminal and run: 
cd frontend
streamlit run app.py

Streamlit will open at:

http://localhost:8501

### 12. API Overview
System
GET /health

Tickets

POST /tickets
GET /tickets/inbox
GET /tickets/{ticket_id}
DELETE /tickets/{ticket_id}

ML

POST /tickets/{ticket_id}/predict

Review

POST /tickets/{ticket_id}/review

Workflow

PATCH /tickets/{ticket_id}/status

Metrics

GET /metrics/override_rate
GET /metrics/review_audit

13. Non-Functional Requirements

The system addresses:

Reliability (transaction-based DB operations)

Transparency (confidence visibility)

Traceability (audit logs)

Maintainability (modular architecture)

Governance (mandatory human validation)

14. Limitations

Prototype-level deployment

SQLite database (not distributed)

No authentication layer

No automated retraining pipeline

No drift detection

15. Future Improvements

JWT authentication

Role-based access control

Model drift monitoring

Automated retraining

Cloud deployment

Docker containerization

Real-time analytics dashboard

### 16. Academic Relevance

This project demonstrates:
* Supervised learning integration
* RESTful AI system architecture
* Human-centered AI design
* Workflow engineering
* Monitoring and governance metrics
* End-to-end AI system deployment
  
It reflects AI Systems Engineering principles by integrating modeling, architecture, decision control, and system-level monitoring within a unified operational framework.
