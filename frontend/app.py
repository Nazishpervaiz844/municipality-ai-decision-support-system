import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

TITLES = [
    "Water leakage / pipe burst",
    "Sewage overflow / bad drainage",
    "Flooding after rain / blocked drains",
    "Road pothole / surface damage",
    "Road collapse / sinkhole",
    "Bridge / wall structural damage",
    "Street light not working",
    "Street light flickering / low visibility",
    "Traffic light malfunction",
    "Missing / damaged traffic sign",
    "Accident risk hazard on road",
    "Illegal dumping / waste on street",
    "Garbage collection missed / delayed",
    "Overflowing bins / dirty public area",
    "Public property damage (bench, fence, playground)",
    "Vandalism / graffiti",
    "Noise complaint (construction/event/neighbors)",
    "Fallen tree / blocked sidewalk",
    "Stray animals causing disturbance",
    "Safety hazard (gas smell / exposed wires / sparks)",
    "Other (custom title)",
]


# ----------------------------
# Helpers
# ----------------------------
def safe_get_json(url: str):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def safe_post_json(url: str, payload=None):
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def safe_patch_json(url: str, payload=None):
    r = requests.patch(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def confidence_badge(conf_value):
    """Returns: (emoji, pct_int, level_text)"""
    if conf_value is None:
        return "—", None, "Confidence unavailable"

    conf_float = float(conf_value)
    pct = int(round(conf_float * 100))

    if conf_float < 0.55:
        return "🟥", pct, "Low confidence"
    if conf_float < 0.70:
        return "🟨", pct, "Medium confidence"
    return "🟩", pct, "High confidence"


def status_badge(status: str):
    s = (status or "").upper().strip()
    if s == "NEW":
        return "🆕 NEW — Received by municipality"
    if s == "REVIEWED":
        return "✅ REVIEWED — Priority validated by staff"
    if s == "IN_PROGRESS":
        return "🛠️ IN_PROGRESS — Assigned / being handled"
    if s == "COMPLETED":
        return "🏁 COMPLETED — Resolved / closed"
    return f"ℹ️ {status}"


def citizen_next_step_text(status: str):
    s = (status or "").upper().strip()
    if s == "NEW":
        return "Next: A municipal clerk will review and validate priority."
    if s == "REVIEWED":
        return "Next: The case will be assigned to a team (IN_PROGRESS)."
    if s == "IN_PROGRESS":
        return "Work is ongoing. Next: COMPLETED when resolved."
    if s == "COMPLETED":
        return "This ticket is closed. If the issue persists, create a new ticket."
    return ""


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Municipality AI System", layout="wide")
st.title("Municipality AI Decision Support System")

tab1, tab2 = st.tabs(["👤 Citizen Portal", "🏛️ Office Portal"])


# ============================
# Citizen Portal
# ============================
with tab1:
    st.subheader("Submit a Complaint")
    st.caption("Citizen submits → system proposes priority → staff validates → progress until completion.")

    left, right = st.columns([2, 1])

    with left:
        title_choice = st.selectbox("Complaint category (title)", TITLES)

        custom_title = ""
        if title_choice == "Other (custom title)":
            custom_title = st.text_input(
                "Custom title (required)",
                placeholder="e.g., Broken water tap in public park",
            )

        final_title = custom_title.strip() if title_choice == "Other (custom title)" else title_choice

        desc = st.text_area(
            "Complaint description",
            height=160,
            placeholder="Explain what happened. Include where it happened and why it is urgent.",
        )

    with right:
        st.markdown("**Location (routing info)**")
        area = st.text_input("Area / Neighborhood", placeholder="e.g., San Giovanni, Fuorigrotta")
        address = st.text_input("Street / Landmark (optional)", placeholder="e.g., Via Roma 10, near bus stop")

        st.markdown("**Citizen perceived urgency (optional)**")
        urgency = st.selectbox("Urgency", ["LOW", "MEDIUM", "HIGH"], index=1)

        st.markdown("**Contact (optional)**")
        contact = st.text_input("Phone/Email (optional)", placeholder="For follow-up")

    st.divider()

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        submit = st.button("✅ Submit Complaint", type="primary")
    with c2:
        auto_predict_after_submit = st.checkbox("Auto-run AI prediction (demo)", value=True)

    if submit:
        if title_choice == "Other (custom title)" and not final_title:
            st.error("Please write a custom title.")
        elif not desc.strip():
            st.error("Please write a description.")
        elif not area.strip():
            st.error("Area/Neighborhood is required for routing.")
        else:
            enriched_desc = (
                f"{desc.strip()}\n\n"
                f"[METADATA] area={area.strip()} | address={address.strip()} | "
                f"urgency={urgency} | contact={contact.strip()}"
            )

            try:
                out = safe_post_json(
                    f"{API_BASE}/tickets",
                    payload={"complaint_title": final_title, "complaint_description": enriched_desc},
                )
                ticket_id = out["ticket_id"]
                st.success(f"Complaint submitted successfully. Ticket ID: {ticket_id}")

                if auto_predict_after_submit:
                    try:
                        pr = safe_post_json(f"{API_BASE}/tickets/{ticket_id}/predict")
                        predicted_label = pr.get("predicted_label")
                        conf = pr.get("confidence")
                        emoji, pct, level = confidence_badge(conf)

                        with st.expander("🔧 Internal system estimate (demo)", expanded=False):
                            if pct is None:
                                st.info(f"AI suggested: **{predicted_label}** — {level}")
                            else:
                                st.write(f"AI suggested priority: **{predicted_label}**")
                                st.write(f"Confidence: **{pct}%** ({level}) {emoji}")
                                st.caption("Internal estimate to help staff. Official priority is validated by municipality staff.")
                    except Exception as e:
                        st.warning(f"Ticket created, but prediction failed: {e}")

            except Exception as e:
                st.error(f"Error submitting complaint: {e}")

    st.divider()

    st.subheader("Track your Ticket (Demo)")
    st.caption("Citizen sees progress + official municipality update. Internal estimate is hidden by default.")

    track_id = st.number_input("Ticket ID", min_value=1, step=1, value=1)
    if st.button("🔎 Check Status"):
        try:
            t = safe_get_json(f"{API_BASE}/tickets/{int(track_id)}")

            st.write(f"**Title:** {t.get('complaint_title')}")
            st.write(f"**Created at:** {t.get('created_at')}")
            st.markdown(f"**Workflow status:** {status_badge(t.get('status'))}")

            next_step = citizen_next_step_text(t.get("status"))
            if next_step:
                st.caption(next_step)

            st.divider()
            st.markdown("### 🏛️ Municipality Update")

            status_now = (t.get("status") or "").upper().strip()
            final_label = t.get("final_label")
            reviewed_at = t.get("reviewed_at")

            if status_now in {"REVIEWED", "IN_PROGRESS", "COMPLETED"} and final_label:
                st.success(f"**Official priority:** {final_label}")
                st.caption(f"Validated by municipality staff • {reviewed_at}")
            else:
                st.info("Priority will be assigned after municipal review.")

            # Optional internal estimate (for professor)
            with st.expander("🔧 Internal system estimate (demo / transparency)", expanded=False):
                pred_label = t.get("predicted_label")
                conf = t.get("confidence")
                if pred_label and conf is not None:
                    emoji, pct, level = confidence_badge(conf)
                    st.write(f"AI suggested priority: **{pred_label}**")
                    st.write(f"Confidence: **{pct}%** ({level}) {emoji}")
                else:
                    st.write("No AI prediction recorded yet.")

        except Exception as e:
            st.error(f"Could not load ticket: {e}")


# ============================
# Office Portal
# ============================
with tab2:
    st.subheader("Office Inbox (Human-in-the-Loop)")

    # Metrics
    try:
        m = safe_get_json(f"{API_BASE}/metrics/override_rate")
        total_reviewed = m.get("total_reviewed", 0)
        overrides = m.get("overrides", 0)
        rate = m.get("override_rate", 0.0)

        k1, k2, k3 = st.columns(3)
        k1.metric("Reviewed tickets", total_reviewed)
        k2.metric("Overrides", overrides)
        k3.metric("Override rate", f"{rate * 100:.1f}%")
    except Exception:
        st.info("Metrics not available yet (run some predictions + reviews).")

    # Override Audit
    st.markdown("### Override Audit (Which tickets were overridden?)")
    try:
        audit = safe_get_json(f"{API_BASE}/metrics/review_audit")

        if not audit:
            st.info("No reviewed tickets with predictions yet.")
        else:
            filter_choice = st.selectbox("Filter audit table", ["Overrides", "Confirmed", "All"], index=0)

            cleaned = []
            for a in audit:
                is_over = bool(a.get("is_override"))
                result = "✅ Override" if is_over else "— Confirmed"

                emoji, pct, _ = confidence_badge(a.get("confidence"))
                conf_pct = f"{pct}%" if pct is not None else ""

                cleaned.append(
                    {
                        "Ticket": a.get("ticket_id"),
                        "Title": a.get("complaint_title"),
                        "AI": a.get("predicted_label"),
                        "Confidence": emoji,
                        "Confidence (%)": conf_pct,
                        "Human": a.get("final_label"),
                        "Result": result,
                        "Reviewer": a.get("reviewer"),
                        "Reviewed At": a.get("reviewed_at"),
                    }
                )

            overrides_only = [r for r in cleaned if r["Result"] == "✅ Override"]
            confirmed_only = [r for r in cleaned if r["Result"] == "— Confirmed"]

            if filter_choice == "All":
                st.dataframe(cleaned, width= "stretch", hide_index=True)
            elif filter_choice == "Overrides":
                if overrides_only:
                    st.error(f"Overrides detected: {len(overrides_only)}")
                    st.dataframe(overrides_only, width= "stretch", hide_index=True)
                else:
                    st.success("No overrides so far.")
            else:  # Confirmed
                if confirmed_only:
                    st.success(f"Confirmed predictions: {len(confirmed_only)}")
                    st.dataframe(confirmed_only, width= "stretch", hide_index=True)
                else:
                    st.info("No confirmed predictions yet.")

    except Exception as e:
        st.warning(f"Could not load review audit: {e}")

    st.divider()

    # Controls
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("🔄 Refresh Inbox")  # reruns app
    with col2:
        auto_predict = st.checkbox("Auto-run prediction when selected", value=True)

    # Inbox
    try:
        inbox = safe_get_json(f"{API_BASE}/tickets/inbox")
    except Exception as e:
        st.error(f"Could not load inbox: {e}")
        inbox = []

    if not inbox:
        st.info("No tickets yet. Submit one from Citizen Portal.")
    else:
        options = [f"#{t['ticket_id']} — {t['complaint_title']} — status: {t['status']}" for t in inbox]
        selected = st.selectbox("Select a ticket to review", options)
        selected_id = int(selected.split("—")[0].strip().replace("#", ""))

        ticket = next((t for t in inbox if int(t.get("ticket_id")) == int(selected_id)), None)

        if not ticket:
            st.warning("Ticket not found.")
        else:
            st.markdown("### Ticket Details")
            st.write(f"**Ticket ID:** {ticket.get('ticket_id')}")
            st.write(f"**Title:** {ticket.get('complaint_title')}")
            st.write(f"**Created at:** {ticket.get('created_at')}")
            st.write(f"**Status:** {ticket.get('status')}")

            predicted_label = ticket.get("predicted_label")
            confidence = ticket.get("confidence")

            run_pred = st.button("🤖 Run Prediction")
            if auto_predict and predicted_label is None:
                run_pred = True

            if run_pred:
                try:
                    out = safe_post_json(f"{API_BASE}/tickets/{selected_id}/predict")
                    predicted_label = out.get("predicted_label")
                    confidence = out.get("confidence")
                except Exception as e:
                    st.error(f"Prediction failed: {e}")

            st.divider()
            st.markdown("### AI Prediction")
            if predicted_label is None:
                st.warning("No prediction yet.")
            else:
                emoji, pct, level = confidence_badge(confidence)
                if emoji == "🟥":
                    st.warning(f"{emoji} {predicted_label} — {pct}% ({level})")
                elif emoji == "🟨":
                    st.info(f"{emoji} {predicted_label} — {pct}% ({level})")
                else:
                    st.success(f"{emoji} {predicted_label} — {pct}% ({level})")

            st.divider()
            st.markdown("### Human Validation (Clerk Review)")

            index_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
            default_index = index_map.get(predicted_label, 1)

            final_label = st.selectbox(
                "Final priority (human decision)",
                ["LOW", "MEDIUM", "HIGH"],
                index=default_index,
                key="final_label_select",
            )
            reviewer = st.text_input("Reviewer ID", value="clerk_1", key="reviewer_input")
            comment = st.text_input("Comment (optional)", value="", key="comment_input")

            if st.button("✅ Submit Review", type="primary"):
                try:
                    safe_post_json(
                        f"{API_BASE}/tickets/{selected_id}/review",
                        payload={
                            "final_label": final_label,
                            "reviewer": reviewer,
                            "comment": comment if comment.strip() else None,
                        },
                    )
                    st.success("Review saved. Ticket marked as REVIEWED.")
                except Exception as e:
                    st.error(f"Review failed: {e}")

            st.divider()
            st.markdown("### Workflow Status Update (Office)")
            current_status = (ticket.get("status") or "").upper().strip()

            next_status_map = {
                "NEW": "REVIEWED",
                "REVIEWED": "IN_PROGRESS",
                "IN_PROGRESS": "COMPLETED",
                "COMPLETED": "COMPLETED",
            }
            suggested_next = next_status_map.get(current_status, "REVIEWED")

            statuses = ["NEW", "REVIEWED", "IN_PROGRESS", "COMPLETED"]

            colS1, colS2, colS3 = st.columns([1, 1, 2])
            with colS1:
                new_status = st.selectbox(
                    "Set status",
                    statuses,
                    index=statuses.index(suggested_next),
                    key="status_select",
                )
            with colS2:
                update_status_btn = st.button("🛠️ Update Status", key="update_status_btn")
            with colS3:
                st.caption("Use after review: REVIEWED → IN_PROGRESS → COMPLETED")

            if update_status_btn:
                try:
                    safe_patch_json(
                        f"{API_BASE}/tickets/{selected_id}/status",
                        payload={"status": new_status},
                    )
                    st.success(f"Status updated to: **{new_status}**")
                    st.info("Click Refresh Inbox (or any interaction) to reload the updated status.")
                except Exception as e:
                    st.error(f"Status update failed: {e}")
