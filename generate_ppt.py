"""Script to generate CRIME X PowerPoint Presentation (.pptx)."""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_crime_x_presentation(output_path: str = "CRIME_X_Project_Presentation.pptx"):
    prs = Presentation()
    # Set slide dimensions to widescreen 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # blank layout

    # Color Palette
    COLOR_BG = RGBColor(15, 23, 42)       # Dark Slate #0F172A
    COLOR_CARD = RGBColor(30, 41, 59)     # Slate 800 #1E293B
    COLOR_BORDER = RGBColor(51, 65, 85)   # Slate 700 #334155
    COLOR_ACCENT = RGBColor(56, 189, 248)  # Sky Blue #38BDF8
    COLOR_GOLD = RGBColor(245, 158, 11)   # Amber #F59E0B
    COLOR_RED = RGBColor(239, 68, 68)     # Crimson #EF4444
    COLOR_GREEN = RGBColor(34, 197, 94)   # Emerald #22C55E
    COLOR_TEXT = RGBColor(248, 250, 252)   # Slate 50 #F8FAFC
    COLOR_MUTED = RGBColor(148, 163, 184) # Slate 400 #94A3B8

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="CRIME X | POLICE INTELLIGENCE & ANALYTICS SYSTEM"):
        # Header category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT
        p_cat.font.name = "Calibri"

        # Main Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TEXT
        p_title.font.name = "Calibri"

        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_BORDER
        line.line.fill.background()

    def add_card(slide, left, top, width, height, title="", border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_ACCENT
            p.font.name = "Calibri"
        return card

    def add_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s1)

    # Accent Top Bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_ACCENT
    bar.line.fill.background()

    # Title Card Background
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_CARD
    card1.line.color.rgb = COLOR_ACCENT
    card1.line.width = Pt(2)

    # Title text
    tb = s1.shapes.add_textbox(Inches(1.4), Inches(1.6), Inches(10.5), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "CRIME X"
    p1.font.size = Pt(54)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT
    p1.font.name = "Calibri"

    p2 = tf.add_paragraph()
    p2.text = "India-Focused Police Crime Intelligence & Decision-Support System"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_ACCENT
    p2.font.name = "Calibri"
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "An end-to-end academic command center integrating NCRB historical analytics, real GIS mapping, supervised crime prediction, computer vision fire safety detection, case management & grounded AI."
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_MUTED
    p3.font.name = "Calibri"
    p3.space_before = Pt(15)

    # Key Metadata Boxes
    meta_data = [
        ("DATA ENGINE", "NCRB 2022 Grounded"),
        ("GIS MAPPING", "36 States & 594 Districts"),
        ("AI / DL VISION", "Custom YOLO11n Detector"),
        ("STACK", "Streamlit, Python, SQLite, ML")
    ]
    for i, (label, val) in enumerate(meta_data):
        m_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.4 + i*2.55), Inches(4.7), Inches(2.4), Inches(1.1))
        m_card.fill.solid()
        m_card.fill.fore_color.rgb = COLOR_BG
        m_card.line.color.rgb = COLOR_BORDER
        m_tb = s1.shapes.add_textbox(Inches(1.4 + i*2.55), Inches(4.75), Inches(2.4), Inches(1.0))
        m_tf = m_tb.text_frame
        m_tf.word_wrap = True
        mp1 = m_tf.paragraphs[0]
        mp1.text = label
        mp1.font.size = Pt(10)
        mp1.font.bold = True
        mp1.font.color.rgb = COLOR_GOLD
        mp1.font.name = "Calibri"
        mp1.alignment = PP_ALIGN.CENTER
        
        mp2 = m_tf.add_paragraph()
        mp2.text = val
        mp2.font.size = Pt(12)
        mp2.font.bold = True
        mp2.font.color.rgb = COLOR_TEXT
        mp2.font.name = "Calibri"
        mp2.alignment = PP_ALIGN.CENTER
        mp2.space_before = Pt(4)

    add_speaker_notes(s1, 
        "Good morning/afternoon everyone. Today I am presenting CRIME X, an academic police command-center intelligence and decision-support system tailored specifically for crime analytics across India.\n\n"
        "CRIME X brings together historical National Crime Records Bureau (NCRB) data, real GIS boundary mapping across 36 states and 594 districts, machine learning crime estimation, computer vision fire safety monitoring, operational case and alert management, and a grounded AI assistant.\n\n"
        "In this presentation, I will walk you through the problem statement, system architecture, module capabilities, technical implementation, and empirical verification."
    )

    # ==========================================
    # SLIDE 2: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ==========================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s2)
    add_header(s2, "Executive Summary & Problem Statement")

    col_width = Inches(3.64)
    col_gap = Inches(0.4)

    # Card 1: Problem
    add_card(s2, Inches(0.8), Inches(1.7), col_width, Inches(5.2), "The Problem Challenge", COLOR_RED)
    tb1 = s2.shapes.add_textbox(Inches(0.95), Inches(2.3), col_width - Inches(0.3), Inches(4.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    bullets1 = [
        ("Fragmented Data Silos: ", "Law enforcement agencies face disparate, unintegrated annual crime reports, making spatial-temporal analysis tedious."),
        ("Lack of Visual GIS Context: ", "Tabular NCRB data lacks interactive geospatial boundary maps for district-level threat assessment."),
        ("Absence of Predictive Support: ", "Traditional systems lack accessible machine-learning decision support to benchmark and anticipate regional crime trends."),
        ("Siloed Incident Response: ", "Case management, alert dispatch, and visual hazards (e.g. fire hazards) operate in disconnected tools.")
    ]
    for i, (b_title, b_desc) in enumerate(bullets1):
        p = tf1.paragraphs[0] if i == 0 else tf1.add_paragraph()
        p.space_after = Pt(12)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = COLOR_TEXT
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(12)
        run2.font.color.rgb = COLOR_MUTED

    # Card 2: Solution
    add_card(s2, Inches(0.8) + col_width + col_gap, Inches(1.7), col_width, Inches(5.2), "The CRIME X Solution", COLOR_ACCENT)
    tb2 = s2.shapes.add_textbox(Inches(0.95) + col_width + col_gap, Inches(2.3), col_width - Inches(0.3), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    bullets2 = [
        ("Unified Command Center: ", "A 10-module Streamlit interface providing real-time situational awareness and analytics."),
        ("Authentic Indian GIS Mapping: ", "Folium choropleths with 100% matched state boundaries and 594 verified district boundaries."),
        ("Supervised ML & DL Models: ", "Ridge regression annual crime estimator + YOLO11n object detector for visual fire hazard identification."),
        ("Grounded AI & Case Lifecycles: ", "Bilingual Hinglish AI assistant + full investigation audit trails and alert triage.")
    ]
    for i, (b_title, b_desc) in enumerate(bullets2):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.space_after = Pt(12)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = COLOR_TEXT
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(12)
        run2.font.color.rgb = COLOR_MUTED

    # Card 3: Academic Scope
    add_card(s2, Inches(0.8) + (col_width + col_gap)*2, Inches(1.7), col_width, Inches(5.2), "Academic Integrity & Scope", COLOR_GOLD)
    tb3 = s2.shapes.add_textbox(Inches(0.95) + (col_width + col_gap)*2, Inches(2.3), col_width - Inches(0.3), Inches(4.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    bullets3 = [
        ("100% Indian Domain Focus: ", "Tailored strictly to Indian Penal Code (IPC), IT Act offences, and NCRB administrative structures."),
        ("Zero Coordinate Fabrication: ", "100% authentic DataMeet and GADM boundary shapefiles without synthetic geometry."),
        ("Rigorous Disclaimers: ", "Exploratory decision-support baseline only; non-parametric confidence limits explicitly flagged."),
        ("Deterministic AI Safety: ", "Zero-hallucination chatbot returning strict data-absent notices for ungrounded queries.")
    ]
    for i, (b_title, b_desc) in enumerate(bullets3):
        p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
        p.space_after = Pt(12)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = COLOR_TEXT
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(12)
        run2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s2,
        "Law enforcement analysts and decision-makers face a critical challenge: raw crime data published by NCRB is rich but static, highly unstructured across tables, and lacks intuitive GIS context.\n\n"
        "CRIME X solves this by consolidating raw crime stats, administrative GIS shapefiles, ML predictors, computer vision models, and operational case tools into a single unified command center.\n\n"
        "Crucially, CRIME X adheres to high academic integrity—we strictly avoid synthetic data fabrication, state disclaimers prominently, and ensure our AI engine never hallucinates."
    )

    # ==========================================
    # SLIDE 3: SYSTEM ARCHITECTURE & TECH STACK
    # ==========================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s3)
    add_header(s3, "System Architecture & Modular Design")

    # Left: Architecture Flow Box
    add_card(s3, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.2), "Layered Architecture Flow")
    tb_arch = s3.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(7.1), Inches(4.4))
    tf_arch = tb_arch.text_frame
    tf_arch.word_wrap = True

    layers = [
        ("1. UI & Presentation Layer", "Streamlit Command Center with custom Police Theme CSS (src/ui/components.py)"),
        ("2. Service Orchestration Layer", "CrimeXService & specialized services (Analytics, GIS Map, ML, Fire Detection, AI)"),
        ("3. GIS & Spatial Pipeline", "GeoPandas, Folium, Shapely & Name Normalizer Engine (src/gis/name_normalizer.py)"),
        ("4. AI / ML / DL Engine", "Scikit-Learn Ridge Regression (ML) + Ultralytics YOLO11n Fire Detector (DL)"),
        ("5. Repository & Data Layer", "SQLAlchemy 2.0 ORM Repository Pattern over SQLite3 Datastore (database/crime_x.sqlite3)")
    ]
    for i, (l_title, l_desc) in enumerate(layers):
        p = tf_arch.paragraphs[0] if i == 0 else tf_arch.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = l_title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = COLOR_ACCENT
        r2 = p.add_run()
        r2.text = "   └── " + l_desc
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT

    # Right: Tech Stack Summary
    add_card(s3, Inches(8.6), Inches(1.7), Inches(3.933), Inches(5.2), "Technology Stack", COLOR_GOLD)
    tb_tech = s3.shapes.add_textbox(Inches(8.8), Inches(2.3), Inches(3.5), Inches(4.4))
    tf_tech = tb_tech.text_frame
    tf_tech.word_wrap = True

    techs = [
        ("Language & Core", "Python 3.11+ / 3.13"),
        ("Web Framework", "Streamlit 1.30+"),
        ("GIS & Mapping", "GeoPandas, Folium, Shapely"),
        ("Machine Learning", "Scikit-Learn, Pandas, NumPy"),
        ("Deep Learning", "Ultralytics YOLO11n, PyTorch"),
        ("Database & ORM", "SQLite 3, SQLAlchemy 2.0"),
        ("Testing Suite", "Pytest (Unit & Integration)")
    ]
    for i, (t_cat, t_val) in enumerate(techs):
        p = tf_tech.paragraphs[0] if i == 0 else tf_tech.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = t_cat + ": "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_GOLD
        r2 = p.add_run()
        r2.text = t_val
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_TEXT

    add_speaker_notes(s3,
        "Here we see the software architecture of CRIME X. The system strictly adheres to clean architectural principles.\n\n"
        "At the top is the Streamlit UI layer styled with a custom high-contrast dark command-center aesthetic.\n\n"
        "Below the UI is the Service Orchestration layer (CrimeXService), which delegates tasks to specialized domain engines: GIS pipelines, ML predictors, YOLO visual detectors, and SQLAlchemy repository calls.\n\n"
        "Everything persists in a lightweight, robust SQLite database using SQLAlchemy 2.0 ORM models."
    )

    # ==========================================
    # SLIDE 4: DATA PROVENANCE & REAL GIS PIPELINE
    # ==========================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s4)
    add_header(s4, "Data Provenance & Verified Indian GIS Pipeline")

    # Left: NCRB Provenance
    add_card(s4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "NCRB Grounded Data Provenance")
    tb_ncrb = s4.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_ncrb = tb_ncrb.text_frame
    tf_ncrb.word_wrap = True
    ncrb_bullets = [
        ("Physical IPC Crime Records: ", "NCRB Crime in India 2022 Table 1.1 with 934 district-level records across 36 States/UTs."),
        ("Cybercrime Statistics: ", "NCRB 2022 Table 1.9 capturing IT Act offences, online financial fraud, identity theft, and extortion."),
        ("State Population & Rates: ", "NCRB Table 1A.1 projected population (in Lakhs) and official rate of cognizable crimes per 100k population."),
        ("Historical Ahmedabad Series: ", "Gujarat police jurisdiction multi-year baseline (2014–2018) for temporal comparison.")
    ]
    for i, (b_title, b_desc) in enumerate(ncrb_bullets):
        p = tf_ncrb.paragraphs[0] if i == 0 else tf_ncrb.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    # Right: GIS Pipeline
    add_card(s4, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Real GIS & Boundary Normalization")
    tb_gis = s4.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_gis = tb_gis.text_frame
    tf_gis.word_wrap = True
    gis_bullets = [
        ("State Polygons (36/36 Matched): ", "Authentic DataMeet Open Maps GeoJSON boundary shapefile covering all 36 States & UTs (including Ladakh & J&K)."),
        ("District Polygons (594 Boundaries): ", "Authentic GADM administrative district shapefile covering 594 geographical boundary polygons."),
        ("Name Normalization Engine: ", "src/gis/name_normalizer.py handles spelling variations, parent-state verification, and string distance matching."),
        ("Zero Fabrication Guarantee: ", "No synthetic centroids or random coordinates are generated. Unmatched police divisions (e.g. Railway Police) are transparently logged.")
    ]
    for i, (b_title, b_desc) in enumerate(gis_bullets):
        p = tf_gis.paragraphs[0] if i == 0 else tf_gis.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s4,
        "Data provenance and spatial accuracy are essential for any police intelligence software.\n\n"
        "All crime data in CRIME X is grounded in official National Crime Records Bureau (NCRB) publications.\n\n"
        "On the GIS side, we implemented a custom Name Normalization Engine (src/gis/name_normalizer.py) that bridges state and district naming discrepancies between NCRB tables and DataMeet/GADM GeoJSON maps. We achieved 100% state boundary matching and mapped over 400 district polygons cleanly."
    )

    # ==========================================
    # SLIDE 5: OPERATIONS DASHBOARD & CRIME ANALYTICS
    # ==========================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s5)
    add_header(s5, "Module 1 & 2: Operations Dashboard & Crime Analytics")

    # Top KPI summary bar
    kpi_items = [
        ("TOTAL IPC CRIMES", "934 Records", COLOR_ACCENT),
        ("CYBERCRIME OFFENCES", "IT Act Table 1.9", COLOR_GOLD),
        ("GIS MAP COVERAGE", "36 States / 594 Dist", COLOR_GREEN),
        ("ACTIVE ALERTS", "Triage Dispatch", COLOR_RED)
    ]
    for i, (k_label, k_val, k_col) in enumerate(kpi_items):
        k_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i*2.98), Inches(1.7), Inches(2.8), Inches(1.0))
        k_card.fill.solid()
        k_card.fill.fore_color.rgb = COLOR_CARD
        k_card.line.color.rgb = k_col
        k_tb = s5.shapes.add_textbox(Inches(0.8 + i*2.98), Inches(1.75), Inches(2.8), Inches(0.9))
        k_tf = k_tb.text_frame
        k_tf.word_wrap = True
        kp1 = k_tf.paragraphs[0]
        kp1.text = k_label
        kp1.font.size = Pt(10)
        kp1.font.bold = True
        kp1.font.color.rgb = k_col
        kp1.alignment = PP_ALIGN.CENTER
        kp2 = k_tf.add_paragraph()
        kp2.text = k_val
        kp2.font.size = Pt(14)
        kp2.font.bold = True
        kp2.font.color.rgb = COLOR_TEXT
        kp2.alignment = PP_ALIGN.CENTER
        kp2.space_before = Pt(2)

    # Main Left Card: Operations Dashboard Features
    add_card(s5, Inches(0.8), Inches(2.9), Inches(5.7), Inches(4.0), "1. Operations Dashboard View")
    tb_dash = s5.shapes.add_textbox(Inches(1.0), Inches(3.5), Inches(5.3), Inches(3.2))
    tf_dash = tb_dash.text_frame
    tf_dash.word_wrap = True
    dash_bullets = [
        ("Command-Center KPIs: ", "High-level aggregation of physical crimes, cyber incidents, and active emergency alerts."),
        ("System Health Monitor: ", "Live status indicators for SQLite database connection, GIS shapefiles, and ML model availability."),
        ("Operational Alert Ticker: ", "Displays latest critical and high-priority law enforcement dispatches.")
    ]
    for i, (b_t, b_d) in enumerate(dash_bullets):
        p = tf_dash.paragraphs[0] if i == 0 else tf_dash.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_MUTED

    # Main Right Card: Crime Intelligence Features
    add_card(s5, Inches(6.833), Inches(2.9), Inches(5.7), Inches(4.0), "2. Crime Intelligence View")
    tb_intel = s5.shapes.add_textbox(Inches(7.0), Inches(3.5), Inches(5.3), Inches(3.2))
    tf_intel = tb_intel.text_frame
    tf_intel.word_wrap = True
    intel_bullets = [
        ("State & District Rankings: ", "Dynamic bar charts comparing top crime reporting states and districts across India."),
        ("Category Breakdown: ", "Exploratory analysis across IPC crime categories (Violent Crime, Theft, Property Crime, etc.)."),
        ("Benchmarking & Filters: ", "State-level per-100k rate comparison against national averages.")
    ]
    for i, (b_t, b_d) in enumerate(intel_bullets):
        p = tf_intel.paragraphs[0] if i == 0 else tf_intel.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s5,
        "Modules 1 and 2 serve as the primary analytics hub of CRIME X.\n\n"
        "The Operations Dashboard provides command-level executive situational awareness with real-time KPI totals, system diagnostics, and active alerts.\n\n"
        "The Crime Intelligence module lets analysts perform deep exploratory analysis—ranking states and districts, filtering by IPC crime categories, and examining state crime rates per 100k population."
    )

    # ==========================================
    # SLIDE 6: INTERACTIVE GEOGRAPHIC CRIME MAP (GIS)
    # ==========================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s6)
    add_header(s6, "Module 3: Geographic Crime Intelligence (Folium GIS Map)")

    add_card(s6, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Interactive Folium Map Engine")
    tb_map = s6.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_map = tb_map.text_frame
    tf_map.word_wrap = True
    map_bullets = [
        ("Choropleth Visualizations: ", "State and district boundaries shaded dynamically based on crime density."),
        ("Interactive Tooltips & Cards: ", "Hovering over any district displays exact crime counts, state affiliation, and category breakdown."),
        ("Dynamic Quartile Legends: ", "Prevents visual bias by categorizing crime levels into balanced statistical quartiles (Q1 to Q4)."),
        ("Seamless Zoom & Pan: ", "Fully responsive GIS web canvas embedded directly inside the Streamlit dashboard.")
    ]
    for i, (b_t, b_d) in enumerate(map_bullets):
        p = tf_map.paragraphs[0] if i == 0 else tf_map.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s6, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "GIS Integrity & Diagnostic Audit", COLOR_GOLD)
    tb_audit = s6.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_audit = tb_audit.text_frame
    tf_audit.word_wrap = True
    audit_bullets = [
        ("100% State Boundary Matching: ", "All 36 States and Union Territories match perfectly with DataMeet GeoJSON polygon boundaries."),
        ("District Boundary Resolution: ", "Over 400 NCRB district entities cleanly matched against GADM 594 administrative boundaries."),
        ("Audited Non-Geographic Entries: ", "Specialized police jurisdictions (e.g., Railway Police, Commissionerate splits) lacking discrete polygons are logged transparently in data/processed/gis_name_matching.csv."),
        ("Zero Fabrication Principle: ", "No synthetic centroids or fake map markers are ever generated.")
    ]
    for i, (b_t, b_d) in enumerate(audit_bullets):
        p = tf_audit.paragraphs[0] if i == 0 else tf_audit.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s6,
        "Module 3 is our Geographic Crime Intelligence map. Built using Folium and GeoPandas, it renders interactive choropleth maps of India.\n\n"
        "We utilize quantile color scaling so that extreme outliers do not skew the visual distribution.\n\n"
        "We also enforce strict GIS auditability: specialized police jurisdictions like Railway Police don't have standard administrative boundary shapefiles, so instead of fabricating fake points, CRIME X transparently logs them in a diagnostic audit file surfaced in the UI."
    )

    # ==========================================
    # SLIDE 7: PREDICTIVE CRIME ANALYTICS (ML)
    # ==========================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s7)
    add_header(s7, "Module 4: Supervised ML Crime Prediction Engine")

    add_card(s7, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Ridge Regression ML Model")
    tb_ml = s7.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_ml = tb_ml.text_frame
    tf_ml.word_wrap = True
    ml_bullets = [
        ("Supervised ML Baseline: ", "Linear / Ridge Regression decision-support baseline trained on multi-year observation series."),
        ("Feature Engineering Matrix: ", "Encodes state/district historical volume, category weightings, and temporal baseline trends."),
        ("Persisted Prediction History: ", "All prediction queries, input snapshots, and estimated outputs are saved to the crime_predictions database table."),
        ("Comparative Baseline: ", "Allows analysts to compare projected annual totals against historical NCRB benchmarks.")
    ]
    for i, (b_t, b_d) in enumerate(ml_bullets):
        p = tf_ml.paragraphs[0] if i == 0 else tf_ml.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s7, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Academic Safeguards & Limitations", COLOR_RED)
    tb_safe = s7.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_safe = tb_safe.text_frame
    tf_safe.word_wrap = True
    safe_bullets = [
        ("Decision-Support Scope: ", "Explicit UI disclaimers state that prediction estimates are for trend comparison, NOT absolute guarantees."),
        ("Confidence Limits Flagged: ", "Parametric confidence intervals are explicitly marked UNAVAILABLE due to short 3-year observation series."),
        ("Non-Deterministic Guardrails: ", "Prevents over-reliance on predictive models by clearly displaying statistical limitations."),
        ("Ethics & Accountability: ", "Designed to support resource allocation planning while preventing automated bias in policing.")
    ]
    for i, (b_t, b_d) in enumerate(safe_bullets):
        p = tf_safe.paragraphs[0] if i == 0 else tf_safe.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s7,
        "Module 4 incorporates supervised Machine Learning for crime trend estimation.\n\n"
        "We implemented a Ridge Regression model (src/ml/train.py) that predicts estimated annual crime counts based on district historical volumes and crime categories.\n\n"
        "Importantly, we uphold academic rigor: parametric confidence intervals are explicitly flagged as unavailable because 3 annual observations cannot yield statistically valid parametric confidence intervals. Disclaimers are prominently displayed in the UI."
    )

    # ==========================================
    # SLIDE 8: CYBERCRIME & DIGITAL THREAT INTELLIGENCE
    # ==========================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s8)
    add_header(s8, "Module 5: Cybercrime & Digital Threat Intelligence")

    add_card(s8, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "IT Act & Cyber Offence Coverage")
    tb_cyb1 = s8.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_cyb1 = tb_cyb1.text_frame
    tf_cyb1.word_wrap = True
    cyb1_bullets = [
        ("NCRB Table 1.9 Grounding: ", "Dedicated analytical pipeline covering IT Act offences across Indian States & UTs."),
        ("Categorical Granularity: ", "Breaks down cyber offences into key legal categories under Indian cybersecurity law."),
        ("State Cyber Cell Metrics: ", "Ranks state-wise cybercrime density and digital threat volume."),
        ("Financial Loss Analytics: ", "Highlights high-incidence online financial fraud zones across urban centers.")
    ]
    for i, (b_t, b_d) in enumerate(cyb1_bullets):
        p = tf_cyb1.paragraphs[0] if i == 0 else tf_cyb1.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s8, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Key Cyber Offence Categories", COLOR_GOLD)
    tb_cyb2 = s8.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_cyb2 = tb_cyb2.text_frame
    tf_cyb2.word_wrap = True
    cyb2_bullets = [
        ("Online Financial Fraud: ", "Banking scams, UPI frauds, phishing, and credit card fraud incidents."),
        ("Identity Theft & Impersonation: ", "Social media identity theft, fake profiles, and spoofing offences."),
        ("Cyber Blackmail & Extortion: ", "Ransomware threats, digital blackmail, and online harassment cases."),
        ("System Hacking & Malware: ", "Unauthorized network access, malware deployment, and web defacement.")
    ]
    for i, (b_t, b_d) in enumerate(cyb2_bullets):
        p = tf_cyb2.paragraphs[0] if i == 0 else tf_cyb2.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s8,
        "Cybercrime is one of the fastest-growing threat vectors in modern law enforcement.\n\n"
        "Module 5 provides dedicated Cybercrime Intelligence grounded in NCRB 2022 District Table 1.9.\n\n"
        "It categorizes digital offences—such as online financial fraud, identity theft, cyber blackmail, and system hacking—allowing cyber cell officers to pinpoint high-risk regions and allocate specialized digital forensic resources."
    )

    # ==========================================
    # SLIDE 9: DEEP LEARNING VISION: AI FIRE DETECTION
    # ==========================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s9)
    add_header(s9, "Module 6: Computer Vision Safety Prototype (AI Fire Detection)")

    add_card(s9, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "YOLO11n Visual Detection Model")
    tb_fire1 = s9.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_fire1 = tb_fire1.text_frame
    tf_fire1.word_wrap = True
    fire1_bullets = [
        ("Custom YOLO11n Weights: ", "Powered by crime_x_fire_detector_v2.pt trained specifically for visual fire hazard identification."),
        ("Real-Time Image Inference: ", "Processes uploaded surveillance frames and highlights fire hazards with visual bounding boxes."),
        ("Inference Audit Logging: ", "Saves image dimensions, bounding box coordinates, and confidence scores directly to fire_detections table."),
        ("Situational Awareness: ", "Integrated into the police command center for rapid hazard verification.")
    ]
    for i, (b_t, b_d) in enumerate(fire1_bullets):
        p = tf_fire1.paragraphs[0] if i == 0 else tf_fire1.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s9, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Model Scope & Safety Disclaimers", COLOR_RED)
    tb_fire2 = s9.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_fire2 = tb_fire2.text_frame
    tf_fire2.word_wrap = True
    fire2_bullets = [
        ("Fire-Only Annotation Scope: ", "Trained strictly on visual fire annotations; does NOT detect smoke or chemical fumes."),
        ("Academic Prototype Standard: ", "Designated as an experimental computer-vision prototype for situational awareness."),
        ("Non-Certified Safety Equipment: ", "Explicitly marked in UI: NOT a certified life-safety fire protection or alarm system."),
        ("Human-in-the-Loop Triage: ", "Requires officer verification before dispatching emergency fire response teams.")
    ]
    for i, (b_t, b_d) in enumerate(fire2_bullets):
        p = tf_fire2.paragraphs[0] if i == 0 else tf_fire2.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s9,
        "Module 6 extends CRIME X into Deep Learning computer vision for situational awareness.\n\n"
        "Using Ultralytics YOLO11n (crime_x_fire_detector_v2.pt), the module analyzes image feeds to detect visual fire hazards and logs detection coordinates to our SQLite database.\n\n"
        "We clearly specify the model scope: it is trained on visual fire only (not smoke), and serves as an experimental academic prototype rather than certified safety equipment."
    )

    # ==========================================
    # SLIDE 10: OPERATIONS: CASES, INVESTIGATION & ALERT CENTER
    # ==========================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s10)
    add_header(s10, "Modules 7 & 8: Case Management & Operational Alert Triage")

    add_card(s10, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "7. Cases & Investigation Lifecycle")
    tb_case = s10.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_case = tb_case.text_frame
    tf_case.word_wrap = True
    case_bullets = [
        ("Full Case CRUD: ", "Create, view, update status (OPEN, INVESTIGATING, CLOSED), assign investigating officers, and delete cases."),
        ("Evidence Tracking Engine: ", "Attaches digital and physical evidence records directly to investigation IDs."),
        ("Timeline Event Audit Trail: ", "Logs chronological investigation milestones and officer updates (investigation_events table)."),
        ("Priority Triage: ", "Categorizes cases by priority levels (LOW, MEDIUM, HIGH, CRITICAL).")
    ]
    for i, (b_t, b_d) in enumerate(case_bullets):
        p = tf_case.paragraphs[0] if i == 0 else tf_case.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s10, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "8. Operational Alert Dispatch Triage", COLOR_RED)
    tb_alert = s10.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_alert = tb_alert.text_frame
    tf_alert.word_wrap = True
    alert_bullets = [
        ("4 Severity Triage Levels: ", "Supports INFO, WARNING, HIGH, and CRITICAL emergency dispatch notifications."),
        ("Resolution Lifecycle: ", "Tracks alert status transitions (UNREAD → READ → RESOLVED) with timestamp tracking."),
        ("Cross-Module Integration: ", "Links alerts to active investigations or spatial crime hotspots."),
        ("Command Dashboard Ticker: ", "Automatically feeds active critical alerts into the central command bar.")
    ]
    for i, (b_t, b_d) in enumerate(alert_bullets):
        p = tf_alert.paragraphs[0] if i == 0 else tf_alert.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s10,
        "Modules 7 and 8 manage operational workflows for police officers and station commanders.\n\n"
        "The Cases & Investigation module provides end-to-end lifecycle management: creating case files, managing officer assignments, logging evidence, and maintaining timeline event audit trails.\n\n"
        "The Alert Center handles operational dispatch with 4 severity levels (INFO, WARNING, HIGH, CRITICAL) and full read/resolution tracking."
    )

    # ==========================================
    # SLIDE 11: BOUNDED AI ASSISTANT (ENGLISH & HINGLISH)
    # ==========================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s11)
    add_header(s11, "Module 9: Bounded AI Intelligence Assistant (English & Hinglish)")

    add_card(s11, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Deterministic Bounded AI Architecture")
    tb_ai1 = s11.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_ai1 = tb_ai1.text_frame
    tf_ai1.word_wrap = True
    ai1_bullets = [
        ("Grounded Query Routing: ", "src/services/ai_service.py evaluates natural language inputs against direct database queries."),
        ("Zero-Hallucination Safety: ", "Queries are resolved strictly against SQLite, NCRB tables, GIS maps, and case records."),
        ("Transparent Absent Notice: ", "For unsupported or ungrounded queries, returns: 'Data is not available in the current CRIME X database.'"),
        ("Auditable SQL Resolution: ", "Eliminates unsafe generative AI hallucinations in law enforcement decision contexts.")
    ]
    for i, (b_t, b_d) in enumerate(ai1_bullets):
        p = tf_ai1.paragraphs[0] if i == 0 else tf_ai1.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s11, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Bilingual & Hinglish Inquiry Examples", COLOR_ACCENT)
    tb_ai2 = s11.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_ai2 = tb_ai2.text_frame
    tf_ai2.word_wrap = True
    ai2_bullets = [
        ("English Query: ", "\"Which state has the highest total crime count?\"\n   └── Evaluates state totals directly from crime_records table."),
        ("Hinglish Query: ", "\"India me sabse zyada crime kis state me hai?\"\n   └── Normalizes Hinglish keywords to execute identical grounded query."),
        ("Cybercrime Query: ", "\"Cyber fraud kaunsa highest hai?\"\n   └── Aggregates IT Act cybercrime metrics for top offences."),
        ("Case Status Query: ", "\"Kitne investigation open hain?\"\n   └── Counts active cases where status = 'OPEN'.")
    ]
    for i, (b_t, b_d) in enumerate(ai2_bullets):
        p = tf_ai2.paragraphs[0] if i == 0 else tf_ai2.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_GOLD
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(11)
        r2.font.color.rgb = COLOR_TEXT

    add_speaker_notes(s11,
        "Module 9 is our AI Assistant. In critical law enforcement environments, generative LLM hallucinations are unacceptable.\n\n"
        "We built a deterministic, grounded AI routing engine (src/services/ai_service.py) that resolves natural language queries directly against SQLite data.\n\n"
        "It supports both English and practical Hinglish queries—like 'India me sabse zyada crime kis state me hai?'—and if data is absent, it transparently states so without making up facts."
    )

    # ==========================================
    # SLIDE 12: DATABASE DESIGN & SCHEMA ARCHITECTURE
    # ==========================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s12)
    add_header(s12, "Database Architecture & Relational Schema")

    # Table Grid Layout
    tables_info = [
        ("states & districts", "Hierarchical administrative mapping with unique state-district composite constraints."),
        ("crime_records", "Physical IPC crime statistics with source dataset provenance and composite indexes."),
        ("cybercrime_records", "IT Act and cyber fraud category metrics indexed by state, district, and year."),
        ("crime_predictions", "Persisted prediction logs, input feature snapshots, and academic disclaimers."),
        ("fire_detections", "Image inference audit logs, bounding boxes, width/height, and confidence scores."),
        ("investigations & evidence", "Case lifecycle management, assigned officer, timeline events, and evidence logs."),
        ("alerts", "Operational emergency dispatch records with severity triage and resolution lifecycle.")
    ]
    for i, (t_name, t_desc) in enumerate(tables_info):
        row = i // 2
        col = i % 2
        w = Inches(5.6)
        h = Inches(1.2)
        l = Inches(0.8) if col == 0 else Inches(6.833)
        t = Inches(1.7 + row * 1.35)

        add_card(s12, l, t, w, h, border_color=COLOR_BORDER)
        tb_t = s12.shapes.add_textbox(l + Inches(0.15), t + Inches(0.1), w - Inches(0.3), h - Inches(0.2))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        pt1 = tf_t.paragraphs[0]
        pt1.text = "Table: " + t_name
        pt1.font.size = Pt(13)
        pt1.font.bold = True
        pt1.font.color.rgb = COLOR_ACCENT
        
        pt2 = tf_t.add_paragraph()
        pt2.text = t_desc
        pt2.font.size = Pt(11)
        pt2.font.color.rgb = COLOR_TEXT
        pt2.space_before = Pt(2)

    add_speaker_notes(s12,
        "Here is the SQLite 3 database schema implemented via SQLAlchemy 2.0 ORM (src/database/models.py).\n\n"
        "The relational schema contains 8 core tables cleanly normalized: administrative states & districts, crime & cybercrime records, ML prediction history, fire detection audit logs, investigation cases with evidence timelines, and operational alerts.\n\n"
        "We also enforce composite unique constraints to guarantee idempotent data seeding."
    )

    # ==========================================
    # SLIDE 13: QUALITY ASSURANCE, TESTING & DIAGNOSTICS
    # ==========================================
    s13 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s13)
    add_header(s13, "Software Engineering, Automated Testing & Settings Diagnostics")

    add_card(s13, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Pytest Automated Test Suite")
    tb_t1 = s13.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_t1 = tb_t1.text_frame
    tf_t1.word_wrap = True
    t1_bullets = [
        ("Comprehensive Test Suite: ", "Automated Pytest coverage across data layers, services, GIS pipelines, and ML models."),
        ("GIS Name Normalizer Tests: ", "Verifies 100% state matching and string distance fallback behavior."),
        ("Database Repository Tests: ", "Validates CRUD operations, foreign key integrity, and cascade deletes."),
        ("Service Isolation Tests: ", "Tests CrimeXService methods against test database fixtures.")
    ]
    for i, (b_t, b_d) in enumerate(t1_bullets):
        p = tf_t1.paragraphs[0] if i == 0 else tf_t1.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s13, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Module 10: System Settings Diagnostics", COLOR_GREEN)
    tb_t2 = s13.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_t2 = tb_t2.text_frame
    tf_t2.word_wrap = True
    t2_bullets = [
        ("Runtime Health Monitor: ", "Checks SQLite datastore connection and database file size."),
        ("Model Verification: ", "Verifies weight integrity for YOLO11n fire model (crime_x_fire_detector_v2.pt)."),
        ("GIS Layer Diagnostics: ", "Surfaces unmatched administrative entries and polygon coverage metrics."),
        ("Environment Configuration: ", "Validates Python dependencies and system paths.")
    ]
    for i, (b_t, b_d) in enumerate(t2_bullets):
        p = tf_t2.paragraphs[0] if i == 0 else tf_t2.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s13,
        "Software quality and diagnostic transparency are key pillars of CRIME X.\n\n"
        "We maintain a comprehensive Pytest regression test suite covering all services, database repository operations, name normalization logic, and ML predictors.\n\n"
        "Furthermore, Module 10 (System Settings) provides live runtime health diagnostics directly in the UI, displaying database integrity, model weight status, and GIS shapefile coverage."
    )

    # ==========================================
    # SLIDE 14: FUTURE ROADMAP & CONCLUSION
    # ==========================================
    s14 = prs.slides.add_slide(blank_slide_layout)
    add_bg(s14)
    add_header(s14, "Future Enhancements & Conclusion")

    add_card(s14, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2), "Future Enhancement Roadmap", COLOR_GOLD)
    tb_f1 = s14.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.4))
    tf_f1 = tb_f1.text_frame
    tf_f1.word_wrap = True
    f1_bullets = [
        ("CCTNS API Integration: ", "Connect directly with India's Crime and Criminal Tracking Network & Systems for live feed updates."),
        ("Advanced Time-Series Forecasting: ", "Upgrade baseline Ridge ML to DeepAR or Prophet for complex temporal crime trends."),
        ("Multi-Camera CCTV Processing: ", "Expand YOLO vision module to process live RTSP surveillance streams across station networks."),
        ("Mobile Officer App: ", "Develop lightweight mobile companion app for field officers to receive critical alert dispatches.")
    ]
    for i, (b_t, b_d) in enumerate(f1_bullets):
        p = tf_f1.paragraphs[0] if i == 0 else tf_f1.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_card(s14, Inches(6.833), Inches(1.7), Inches(5.7), Inches(5.2), "Project Summary & Key Takeaways", COLOR_ACCENT)
    tb_f2 = s14.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_f2 = tb_f2.text_frame
    tf_f2.word_wrap = True
    f2_bullets = [
        ("Comprehensive 10-Module Platform: ", "Delivers an end-to-end command-center experience for law enforcement analytics."),
        ("Grounded & Authentic Data: ", "100% NCRB 2022 grounded statistics + DataMeet/GADM verified GIS boundaries."),
        ("Multi-Disciplinary AI Integration: ", "Combines ML regression, YOLO vision detection, and deterministic Hinglish AI."),
        ("Academic Rigor & Safety: ", "Enforces strict academic disclaimers, zero-hallucination AI, and zero coordinate fabrication.")
    ]
    for i, (b_t, b_d) in enumerate(f2_bullets):
        p = tf_f2.paragraphs[0] if i == 0 else tf_f2.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = "• " + b_t
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = COLOR_TEXT
        r2 = p.add_run()
        r2.text = b_d
        r2.font.size = Pt(12)
        r2.font.color.rgb = COLOR_MUTED

    add_speaker_notes(s14,
        "In conclusion, CRIME X demonstrates how modern open-source software, GIS mapping, machine learning, and computer vision can be combined into a robust police command center for India.\n\n"
        "In the future, we plan to integrate live CCTNS data feeds, implement deep learning time-series models like DeepAR, and scale computer vision to live CCTV streams.\n\n"
        "Thank you for your time and attention! I am now open to any questions."
    )

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_crime_x_presentation()
