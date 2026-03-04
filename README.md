## Municipality AI Decision Support System
## AI Systems Engineering Project
Nazish Pervaiz Gill
D03000191
Course: AI Systems Engineering
Exam Session: March 13
GitHub Link : https://github.com/Nazishpervaiz844/municipality-ai-decision-support-system
University of Naples Federico II

## Abstract

This project presents an AI-assisted municipal complaint management system integrating machine learning within an operational decision workflow. The system classifies free-text citizen complaints into priority levels (LOW, MEDIUM, HIGH) using a supervised learning model and incorporates human validation to ensure accountability, governance, and reliability.

The architecture demonstrates end-to-end AI system integration, including model inference, human-in-the-loop validation, workflow orchestration, and performance monitoring.

## Objective

To design and implement a production-style AI-enabled decision support system that:

Processes unstructured textual input

Performs automated priority classification

Integrates human oversight

Tracks workflow states

Monitors model reliability through override metrics

## System Architecture

Citizen Portal (Streamlit)
↓
FastAPI Backend (REST API)
↓
SQLite Database
↓
Machine Learning Model (TF-IDF + Logistic Regression)

The ML component is embedded within a structured REST architecture, not isolated as a standalone script.

## AI Component
## Model

TF-IDF vectorization

Logistic Regression classifier

Probabilistic output via predict_proba

Output

Predicted priority label

Confidence score

Model version tracking

This transforms unstructured complaint text into structured decision support signals.

Run the System
# Start Backend
uvicorn backend.main:app --reload

Open Swagger UI:

http://127.0.0.1:8000/docs
# Start Frontend
cd frontend
streamlit run app.py

## API Endpoints
System

GET /health

# Tickets

POST /tickets

GET /tickets/inbox

GET /tickets/{ticket_id}

DELETE /tickets/{ticket_id}

# ML

POST /tickets/{ticket_id}/predict


# Review

POST /tickets/{ticket_id}/review

# Workflow

PATCH /tickets/{ticket_id}/status

# Metrics

GET /metrics/override_rate

GET /metrics/review_audit

### Example ML Output
{
  "ticket_id": 1,
  "predicted_label": "HIGH",
  "confidence": 0.87
}

## Human-in-the-Loop Design

The system enforces a controlled decision pipeline:

NEW → REVIEWED → IN_PROGRESS → COMPLETED

AI output is advisory only.

Municipal staff validate or override predictions.

Overrides are recorded and measurable.

Governance metrics are computed (override rate).

This ensures responsible AI deployment.

### Monitoring & Governance

 ### Override Rate:

override_rate = (AI ≠ Human decisions) / total reviewed tickets

This metric evaluates alignment between model predictions and human decisions.

### The system maintains:

Full audit trail

Prediction history

Human review records

Workflow transparency

Technical Stack

FastAPI (Backend)

Streamlit (Frontend)

SQLite (Database)

Scikit-learn (ML)

Joblib (Model serialization)

Academic Relevance

### This project demonstrates:

Applied supervised learning for text classification

AI system integration within operational workflows

Human-centered AI architecture

Model monitoring and governance design

RESTful API engineering

Database-backed AI inference pipelines

It aligns with AI Systems Engineering principles by integrating modeling, system architecture, decision control, and performance evaluation within a unified framework.

### Author

Nazish Pervaiz Gill
Master’s in Data Science
University of Naples Federico II

