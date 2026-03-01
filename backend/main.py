from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import sqlite3
from datetime import datetime
import joblib
import os
import traceback

# ============================================================
# App metadata (Swagger)
# ============================================================
app = FastAPI(
    title="Municipality AI System",
    description="AI-assisted municipal complaint prioritization with human-in-the-loop validation.",
    version="1.0.0",
)

# ============================================================
# Paths
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
ML_DIR = os.path.join(BASE_DIR, "ml")
DB_PATH = os.path.join(BASE_DIR, "backend", "municipality.db")

print("BASE_DIR =", BASE_DIR)
print("ML_DIR   =", ML_DIR)
print("DB_PATH  =", DB_PATH)

# ============================================================
# Load ML artifacts
# ============================================================
model = joblib.load(os.path.join(ML_DIR, "priority_model.pkl"))
vectorizer = joblib.load(os.path.join(ML_DIR, "vectorizer.pkl"))

print("MODEL TYPE:", type(model))
print("HAS predict_proba:", hasattr(model, "predict_proba"))

MODEL_VERSION = "v1-tfidf-logreg"

# ============================================================
# DB helpers
# ============================================================
def db_connect():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.execute("PRAGMA journal_mode=WAL;")  # helps avoid "database is locked"
    return con


def init_db():
    con = db_connect()
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets(
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_title TEXT NOT NULL,
            complaint_description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'NEW'
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions(
            pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            predicted_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            model_version TEXT NOT NULL,
            predicted_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews(
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            final_label TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            reviewed_at TEXT NOT NULL,
            comment TEXT,
            FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
        )
        """
    )

    con.commit()
    con.close()


init_db()

# ============================================================
# Schemas
# ============================================================
class TicketCreate(BaseModel):
    complaint_title: str
    complaint_description: str


class PredictOut(BaseModel):
    ticket_id: int
    predicted_label: str
    confidence: float


class ReviewCreate(BaseModel):
    final_label: Literal["LOW", "MEDIUM", "HIGH"]
    reviewer: str
    comment: Optional[str] = None


class TicketDetailsOut(BaseModel):
    ticket_id: int
    complaint_title: str
    complaint_description: str
    created_at: str
    status: Literal["NEW", "REVIEWED", "IN_PROGRESS", "COMPLETED"] | str

    # latest AI prediction
    predicted_label: Optional[str] = None
    confidence: Optional[float] = None
    predicted_at: Optional[str] = None

    # latest human review
    final_label: Optional[str] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_comment: Optional[str] = None


class StatusUpdate(BaseModel):
    status: Literal["NEW", "REVIEWED", "IN_PROGRESS", "COMPLETED"]


# ============================================================
# ML helper
# ============================================================
def predict_priority(title: str, desc: str):
    combined = (title + " " + desc).strip()
    X = vectorizer.transform([combined])

    # LogisticRegression supports predict_proba
    proba = model.predict_proba(X)[0]
    classes = list(model.classes_)
    best_idx = int(proba.argmax())

    return classes[best_idx], float(proba[best_idx])


# ============================================================
# Endpoints
# ============================================================
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}


# ----------------------------
# Tickets
# ----------------------------
@app.post("/tickets", tags=["Tickets"])
def create_ticket(req: TicketCreate):
    now = datetime.utcnow().isoformat()

    con = db_connect()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO tickets(complaint_title, complaint_description, created_at, status) VALUES(?,?,?,?)",
        (req.complaint_title, req.complaint_description, now, "NEW"),
    )
    ticket_id = cur.lastrowid

    con.commit()
    con.close()

    return {"ticket_id": ticket_id}


@app.get("/tickets/inbox", tags=["Tickets"])
def inbox():
    con = db_connect()
    cur = con.cursor()

    cur.execute(
        """
        SELECT t.ticket_id, t.complaint_title, t.created_at, t.status,
               p.predicted_label, p.confidence
        FROM tickets t
        LEFT JOIN (
            SELECT ticket_id, predicted_label, confidence
            FROM predictions
            WHERE pred_id IN (SELECT MAX(pred_id) FROM predictions GROUP BY ticket_id)
        ) p ON t.ticket_id = p.ticket_id
        ORDER BY t.ticket_id DESC
        """
    )
    rows = cur.fetchall()
    con.close()

    return [
        {
            "ticket_id": r[0],
            "complaint_title": r[1],
            "created_at": r[2],
            "status": r[3],
            "predicted_label": r[4],
            "confidence": r[5],
        }
        for r in rows
    ]


@app.get("/tickets/{ticket_id}", tags=["Tickets"], response_model=TicketDetailsOut)
def get_ticket(ticket_id: int):
    con = db_connect()
    cur = con.cursor()

    # ticket
    cur.execute(
        """
        SELECT ticket_id, complaint_title, complaint_description, created_at, status
        FROM tickets
        WHERE ticket_id=?
        """,
        (ticket_id,),
    )
    t = cur.fetchone()
    if not t:
        con.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    # latest prediction
    cur.execute(
        """
        SELECT predicted_label, confidence, predicted_at
        FROM predictions
        WHERE ticket_id=?
        ORDER BY pred_id DESC
        LIMIT 1
        """,
        (ticket_id,),
    )
    p = cur.fetchone()

    # latest review
    cur.execute(
        """
        SELECT final_label, reviewer, reviewed_at, comment
        FROM reviews
        WHERE ticket_id=?
        ORDER BY review_id DESC
        LIMIT 1
        """,
        (ticket_id,),
    )
    r = cur.fetchone()

    con.close()

    out = {
        "ticket_id": t[0],
        "complaint_title": t[1],
        "complaint_description": t[2],
        "created_at": t[3],
        "status": t[4],
    }

    if p:
        out.update({"predicted_label": p[0], "confidence": p[1], "predicted_at": p[2]})

    if r:
        out.update({"final_label": r[0], "reviewer": r[1], "reviewed_at": r[2], "review_comment": r[3]})

    return out


@app.delete("/tickets/{ticket_id}", tags=["Tickets"])
def delete_ticket(ticket_id: int):
    con = db_connect()
    cur = con.cursor()

    # ensure ticket exists (optional but clean)
    cur.execute("SELECT ticket_id FROM tickets WHERE ticket_id=?", (ticket_id,))
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    # delete related rows first (FK order)
    cur.execute("DELETE FROM reviews WHERE ticket_id=?", (ticket_id,))
    cur.execute("DELETE FROM predictions WHERE ticket_id=?", (ticket_id,))
    cur.execute("DELETE FROM tickets WHERE ticket_id=?", (ticket_id,))

    con.commit()
    con.close()

    return {"deleted_ticket_id": ticket_id}


# ----------------------------
# ML
# ----------------------------
@app.post("/tickets/{ticket_id}/predict", tags=["ML"], response_model=PredictOut)
def run_prediction(ticket_id: int):
    try:
        con = db_connect()
        cur = con.cursor()

        cur.execute(
            "SELECT complaint_title, complaint_description FROM tickets WHERE ticket_id=?",
            (ticket_id,),
        )
        row = cur.fetchone()

        if not row:
            con.close()
            raise HTTPException(status_code=404, detail="Ticket not found")

        title, desc = row
        label, conf = predict_priority(title, desc)

        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO predictions(ticket_id, predicted_label, confidence, model_version, predicted_at) VALUES(?,?,?,?,?)",
            (ticket_id, label, conf, MODEL_VERSION, now),
        )

        con.commit()
        con.close()

        return {"ticket_id": ticket_id, "predicted_label": label, "confidence": conf}

    except HTTPException:
        raise
    except Exception as e:
        print("PREDICT ERROR:", str(e))
        print(traceback.format_exc())
        raise


# ----------------------------
# Review
# ----------------------------
@app.post("/tickets/{ticket_id}/review", tags=["Review"])
def review(ticket_id: int, req: ReviewCreate):
    now = datetime.utcnow().isoformat()

    con = db_connect()
    cur = con.cursor()

    # ensure ticket exists
    cur.execute("SELECT ticket_id FROM tickets WHERE ticket_id=?", (ticket_id,))
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    cur.execute(
        "INSERT INTO reviews(ticket_id, final_label, reviewer, reviewed_at, comment) VALUES(?,?,?,?,?)",
        (ticket_id, req.final_label, req.reviewer, now, req.comment),
    )

    # after review -> status becomes REVIEWED
    cur.execute("UPDATE tickets SET status='REVIEWED' WHERE ticket_id=?", (ticket_id,))

    con.commit()
    con.close()

    return {"ticket_id": ticket_id, "final_label": req.final_label, "status": "REVIEWED"}


# ----------------------------
# Workflow
# ----------------------------
@app.patch("/tickets/{ticket_id}/status", tags=["Workflow"])
def update_ticket_status(ticket_id: int, req: StatusUpdate):
    con = db_connect()
    cur = con.cursor()

    cur.execute("SELECT status FROM tickets WHERE ticket_id=?", (ticket_id,))
    row = cur.fetchone()
    if not row:
        con.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    cur.execute("UPDATE tickets SET status=? WHERE ticket_id=?", (req.status, ticket_id))

    con.commit()
    con.close()

    return {"ticket_id": ticket_id, "status": req.status}


# ----------------------------
# Metrics
# ----------------------------
@app.get("/metrics/override_rate", tags=["Metrics"])
def override_rate():
    con = db_connect()
    cur = con.cursor()

    # Compare latest prediction vs latest review for each ticket
    cur.execute(
        """
        SELECT
            COUNT(*) as total_reviewed,
            SUM(CASE WHEN p.predicted_label != r.final_label THEN 1 ELSE 0 END) as overrides
        FROM reviews r
        JOIN (
            SELECT ticket_id, predicted_label
            FROM predictions
            WHERE pred_id IN (SELECT MAX(pred_id) FROM predictions GROUP BY ticket_id)
        ) p ON r.ticket_id = p.ticket_id
        """
    )
    row = cur.fetchone()
    con.close()

    total = int(row[0]) if row and row[0] is not None else 0
    overrides = int(row[1]) if row and row[1] is not None else 0
    rate = (overrides / total) if total > 0 else 0.0

    return {"total_reviewed": total, "overrides": overrides, "override_rate": rate}


@app.get("/metrics/review_audit", tags=["Metrics"])
def review_audit():
    con = db_connect()
    cur = con.cursor()

    cur.execute(
        """
        SELECT
            t.ticket_id,
            t.complaint_title,
            p.predicted_label,
            p.confidence,
            r.final_label,
            CASE WHEN p.predicted_label != r.final_label THEN 1 ELSE 0 END as is_override,
            r.reviewer,
            r.reviewed_at
        FROM tickets t
        JOIN (
            SELECT ticket_id, predicted_label, confidence
            FROM predictions
            WHERE pred_id IN (SELECT MAX(pred_id) FROM predictions GROUP BY ticket_id)
        ) p ON t.ticket_id = p.ticket_id
        JOIN (
            SELECT ticket_id, final_label, reviewer, reviewed_at
            FROM reviews
            WHERE review_id IN (SELECT MAX(review_id) FROM reviews GROUP BY ticket_id)
        ) r ON t.ticket_id = r.ticket_id
        ORDER BY r.reviewed_at DESC
        """
    )

    rows = cur.fetchall()
    con.close()

    return [
        {
            "ticket_id": row[0],
            "complaint_title": row[1],
            "predicted_label": row[2],
            "confidence": row[3],
            "final_label": row[4],
            "is_override": bool(row[5]),
            "reviewer": row[6],
            "reviewed_at": row[7],
        }
        for row in rows
    ]