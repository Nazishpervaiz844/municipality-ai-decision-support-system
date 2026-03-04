import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt


# ----------------------------
# Config
# ----------------------------
LABEL_COL = "priority"
TITLE_COL = "complaint_title"
DESC_COL = "complaint_description"

MODEL_VERSION = "v1-tfidf-logreg"
LABELS_ORDER = ["LOW", "MEDIUM", "HIGH"]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(PROJECT_ROOT, "ml")
DATA_PATH = os.path.join(ML_DIR, "municipal_complaints_200_with_titles.csv")
REPORT_DIR = os.path.join(ML_DIR, "outputs")

os.makedirs(ML_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ----------------------------
# Load + checks
# ----------------------------
df = pd.read_csv(DATA_PATH)

required_cols = {TITLE_COL, DESC_COL, LABEL_COL, "category"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns in CSV: {missing}")

df[TITLE_COL] = df[TITLE_COL].fillna("")
df[DESC_COL] = df[DESC_COL].fillna("")
df["category"] = df["category"].fillna("")

df[LABEL_COL] = df[LABEL_COL].astype(str).str.upper().str.strip()

df["combined_text"] = (
    df["category"].astype(str).str.strip()
    + " "
    + df[TITLE_COL]
    + " "
    + df[DESC_COL]
).str.strip()

print("=== Dataset Summary ===")
print("Rows:", len(df))
print("Label distribution:\n", df[LABEL_COL].value_counts())
print()


# ----------------------------
# Split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    df["combined_text"],
    df[LABEL_COL],
    test_size=0.2,
    random_state=42,
    stratify=df[LABEL_COL],
)

print("Train size:", len(X_train), "| Test size:", len(X_test))
print()


# ----------------------------
# Vectorize
# ----------------------------
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=20000
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("TF-IDF train matrix shape:", X_train_vec.shape)
print()


# ----------------------------
# Train model
# ----------------------------
model = LogisticRegression(max_iter=2000)
model.fit(X_train_vec, y_train)


# ----------------------------
# Evaluate
# ----------------------------
y_pred = model.predict(X_test_vec)

report_text = classification_report(y_test, y_pred, digits=4)
cm = confusion_matrix(y_test, y_pred, labels=LABELS_ORDER)

print("=== Classification Report ===")
print(report_text)
print("=== Confusion Matrix ===")
print(cm)
print()

# Save report text
report_path = os.path.join(REPORT_DIR, "classification_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("Model Version: " + MODEL_VERSION + "\n\n")
    f.write("Dataset: " + DATA_PATH + "\n")
    f.write("Train/Test split: 80/20 | random_state=42 | stratified\n\n")
    f.write("Classification Report:\n")
    f.write(report_text + "\n\n")
    f.write("Confusion Matrix (rows=true, cols=pred):\n")
    f.write(str(cm))

print("Saved classification report to:", report_path)

# Save confusion matrix figure
fig_path = os.path.join(REPORT_DIR, "confusion_matrix.png")

plt.figure(figsize=(6, 5))
plt.imshow(cm, interpolation="nearest")
plt.title("Confusion Matrix")
plt.colorbar()

tick_marks = range(len(LABELS_ORDER))
plt.xticks(tick_marks, LABELS_ORDER, rotation=45)
plt.yticks(tick_marks, LABELS_ORDER)

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, str(cm[i, j]), ha="center", va="center")

plt.ylabel("True label")
plt.xlabel("Predicted label")
plt.tight_layout()
plt.savefig(fig_path, dpi=200)
plt.close()

print("Saved confusion matrix image to:", fig_path)


# ----------------------------
# Save model artefacts (for backend)
# ----------------------------
model_path = os.path.join(ML_DIR, "priority_model.pkl")
vec_path = os.path.join(ML_DIR, "vectorizer.pkl")

joblib.dump(model, model_path)
joblib.dump(vectorizer, vec_path)

print("\n✅ Model saved to:", model_path)
print("✅ Vectorizer saved to:", vec_path)
print("✅ Done.")