"""Reusable visual components and motion design system for the CRIME X command center."""

from __future__ import annotations

import time
import pandas as pd
import streamlit as st


def inject_theme() -> None:
    """Inject the ultra-modern tactical glassmorphism 2.0 design system with motion animations."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

    :root {
        --cx-bg: #060913;
        --cx-bg-elevated: #0a0f1d;
        --cx-glass: rgba(13, 20, 36, 0.68);
        --cx-glass-elevated: rgba(18, 28, 52, 0.82);
        --cx-glass-border: rgba(255, 255, 255, 0.08);
        --cx-glass-border-hover: rgba(56, 189, 248, 0.35);
        --cx-glass-highlight: rgba(255, 255, 255, 0.16);
        --cx-red: #dc2626;
        --cx-red-accent: #f87171;
        --cx-crimson: #991b1b;
        --cx-crimson-dark: #7f1d1d;
        --cx-gold: #f59e0b;
        --cx-cyan: #38bdf8;
        --cx-cyan-glow: rgba(56, 189, 248, 0.4);
        --cx-emerald: #10b981;
        --cx-emerald-glow: rgba(16, 185, 129, 0.4);
        --cx-purple: #818cf8;
        --cx-muted: #94a3b8;
        --cx-text: #f8fafc;
    }

    /* Ambient Canvas & Dynamic Mesh Lighting */
    .stApp {
        background-color: var(--cx-bg);
        background-image:
            radial-gradient(at 10% 15%, rgba(99, 102, 241, 0.10) 0px, transparent 55%),
            radial-gradient(at 85% 85%, rgba(153, 27, 27, 0.12) 0px, transparent 50%),
            radial-gradient(at 50% 40%, rgba(56, 189, 248, 0.05) 0px, transparent 65%),
            radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.03) 0px, transparent 70%),
            radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 32px 32px;
        background-attachment: fixed;
        color: var(--cx-text);
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
    }

    /* Custom Tactical Scrollbars */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(6, 9, 19, 0.8);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(153, 27, 27, 0.45);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(220, 38, 38, 0.7);
    }

    /* =======================================================
       1. CINEMATIC LOGO: SLEEK BRAND IDENTITY
       ======================================================= */
    .cx-brand {
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 18px;
        margin-bottom: 20px;
        overflow: visible !important;
        position: relative;
    }

    .cx-brand::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #dc2626, #38bdf8);
        border-radius: 2px;
        box-shadow: 0 0 8px rgba(220, 38, 38, 0.6);
    }

    .cx-brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        overflow: visible !important;
    }

    .cx-brand-title {
        position: relative !important;
        display: inline-flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 2px 0 !important;
        font-size: 2.05rem !important;
        font-weight: 800 !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.14em !important;
        line-height: 1.1 !important;
        overflow: visible !important;
        cursor: pointer;
    }

    .cx-word-crime {
        position: relative !important;
        z-index: 10 !important;
        color: #f8fafc !important;
        font-weight: 800 !important;
        padding: 0 4px 0 0 !important;
        background: linear-gradient(180deg, #ffffff 30%, #cbd5e1 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
    }

    .cx-letter-x-box {
        position: relative !important;
        display: inline-block !important;
        z-index: 5 !important;
        margin-left: 2px !important;
        overflow: visible !important;
    }

    .cx-letter-x {
        display: inline-block !important;
        font-weight: 900 !important;
        color: #ef4444 !important;
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.5));
        transform-origin: center center;
        animation: emerge-x-behind 1.2s cubic-bezier(0.18, 0.9, 0.32, 1.2) 0.2s forwards !important;
    }

    .cx-brand-title:hover .cx-letter-x {
        animation: emerge-x-behind 1.0s cubic-bezier(0.18, 0.9, 0.32, 1.2) forwards !important;
        filter: drop-shadow(0 0 16px rgba(239, 68, 68, 0.8));
    }

    @keyframes emerge-x-behind {
        0% {
            opacity: 0;
            transform: translateX(-35px) scale(0.4) rotate(-30deg);
            filter: blur(4px) drop-shadow(0 0 0 rgba(239, 68, 68, 0));
        }
        55% {
            opacity: 1;
            transform: translateX(8px) scale(1.15) rotate(8deg);
            filter: blur(0px) drop-shadow(0 0 12px rgba(239, 68, 68, 0.7));
        }
        78% {
            opacity: 1;
            transform: translateX(-2px) scale(0.97) rotate(-2deg);
        }
        100% {
            opacity: 1;
            transform: translateX(0px) scale(1) rotate(0deg);
            filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.5));
        }
    }

    /* Crest Icon with Holographic Border */
    .cx-crest-box {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #991b1b 0%, #1e1b4b 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.15rem;
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
        letter-spacing: 0.04em;
        box-shadow: 0 6px 20px rgba(153, 27, 27, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }

    .cx-crest-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(transparent, rgba(239, 68, 68, 0.4), transparent 30%);
        animation: rotate-crest-border 4s linear infinite;
        z-index: 1;
    }

    .cx-crest-box-inner {
        position: relative;
        z-index: 2;
        background: #0d1222;
        width: 38px;
        height: 38px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    @keyframes rotate-crest-border {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .cx-brand p {
        color: var(--cx-muted);
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        line-height: 1.4;
        margin: 4px 0 0;
        font-weight: 600;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .cx-brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(153, 27, 27, 0.16);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.62rem;
        color: #fca5a5;
        font-weight: 600;
        letter-spacing: 0.08em;
        width: fit-content;
        margin-top: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .cx-brand-dot {
        width: 6px;
        height: 6px;
        background: #ef4444;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.8);
        animation: cx-dot-pulse 2s infinite ease-in-out;
    }

    @keyframes cx-dot-pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.4); opacity: 0.6; }
    }

    /* =======================================================
       2. GLASSMORPHIC SIDEBAR & NAVIGATION (TACTICAL DOCK)
       ======================================================= */
    [data-testid="stSidebar"] {
        background: rgba(8, 12, 22, 0.82) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 12px 0 40px rgba(0, 0, 0, 0.6) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] {
        gap: 4px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.14em !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        padding: 9px 14px !important;
        border-radius: 12px !important;
        border: 1px solid transparent !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        color: #94a3b8 !important;
        margin-bottom: 4px !important;
        background: transparent !important;
        position: relative !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }

    /* Active Radio Item Accent */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(90deg, rgba(153, 27, 27, 0.3) 0%, rgba(56, 189, 248, 0.08) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(153, 27, 27, 0.25), inset 3px 0 0 #ef4444 !important;
        transform: translateX(4px) !important;
    }

    /* =======================================================
       3. FROSTED GLASS METRIC & KPI CARDS WITH HOVER SHIMMER
       ======================================================= */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.7) 0%, rgba(10, 15, 28, 0.8) 100%) !important;
        backdrop-filter: blur(24px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 18px 22px !important;
        border-radius: 16px !important;
        min-height: 104px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Glowing Top Accent Bar */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #dc2626 0%, #f59e0b 50%, #38bdf8 100%);
        opacity: 0.65;
        transition: opacity 0.3s ease;
    }

    /* Shimmer light sweep on hover */
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -60%;
        width: 40%;
        height: 200%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.07), transparent);
        transform: rotate(25deg);
        transition: none;
        pointer-events: none;
    }

    [data-testid="stMetric"]:hover::after {
        left: 140%;
        transition: all 0.75s ease-in-out;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) !important;
        background: linear-gradient(145deg, rgba(20, 32, 58, 0.85) 0%, rgba(13, 20, 38, 0.95) 100%) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
        border-top-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5), 0 0 25px rgba(56, 189, 248, 0.12) !important;
    }

    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 12px rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
    }

    /* =======================================================
       4. CUSTOM TACTICAL KPI CARD WITH MOTION & BADGES
       ======================================================= */
    .cx-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .cx-kpi-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.72) 0%, rgba(10, 15, 28, 0.85) 100%);
        backdrop-filter: blur(24px) saturate(190%);
        -webkit-backdrop-filter: blur(24px) saturate(190%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.22);
        padding: 16px 20px;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    .cx-kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        border-radius: 2px 2px 0 0;
    }

    .cx-kpi-card.theme-red::before { background: linear-gradient(90deg, #ef4444, #be123c); }
    .cx-kpi-card.theme-cyan::before { background: linear-gradient(90deg, #38bdf8, #0284c7); }
    .cx-kpi-card.theme-emerald::before { background: linear-gradient(90deg, #10b981, #059669); }
    .cx-kpi-card.theme-amber::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .cx-kpi-card.theme-purple::before { background: linear-gradient(90deg, #818cf8, #6366f1); }

    .cx-kpi-card:hover {
        transform: translateY(-5px);
        background: linear-gradient(145deg, rgba(20, 32, 58, 0.88) 0%, rgba(13, 20, 38, 0.98) 100%);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 24px rgba(56, 189, 248, 0.12);
    }

    .cx-kpi-card.theme-red:hover { border-color: rgba(239, 68, 68, 0.35); }
    .cx-kpi-card.theme-cyan:hover { border-color: rgba(56, 189, 248, 0.35); }
    .cx-kpi-card.theme-emerald:hover { border-color: rgba(16, 185, 129, 0.35); }
    .cx-kpi-card.theme-amber:hover { border-color: rgba(245, 158, 11, 0.35); }
    .cx-kpi-card.theme-purple:hover { border-color: rgba(129, 140, 248, 0.35); }

    .cx-kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .cx-kpi-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #94a3b8;
    }

    .cx-kpi-icon {
        font-size: 1rem;
        opacity: 0.85;
    }

    .cx-kpi-value {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
        line-height: 1.1;
    }

    .cx-kpi-meta {
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.72rem;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
    }

    /* =======================================================
       5. MODERN FROSTED BUTTONS WITH TACTICAL SHINE
       ======================================================= */
    .stButton > button, .stFormSubmitButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.28) !important;
        background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.03em !important;
        padding: 10px 22px !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 16px rgba(153, 27, 27, 0.35) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton > button::before, .stFormSubmitButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: all 0.5s ease;
    }

    .stButton > button:hover::before, .stFormSubmitButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: rgba(255, 255, 255, 0.35) !important;
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.5) !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }

    .stButton > button:active, .stFormSubmitButton > button:active {
        transform: translateY(1px) scale(0.98) !important;
    }

    /* Secondary / Alternate Buttons */
    button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #e2e8f0 !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        color: #ffffff !important;
    }

    /* =======================================================
       6. FROSTED GLASS INPUTS & CONTROLS
       ======================================================= */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: rgba(13, 20, 36, 0.65) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        transition: all 0.25s ease !important;
    }

    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: transparent !important;
        color: #f8fafc !important;
        font-size: 0.92rem !important;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within {
        border-color: #38bdf8 !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25), 0 0 16px rgba(56, 189, 248, 0.15) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(13, 20, 36, 0.65) !important;
        backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        transition: all 0.25s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: rgba(56, 189, 248, 0.3) !important;
    }

    ul[role="listbox"] {
        background-color: rgba(10, 15, 28, 0.96) !important;
        backdrop-filter: blur(28px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7) !important;
    }

    ul[role="listbox"] li {
        color: #e2e8f0 !important;
        font-size: 0.88rem !important;
        transition: background-color 0.15s ease !important;
    }

    ul[role="listbox"] li:hover {
        background-color: rgba(153, 27, 27, 0.3) !important;
        color: #ffffff !important;
    }

    /* Segmented Control Mode */
    [data-testid="stSegmentedControl"] {
        background: rgba(10, 15, 28, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }

    /* File Uploader Glass Mode */
    [data-testid="stFileUploader"] section {
        background-color: rgba(13, 20, 36, 0.55) !important;
        backdrop-filter: blur(18px) !important;
        border: 1px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 14px !important;
        color: #e2e8f0 !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: #ef4444 !important;
        background-color: rgba(153, 27, 27, 0.08) !important;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.15) !important;
    }

    /* Streamlit Alert/Info/Warning/Success Glass Mode */
    .stAlert {
        background: rgba(13, 20, 36, 0.72) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 14px !important;
        color: #f8fafc !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3) !important;
    }

    /* =======================================================
       7. PAGE HEADER & SECTION SEPARATORS
       ======================================================= */
    .cx-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 16px;
        margin-bottom: 22px;
        position: relative;
    }

    .cx-header::after {
        content: '';
        position: absolute;
        bottom: -1px; left: 0;
        width: 140px;
        height: 2px;
        background: linear-gradient(90deg, #ef4444, #f59e0b, #38bdf8);
        border-radius: 2px;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    }

    .cx-header h1 {
        margin: 0;
        font-size: 1.95rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    }

    .cx-header p {
        margin: 4px 0 0;
        color: var(--cx-muted);
        font-size: 0.88rem;
    }

    /* Pulsing System Online Radar Badge with Double Ring */
    .cx-online-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 6px 14px;
        border-radius: 24px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #34d399;
        backdrop-filter: blur(12px);
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.15);
        position: relative;
    }

    .cx-radar-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        position: relative;
        box-shadow: 0 0 8px #10b981;
    }

    .cx-radar-dot::before {
        content: '';
        position: absolute;
        top: -4px; left: -4px; width: 16px; height: 16px;
        border-radius: 50%;
        border: 1px solid rgba(16, 185, 129, 0.8);
        animation: radar-beacon-pulse 1.8s ease-out infinite;
    }

    @keyframes radar-beacon-pulse {
        0% { transform: scale(0.5); opacity: 1; }
        100% { transform: scale(1.8); opacity: 0; }
    }

    /* Section Separator */
    .cx-section {
        color: #f8fafc;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
        border-left: 3px solid #ef4444;
        padding: 9px 16px;
        margin: 24px 0 16px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-radius: 0 10px 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        backdrop-filter: blur(10px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .cx-note {
        background: rgba(13, 20, 36, 0.65);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.18);
        padding: 16px 20px;
        color: #cbd5e1;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }

    /* Telemetry Status Capsule */
    .cx-status {
        background: rgba(13, 20, 36, 0.7);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-top: 1px solid rgba(16, 185, 129, 0.5);
        color: #34d399;
        padding: 10px 16px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.04em;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        margin-bottom: 8px;
    }

    .cx-status:hover {
        border-color: rgba(16, 185, 129, 0.6);
        background: rgba(16, 185, 129, 0.12);
        transform: translateX(4px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);
    }

    /* Status Dot in Capsule */
    .cx-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px #10b981;
        display: inline-block;
    }
    .cx-status-dot.cyan { background: #38bdf8; box-shadow: 0 0 8px #38bdf8; }
    .cx-status-dot.amber { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
    .cx-status-dot.red { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

    /* =======================================================
       8. HERO BANNER FOR DASHBOARD (HOLOGRAPHIC HUD)
       ======================================================= */
    .cx-hero-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(10, 15, 28, 0.92) 100%);
        backdrop-filter: blur(28px) saturate(200%);
        -webkit-backdrop-filter: blur(28px) saturate(200%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 20px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
        position: relative;
        overflow: hidden;
    }

    /* Ambient Holographic Glow Behind Banner */
    .cx-hero-banner::before {
        content: '';
        position: absolute;
        top: -80px;
        right: 15%;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(239, 68, 68, 0.15) 0%, transparent 70%);
        filter: blur(40px);
        pointer-events: none;
    }

    .cx-hero-banner::after {
        content: '';
        position: absolute;
        bottom: -80px;
        left: 20%;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
        filter: blur(40px);
        pointer-events: none;
    }

    .cx-hero-left {
        position: relative;
        z-index: 2;
    }

    .cx-hero-right {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
    }

    .cx-hero-title {
        font-size: 2.5rem !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .cx-hero-tagline {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        letter-spacing: 0.14em;
        color: #94a3b8;
        margin-top: 4px;
    }

    .cx-hero-telemetry {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 0.08em;
    }

    /* Live Clock Pill */
    .cx-clock-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #7dd3fc;
        font-weight: 600;
    }

    /* Glassmorphic Data Table */
    [data-testid="stDataFrame"] {
        background: rgba(13, 20, 36, 0.55) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
    }

    /* =======================================================
       9. TRANSITION RADAR SCANNER (MOTION ANIMATION)
       ======================================================= */
    .cx-page-transition-screen {
        background: rgba(8, 12, 22, 0.92);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 32px 24px;
        margin: 14px 0 22px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        animation: loader-fade-in 0.2s ease-out forwards;
    }

    @keyframes loader-fade-in {
        0% { opacity: 0; transform: scale(0.98); }
        100% { opacity: 1; transform: scale(1); }
    }

    .cx-radar-scanner-wrapper {
        position: relative;
        width: 80px;
        height: 80px;
    }

    .cx-radar-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 2px solid rgba(56, 189, 248, 0.4);
        background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(6, 9, 19, 0.95) 75%);
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }

    .cx-radar-circle::before {
        content: '';
        position: absolute;
        top: 50%; left: 0; right: 0;
        height: 1px;
        background: rgba(255, 255, 255, 0.18);
    }

    .cx-radar-circle::after {
        content: '';
        position: absolute;
        left: 50%; top: 0; bottom: 0;
        width: 1px;
        background: rgba(255, 255, 255, 0.18);
    }

    .cx-radar-ring-inner {
        position: absolute;
        top: 15px; left: 15px;
        width: 48px; height: 48px;
        border-radius: 50%;
        border: 1px dashed rgba(56, 189, 248, 0.45);
        animation: ring-counter-rotate 6s linear infinite;
    }

    @keyframes ring-counter-rotate {
        0% { transform: rotate(360deg); }
        100% { transform: rotate(0deg); }
    }

    .cx-radar-sweep {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        border-radius: 50%;
        background: conic-gradient(from 0deg, rgba(239, 68, 68, 0.9) 0deg, rgba(56, 189, 248, 0.35) 45deg, transparent 90deg, transparent 360deg);
        animation: radar-sweep-spin 1.1s linear infinite;
    }

    @keyframes radar-sweep-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .cx-radar-blip {
        position: absolute;
        top: 24px; left: 48px;
        width: 6px; height: 6px;
        background: #ef4444;
        border-radius: 50%;
        box-shadow: 0 0 10px #ef4444;
        animation: blip-pulse 1.1s ease-out infinite;
    }

    .cx-blip-2 {
        top: 50px; left: 24px;
        background: #38bdf8;
        box-shadow: 0 0 10px #38bdf8;
        animation: blip-pulse 1.1s ease-out infinite 0.55s;
    }

    @keyframes blip-pulse {
        0% { opacity: 0; transform: scale(0.6); }
        50% { opacity: 1; transform: scale(1.3); }
        100% { opacity: 0; transform: scale(0.6); }
    }

    .cx-loader-text {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        width: 100%;
        max-width: 500px;
    }

    .cx-loader-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .cx-loader-bar-track {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        overflow: hidden;
        position: relative;
    }

    .cx-loader-bar-fill {
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, #ef4444, #f59e0b, #38bdf8);
        animation: progress-slide 0.45s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }

    @keyframes progress-slide {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(0%); }
    }

    .cx-loader-status {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: var(--cx-muted);
        letter-spacing: 0.08em;
    }

    /* Page Content Smooth Entrance Reveal */
    .main .block-container {
        animation: page-content-reveal 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }

    @keyframes page-content-reveal {
        0% {
            opacity: 0;
            transform: translateY(10px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* =======================================================
       10. AUDIO EQUALIZER BARS (FOR AI ASSISTANT / VOICE)
       ======================================================= */
    .cx-audio-eq {
        display: inline-flex;
        align-items: flex-end;
        gap: 3px;
        height: 18px;
        padding: 0 4px;
    }

    .cx-eq-bar {
        width: 3px;
        background: #10b981;
        border-radius: 2px;
        animation: eq-bounce 1s ease-in-out infinite alternate;
    }

    .cx-eq-bar:nth-child(1) { height: 60%; animation-delay: 0.1s; }
    .cx-eq-bar:nth-child(2) { height: 100%; animation-delay: 0.3s; }
    .cx-eq-bar:nth-child(3) { height: 40%; animation-delay: 0.15s; }
    .cx-eq-bar:nth-child(4) { height: 80%; animation-delay: 0.4s; }
    .cx-eq-bar:nth-child(5) { height: 50%; animation-delay: 0.25s; }

    @keyframes eq-bounce {
        0% { height: 20%; }
        100% { height: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)


def brand() -> None:
    """Render the sleek animated brand identity in the sidebar."""
    st.markdown("""
    <div class="cx-brand">
      <div class="cx-brand-header">
        <div class="cx-crest-box">
          <div class="cx-crest-box-inner">CX</div>
        </div>
        <div>
          <div class="cx-brand-title">
            <span class="cx-word-crime">CRIME</span>
            <span class="cx-letter-x-box">
              <span class="cx-letter-x">X</span>
            </span>
          </div>
          <p>POLICE INTELLIGENCE &amp; ANALYTICS</p>
        </div>
      </div>
      <div class="cx-brand-badge">
        <span class="cx-brand-dot"></span>
        <span>SECURE LAW ENFORCEMENT PROTOCOL</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def hero_banner() -> None:
    """Render a prominent hero banner with dynamic motion, live clock, and tactical telemetry."""
    st.markdown("""
    <div class="cx-hero-banner">
      <div class="cx-hero-left">
        <div class="cx-brand-title cx-hero-title">
          <span class="cx-word-crime">CRIME</span>
          <span class="cx-letter-x-box">
            <span class="cx-letter-x">X</span>
          </span>
        </div>
        <div class="cx-hero-tagline">INDIA POLICE CRIME INTELLIGENCE &amp; ANALYTICS PLATFORM</div>
        <div class="cx-hero-telemetry">SECURE GRID // NCRB 2022 HISTORICAL DATALINK // REAL-TIME AI RADAR</div>
      </div>
      <div class="cx-hero-right">
        <div class="cx-online-pill">
          <span class="cx-radar-dot"></span>
          <span>COMMAND RADAR ACTIVE</span>
        </div>
        <div class="cx-clock-pill">
          <span>IST TELEMETRY // 24/7 SURVEILLANCE</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_page_transition(page_name: str) -> None:
    """Render a visible, high-tech tactical radar loading animation when switching pages."""
    placeholder = st.empty()
    placeholder.markdown(f"""
    <div class="cx-page-transition-screen">
        <div class="cx-radar-scanner-wrapper">
            <div class="cx-radar-circle">
                <div class="cx-radar-ring-inner"></div>
                <div class="cx-radar-sweep"></div>
                <div class="cx-radar-blip"></div>
                <div class="cx-radar-blip cx-blip-2"></div>
            </div>
        </div>
        <div class="cx-loader-text">
            <div class="cx-loader-title">INITIALIZING {page_name.upper()} INTELLIGENCE...</div>
            <div class="cx-loader-bar-track">
                <div class="cx-loader-bar-fill"></div>
            </div>
            <div class="cx-loader-status">SECURE POLICE PROTOCOL // SYNCHRONIZING WITH SQLITE DATASTORE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.4)
    placeholder.empty()


def page_header(title: str, subtitle: str, badge_text: str = "SYSTEM ONLINE") -> None:
    """Render a sleek page header with live status pill."""
    st.markdown(f"""
    <div class="cx-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div class="cx-online-pill">
        <span class="cx-radar-dot"></span>
        <span>{badge_text}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def section(title: str, icon: str = "") -> None:
    """Render a tactical section header with glowing indicator."""
    icon_html = f"<span>{icon}</span> " if icon else ""
    st.markdown(f'<div class="cx-section">{icon_html}{title}</div>', unsafe_allow_html=True)


def modern_kpi_card(title: str, value: str, subtitle: str = "", theme: str = "red", icon: str = "📊") -> str:
    """Return HTML for a modern frosted glass KPI card with motion hover and category theme."""
    return f"""
    <div class="cx-kpi-card theme-{theme}">
      <div class="cx-kpi-top">
        <span class="cx-kpi-label">{title}</span>
        <span class="cx-kpi-icon">{icon}</span>
      </div>
      <div class="cx-kpi-value">{value}</div>
      {f'<div class="cx-kpi-meta">{subtitle}</div>' if subtitle else ''}
    </div>
    """


def kpis(values: list[tuple[str, object]]) -> None:
    """Render standard Streamlit metrics styled with frosted glass and glowing borders."""
    columns = st.columns(len(values))
    for column, (label, value) in zip(columns, values):
        column.metric(label, value)


def records_table(records: list[dict], empty_message: str = "No data available.") -> None:
    """Render an interactive dataframe with sleek glass container styling."""
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


def empty_state(message: str) -> None:
    """Render a high-tech informational callout."""
    st.markdown(f'<div class="cx-note">{message}</div>', unsafe_allow_html=True)


def status_capsule(text: str, color: str = "emerald") -> str:
    """Generate HTML for a glowing telemetry status indicator."""
    return f'<div class="cx-status"><span class="cx-status-dot {color}"></span>{text}</div>'