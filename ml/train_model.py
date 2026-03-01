import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load dataset
df = pd.read_csv("municipal_complaints_200_with_titles.csv")

# Combine title + description
df["combined_text"] = df["complaint_title"] + " " + df["complaint_description"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df["combined_text"], df["priority"],
    test_size=0.2,
    random_state=42,
    stratify=df["priority"]
)

# Vectorization
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)


# Evaluate
predictions = model.predict(X_test_vec)

print("\nClassification Report:\n")
print(classification_report(y_test, predictions))

# Save model + vectorizer
joblib.dump(model, "priority_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\nModel saved successfully.")
