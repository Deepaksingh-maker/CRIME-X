"""Alert Center management view for system and operational notifications."""

from __future__ import annotations

import streamlit as st

from src.ui.components import modern_kpi_card, page_header, records_table, section


def render(repository) -> None:
    page_header("Alert Dispatch Center", "Monitor, triage, and resolve real-time operational notifications", "ALERT RADAR ACTIVE")

    all_alerts = repository.get_alerts()
    unread_alerts = repository.get_alerts(unread_only=True)
    critical_alerts = [a for a in all_alerts if a.get("severity") in ("CRITICAL", "HIGH")]
    resolved_alerts = repository.get_alerts(status="RESOLVED")

    st.markdown(f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Total Dispatches", f"{len(all_alerts)}", "All Registered Events", "purple", "🚨")}
      {modern_kpi_card("Unread Alerts", f"{len(unread_alerts)}", "Requires Triage Action", "amber", "⚠️")}
      {modern_kpi_card("High / Critical", f"{len(critical_alerts)}", "Priority Threat Level", "red", "🔥")}
      {modern_kpi_card("Resolved", f"{len(resolved_alerts)}", "Addressed & Closed", "emerald", "🛡️")}
    </div>
    """, unsafe_allow_html=True)

    # 1. Alert Log Overview
    section("ACTIVE NOTIFICATIONS & INCIDENT DISPATCHES", icon="⚡")
    mode = st.segmented_control("Filter Alerts", ["Unread", "All", "Resolved"], default="Unread")

    if mode == "Unread":
        alerts = repository.get_alerts(unread_only=True)
    elif mode == "Resolved":
        alerts = repository.get_alerts(status="RESOLVED")
    else:
        alerts = repository.get_alerts()

    if alerts:
        display_alerts = [
            {
                "ID": f"#{a.get('id')}",
                "Type": a.get("alert_type"),
                "Severity": a.get("severity"),
                "Status": a.get("status", "UNREAD"),
                "Source": a.get("source") or "system",
                "Message": a.get("message"),
                "Timestamp": str(a.get("created_at"))[:19] if a.get("created_at") else "N/A",
            }
            for a in alerts
        ]
        records_table(display_alerts)

        st.write("")
        section("TRIAGE ACTIONS & INCIDENT RESOLUTION", icon="🎯")
        for alert in alerts[:8]:
            sev = alert.get("severity", "INFO")
            sev_color = {
                "CRITICAL": "#ef4444",
                "HIGH": "#f97316",
                "WARNING": "#f59e0b",
                "INFO": "#38bdf8",
            }.get(sev, "#94a3b8")

            col1, col2, col3 = st.columns([3.5, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(15,23,42,0.7), rgba(10,15,28,0.85)); border:1px solid rgba(255,255,255,0.08); border-left:3px solid {sev_color}; border-radius:10px; padding:10px 14px; margin-bottom:6px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; font-weight:700; color:{sev_color};">#{alert['id']} [{sev}]</span>
                        <span style="font-family:'Outfit', sans-serif; font-size:0.85rem; font-weight:600; color:#f8fafc;">{alert['alert_type']}</span>
                        <span style="margin-left:auto; font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#64748b;">{str(alert.get('created_at'))[:19] if alert.get('created_at') else ''}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#94a3b8; margin-top:4px;">{alert['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if not alert.get("is_read"):
                    if st.button("Mark Read", key=f"read_{alert['id']}"):
                        repository.mark_alert_read(alert["id"])
                        st.rerun()
                else:
                    st.caption(f"Status: {alert.get('status')}")
            with col3:
                if alert.get("status") != "RESOLVED":
                    if st.button("Resolve", key=f"resolve_{alert['id']}", type="primary"):
                        repository.resolve_alert(alert["id"])
                        st.success(f"Alert #{alert['id']} marked as RESOLVED.")
                        st.rerun()
                else:
                    st.caption("RESOLVED")
    else:
        st.info("No active alerts stored in SQLite database matching current filter.")

    # 2. Create Alert Form
    section("DISPATCH MANUAL BROADCAST ALERT", icon="📢")
    with st.form("create_alert"):
        c1, c2 = st.columns([1, 2])
        with c1:
            alert_type = st.selectbox("Alert Type", ["HIGH_RISK_DISTRICT", "SUSPICIOUS_ACTIVITY", "INVESTIGATION_DISPATCH", "FIRE_ALERT", "SYSTEM_WARNING"])
            severity = st.selectbox("Severity Level", ["INFO", "WARNING", "HIGH", "CRITICAL"], index=1)
        with c2:
            message = st.text_area("Alert Message / Dispatch Summary", placeholder="Enter official alert narrative...")
        submitted = st.form_submit_button("Broadcast Incident Alert", type="primary")

    if submitted:
        if alert_type.strip() and message.strip():
            repository.create_alert({
                "alert_type": alert_type.strip(),
                "severity": severity,
                "message": message.strip(),
                "source": "manual_dispatch",
                "status": "UNREAD",
                "is_read": False,
            })
            st.success("Alert registered in SQLite database.")
            st.rerun()
        else:
            st.error("Alert type and message narrative are required.")