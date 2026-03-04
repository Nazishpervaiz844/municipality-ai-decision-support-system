### Municipality AI Decision Support System
### AI Systems Engineering – Innovation Project

Author: Nazish Pervaiz Gill
Master’s in Data Science
University of Naples Federico II

### Project Overview
This project implements an AI-assisted municipal complaint prioritization system that helps local administrations manage citizen complaints efficiently.
The system processes free-text complaints submitted by citizens and automatically predicts a priority level (LOW, MEDIUM, HIGH) using a machine learning model based on TF-IDF vectorization and Logistic Regression.
The prediction is integrated into a human-in-the-loop decision workflow, where municipal staff review and confirm or override the AI suggestion before the complaint proceeds through the operational workflow.
This design demonstrates how machine learning can be embedded into a real-world decision support system while maintaining transparency, accountability, and governance.

### System Architecture
The system follows a layered architecture typical for production AI applications.

Citizen Portal (Streamlit)
        ↓
FastAPI Backend (REST API)
        ↓
SQLite Database
        ↓
Machine Learning Model
(TF-IDF + Logistic Regression)
Components

#### Frontend
Built using Streamlit
Citizen portal for submitting complaints
Office portal for reviewing and validating AI predictions

#### Backend
Built with FastAPI
Handles ticket creation, prediction, workflow updates, and metrics

#### Database
SQLite database storing complaints, predictions, and reviews

#### Machine Learning Module
TF-IDF feature extraction

Logistic Regression classifier

Saved model artifacts used by the backend for inference

#### Key Features

* Citizen complaint submission interface
* Automatic AI-based priority prediction
* Prediction confidence score
* Human validation and override capability
* Structured ticket workflow management
* Monitoring metrics (override rate)
* REST API architecture
* Reproducible machine learning training pipeline

#### Dataset

Dataset file:

ml/municipal_complaints_200_with_titles.csv

#### Dataset characteristics:
* 200 labeled municipal complaints
* Balanced priority classes

#### Text fields:
* complaint_title
* complaint_description
* category

#### Target label:
priority (LOW / MEDIUM / HIGH)

#### Training input combines:
category + complaint_title + complaint_description

This provides richer contextual information for classification.

### Machine Learning Model
#### Feature Extraction

TF-IDF (Term Frequency – Inverse Document Frequency)

#### Classifier

Logistic Regression

The model transforms complaint text into numerical features and predicts the most likely priority category.

Example prediction output:

{
  "ticket_id": 4,
  "predicted_label": "HIGH",
  "confidence": 0.48
}
#### Model Training

Training script:

ml/train_model.py

##### Training pipeline:
* Load complaint dataset
* Combine category, title, and description
* Perform stratified 80/20 train-test split
* Convert text into TF-IDF feature vectors
* Train Logistic Regression classifier
* Evaluate model performance
* Save trained model artifacts

##### Saved artifacts:
ml/priority_model.pkl
ml/vectorizer.pkl

These files are loaded by the backend for runtime prediction.

### Model Evaluation
Evaluation metrics used:
* Accuracy
* Precision
* Recall
* F1-score
* Confusion Matrix

Model performance on test set:

Accuracy: 92.5%

Evaluation artifacts:

ml/outputs/classification_report.txt
ml/outputs/confusion_matrix.png

#### Human-in-the-Loop Workflow

The system implements a structured complaint lifecycle:

NEW → REVIEWED → IN_PROGRESS → COMPLETED

AI predictions are advisory only.
Municipal staff must validate or override the prediction before the complaint progresses through the workflow.
Overrides are recorded for transparency and monitoring.

#### Monitoring and Governance

The system calculates an Override Rate:

override_rate = (AI predictions overridden by humans) / total reviewed tickets

This metric helps monitor:

* AI reliability
* human disagreement with predictions
* potential model drift

*** Project Structure
municipality-ai-system
│
├── backend
│   ├── main.py
│   ├── municipality.db
│   └── requirements.txt
│
├── frontend
│   ├── app.py
│   └── requirements.txt
│
├── ml
│   ├── municipal_complaints_200_with_titles.csv
│   ├── train_model.py
│   ├── priority_model.pkl
│   ├── vectorizer.pkl
│   └── outputs
│       ├── classification_report.txt
│       └── confusion_matrix.png
│
├── docker-compose.yml
├── .gitignore
└── README.md

*** Installation

***** Install required dependencies:

pip install fastapi uvicorn streamlit scikit-learn pandas joblib matplotlib

***** Running the System

Run commands from project root:

municipality-ai-system
*****Start Backend
uvicorn backend.main:app --reload

Swagger API documentation:

http://127.0.0.1:8000/docs
*****Start Frontend

Open a new terminal and run:

streamlit run frontend/app.py

Application will open at:

http://localhost:8501

***** API Endpoints

****** System

GET /health

****** Tickets

POST /tickets
GET /tickets/inbox
GET /tickets/{ticket_id}
DELETE /tickets/{ticket_id}

****** Machine Learning

POST /tickets/{ticket_id}/predict

****** Review

POST /tickets/{ticket_id}/review

****** Workflow

PATCH /tickets/{ticket_id}/status

****** Metrics

GET /metrics/override_rate
GET /metrics/review_audit

***** Ethical Considerations
AI-based prioritization must consider:

* fairness in complaint handling
* transparency of decision support
* accountability for final decisions
* human oversight
The system mitigates these concerns through:

* mandatory human validation
* visible confidence scores
* override monitoring
* audit logging

**** Future Improvements

Possible extensions include:
* authentication and role-based access
* automated model retraining pipeline
* model drift detection
* cloud deployment
* analytics dashboard
* multilingual complaint support

**** Academic Context
This project was developed for the AI Systems Engineering course and demonstrates how machine learning models can be integrated into operational decision support systems.
The project covers:
* data preparation
* model training
* evaluation
* system architecture
* backend integration
* human-centered AI governance

**** Author

Nazish Pervaiz Gill
Master’s in Data Science
University of Naples Federico II

**** License

Academic project for educational purposes.
