"""Investigation management view for active case lifecycle."""

from __future__ import annotations

import streamlit as st

from src.ui.components import modern_kpi_card, page_header, records_table, section


def render(repository) -> None:
    page_header("Investigation Command Center", "Active case dossier management, evidence logging & status lifecycle", "CASE REGISTRY ACTIVE")

    total_cases = repository.count_investigations()
    open_cases = len(repository.list_investigations(status="OPEN"))
    investigating = len(repository.list_investigations(status="INVESTIGATING"))
    closed = len(repository.list_investigations(status="CLOSED"))

    # Quick Tactical Metrics
    st.markdown(f"""
    <div class="cx-kpi-grid">
      {modern_kpi_card("Total Registered", f"{total_cases}", "All Recorded Dossiers", "purple", "📁")}
      {modern_kpi_card("Open Cases", f"{open_cases}", "Pending Action", "amber", "⚠️")}
      {modern_kpi_card("Active Investigations", f"{investigating}", "In-Progress Field Operations", "cyan", "🔍")}
      {modern_kpi_card("Closed Dossiers", f"{closed}", "Resolved & Archived", "emerald", "✅")}
    </div>
    """, unsafe_allow_html=True)

    # 1. Active Cases Overview Table
    section("ACTIVE INVESTIGATIONS REPOSITORY", icon="📋")
    filter_col1, filter_col2 = st.columns([1.5, 2.5])
    with filter_col1:
        status_filter = st.selectbox("Filter by Status", ["All", "OPEN", "INVESTIGATING", "CLOSED"], index=0)
    with filter_col2:
        search_query = st.text_input("Search Cases", placeholder="Search by case ID, title, officer, or location...").strip()

    status_arg = None if status_filter == "All" else status_filter
    cases = repository.list_investigations(status=status_arg, search=search_query or None)

    if cases:
        display_cases = [
            {
                "Case ID": c.get("case_reference"),
                "Title": c.get("title"),
                "Status": c.get("status"),
                "Priority": c.get("priority"),
                "Type": c.get("case_type") or "Unspecified",
                "Location": c.get("location") or "Unspecified",
                "Officer": c.get("assigned_officer") or "Unassigned",
                "Created": str(c.get("created_at"))[:19] if c.get("created_at") else "N/A",
            }
            for c in cases
        ]
        records_table(display_cases)
    else:
        st.info("No active investigations stored in SQLite database matching current filters.")

    # 2. Create Investigation
    section("REGISTER NEW CASE DOSSIER", icon="➕")
    with st.form("create_investigation"):
        c1, c2, c3 = st.columns(3)
        with c1:
            reference = st.text_input("Case ID *", placeholder="e.g. CASE-2026-001")
        with c2:
            title = st.text_input("Case Title *", placeholder="Brief description of incident")
        with c3:
            priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=1)

        c4, c5, c6 = st.columns(3)
        with c4:
            case_type = st.selectbox("Case Type", ["Physical Crime", "Cybercrime", "Financial Fraud", "Homicide", "Theft/Burglary", "Other"])
        with c5:
            location = st.text_input("Location / Jurisdiction", placeholder="e.g. Ahmedabad City")
        with c6:
            assigned_officer = st.text_input("Assigned Officer", placeholder="e.g. Inspector R. Sharma")

        description = st.text_area("Initial Incident Description", placeholder="Enter case details and preliminary evidence summary...")
        submitted = st.form_submit_button("Create Case Dossier", type="primary")

    if submitted:
        if not reference.strip() or not title.strip():
            st.error("Case ID and Title are required fields.")
        else:
            try:
                repository.create_investigation({
                    "case_reference": reference.strip(),
                    "title": title.strip(),
                    "case_type": case_type,
                    "location": location.strip() if location else None,
                    "assigned_officer": assigned_officer.strip() if assigned_officer else None,
                    "priority": priority,
                    "description": description.strip() if description else None,
                    "status": "OPEN",
                })
                st.success(f"Investigation '{reference.strip()}' successfully registered in SQLite database.")
                st.rerun()
            except Exception as error:
                st.error(f"Failed to create investigation: {error}")

    # 3. Case Inspection & Lifecycle Management
    section("CASE INSPECTION & DOSSIER TIMELINE", icon="🔎")
    lookup = st.text_input("Enter Case ID to Inspect or Update", placeholder="e.g. CASE-2026-001").strip()
    if lookup:
        record = repository.get_investigation(lookup)
        if record:
            priority_color = {
                "CRITICAL": "#ef4444",
                "HIGH": "#f97316",
                "MEDIUM": "#f59e0b",
                "LOW": "#38bdf8",
            }.get(record.get("priority"), "#94a3b8")

            status_bg = {
                "OPEN": "rgba(56, 189, 248, 0.15)",
                "INVESTIGATING": "rgba(245, 158, 11, 0.15)",
                "CLOSED": "rgba(16, 185, 129, 0.15)",
            }.get(record.get("status"), "rgba(255,255,255,0.1)")

            status_color = {
                "OPEN": "#38bdf8",
                "INVESTIGATING": "#fbbf24",
                "CLOSED": "#34d399",
            }.get(record.get("status"), "#ffffff")

            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(15,23,42,0.85), rgba(10,15,28,0.95)); border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid {priority_color}; padding: 20px 24px; border-radius: 16px; margin-bottom: 16px; box-shadow: 0 12px 32px rgba(0,0,0,0.4);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                        <div>
                            <div style="font-family:'Outfit', sans-serif; font-size:1.35rem; font-weight:700; color:#f8fafc; margin-bottom:4px;">
                                {record.get('title')}
                            </div>
                            <div style="font-family:'JetBrains Mono', monospace; font-size:0.78rem; color:#94a3b8;">
                                REF: <span style="color:#ffffff; font-weight:700;">{record.get('case_reference')}</span> · REGISTERED: {str(record.get('created_at'))[:19]}
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; font-weight:700; background:{status_bg}; border:1px solid {status_color}; padding:4px 12px; border-radius:20px; color:{status_color};">
                                STATUS: {record.get('status')}
                            </span>
                            <span style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; font-weight:700; background:rgba(239,68,68,0.15); border:1px solid {priority_color}; padding:4px 12px; border-radius:20px; color:{priority_color};">
                                PRIORITY: {record.get('priority')}
                            </span>
                        </div>
                    </div>
                    <div style="margin-top:16px; display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; font-size:0.84rem; color:#cbd5e1; background:rgba(0,0,0,0.25); padding:12px 16px; border-radius:10px;">
                        <div><span style="color:#64748b; font-family:'JetBrains Mono', monospace; font-size:0.72rem; text-transform:uppercase;">Case Type:</span><br><b>{record.get('case_type') or 'N/A'}</b></div>
                        <div><span style="color:#64748b; font-family:'JetBrains Mono', monospace; font-size:0.72rem; text-transform:uppercase;">Jurisdiction:</span><br><b>{record.get('location') or 'N/A'}</b></div>
                        <div><span style="color:#64748b; font-family:'JetBrains Mono', monospace; font-size:0.72rem; text-transform:uppercase;">Assigned Officer:</span><br><b>{record.get('assigned_officer') or 'Unassigned'}</b></div>
                    </div>
                    <div style="margin-top:14px; font-size:0.86rem; color:#94a3b8; line-height:1.5;">
                        <span style="color:#64748b; font-family:'JetBrains Mono', monospace; font-size:0.72rem; text-transform:uppercase;">Incident Summary:</span><br>
                        {record.get('description') or 'No description recorded.'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Timeline
            timeline = repository.get_investigation_timeline(lookup)
            if timeline:
                events_html = "".join([
                    f"""
                    <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(15,23,42,0.8); border:1px solid rgba(255,255,255,0.1); padding:6px 12px; border-radius:8px; font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#cbd5e1; margin-right:8px; margin-bottom:8px;">
                        <span style="width:6px; height:6px; background:#38bdf8; border-radius:50%;"></span>
                        <b>{ev.get('event_type')}</b>
                        <span style="color:#64748b;">({str(ev.get('created_at'))[11:16]})</span>
                    </div>
                    """
                    for ev in timeline
                ])
                st.markdown(f'<div style="margin-bottom:14px;"><span style="font-family:\'JetBrains Mono\', monospace; font-size:0.72rem; color:#64748b; text-transform:uppercase;">EVENT TIMELINE:</span><div style="margin-top:6px; display:flex; flex-wrap:wrap;">{events_html}</div></div>', unsafe_allow_html=True)

            act1, act2, act3, act4 = st.columns(4)
            with act1:
                if record.get("status") != "INVESTIGATING":
                    if st.button("Mark Investigating", key="btn_investigating"):
                        repository.update_investigation(lookup, {"status": "INVESTIGATING"})
                        st.success("Status updated to INVESTIGATING.")
                        st.rerun()
            with act2:
                if record.get("status") != "CLOSED":
                    if st.button("Close Investigation", key="btn_close", type="primary"):
                        repository.update_investigation(lookup, {"status": "CLOSED"})
                        st.success("Investigation closed.")
                        st.rerun()
            with act3:
                if record.get("status") == "CLOSED":
                    if st.button("Re-open Case", key="btn_reopen"):
                        repository.update_investigation(lookup, {"status": "OPEN"})
                        st.success("Case re-opened.")
                        st.rerun()
            with act4:
                if st.button("Delete Case", key="btn_delete"):
                    repository.delete_investigation(lookup)
                    st.success("Investigation deleted.")
                    st.rerun()
        else:
            st.info(f"No investigation matching Case ID '{lookup}' was found in SQLite.")