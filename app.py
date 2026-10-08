import streamlit as st
from datetime import datetime
from datetime import date, time, timedelta, timezone
import json
import math
import os
from pathlib import Path
from threading import Lock
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from streamlit.errors import StreamlitSecretNotFoundError
import streamlit.components.v1 as components

st.set_page_config(page_title="GenAI Smart Traffic Assistant", page_icon="🚦", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --canvas: #f4f6f1;
        --paper: #ffffff;
        --ink: #1c3029;
        --muted: #687a72;
        --line: #e3e9e3;
        --green: #187052;
        --green-dark: #104c39;
        --mint: #e6f1e9;
        --lime: #c8e4a1;
        --amber: #ab6b15;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--canvas) !important;
        color: var(--ink) !important;
        font-family: "Aptos", "Segoe UI", Arial, sans-serif;
    }
    [data-testid="stHeader"] {
        background: rgba(244, 246, 241, 0.92) !important;
    }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stAppViewContainer"] > .main {
        background: var(--canvas) !important;
    }
    .block-container {
        padding-top: 2.4rem;
        padding-bottom: 4rem;
        padding-left: 2.4rem;
        padding-right: 2.4rem;
        max-width: 1320px;
    }
    .header-wrap {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 12px;
        margin: 0 0 0.45rem 0;
    }
    .traffic-light {
        width: 34px;
        height: 34px;
        border-radius: 11px;
        background: linear-gradient(145deg, var(--green), #31956e);
        box-shadow: 0 6px 14px rgba(24, 112, 82, 0.18);
        position: relative;
    }
    .traffic-light::before {
        content: "↗";
        position: absolute;
        inset: 0;
        display: grid;
        place-items: center;
        color: white;
        font-size: 1.45rem;
        font-weight: 800;
    }
    h1 {
        font-size: 2.25rem !important;
        font-weight: 760 !important;
        letter-spacing: -0.045em;
        margin: 0 !important;
        color: var(--ink) !important;
        text-align: left;
    }
    .subtitle {
        text-align: left;
        color: var(--muted);
        font-size: 1rem;
        margin-bottom: 0;
        font-weight: 450;
        line-height: 1.55;
    }
    .eyebrow {
        color: var(--green);
        font-size: 0.75rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .hero-panel {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1.1fr) minmax(260px, 0.9fr);
        align-items: center;
        gap: 1.2rem;
        isolation: isolate;
        overflow: hidden;
        background:
            radial-gradient(ellipse at 78% 22%, rgba(75, 179, 132, 0.28), transparent 35%),
            linear-gradient(125deg, #122a24 0%, #183b30 55%, #214c3b 100%);
        border: 1px solid rgba(180, 223, 195, 0.18);
        border-radius: 26px;
        padding: 1.8rem 2rem 1.75rem;
        margin: 0.2rem 0 1.5rem;
        box-shadow: 0 24px 55px rgba(22, 54, 40, 0.18), inset 0 1px 0 rgba(255,255,255,0.12);
    }
    .hero-panel::before {
        content: "";
        position: absolute;
        z-index: -1;
        width: 370px;
        height: 370px;
        top: -245px;
        left: -115px;
        border: 1px solid rgba(217, 245, 222, 0.11);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(217, 245, 222, 0.025), 0 0 0 58px rgba(217, 245, 222, 0.02);
    }
    .hero-copy { position: relative; z-index: 2; }
    .hero-panel .eyebrow { color: #b8df9e; }
    .hero-panel h1 { color: #f4f8f1 !important; }
    .hero-panel .subtitle { color: #cadbd0; max-width: 560px; }
    .hero-visual {
        position: relative;
        min-height: 210px;
        display: grid;
        place-items: center;
        perspective: 900px;
    }
    .route-orbit {
        position: relative;
        width: min(100%, 390px);
        height: 190px;
        transform: rotateX(54deg) rotateZ(-13deg);
        transform-style: preserve-3d;
        animation: orbit-float 7s ease-in-out infinite;
    }
    .route-orbit::before, .route-orbit::after {
        content: "";
        position: absolute;
        inset: 15% 8%;
        border: 1px solid rgba(183, 223, 193, 0.2);
        border-radius: 50%;
        transform: translateZ(-28px);
    }
    .route-orbit::after {
        inset: 25% 0;
        transform: rotateZ(53deg) translateZ(-12px);
        border-color: rgba(183, 223, 193, 0.12);
    }
    .route-grid {
        position: absolute;
        inset: 4% 0 0;
        background-image: radial-gradient(rgba(201, 231, 203, 0.32) 1px, transparent 1px);
        background-size: 23px 23px;
        mask-image: radial-gradient(ellipse, black 8%, transparent 72%);
        opacity: 0.5;
        transform: translateZ(-42px);
    }
    .route-svg {
        position: absolute;
        inset: 3%;
        width: 94%;
        height: 94%;
        overflow: visible;
        filter: drop-shadow(0 7px 8px rgba(83, 219, 153, 0.25));
        transform: translateZ(12px);
    }
    .route-line-base {
        fill: none;
        stroke: rgba(202, 237, 206, 0.25);
        stroke-width: 2.5;
        stroke-linecap: round;
        stroke-dasharray: 2 7;
    }
    .route-line-active {
        fill: none;
        stroke: #c5ed9b;
        stroke-width: 3;
        stroke-linecap: round;
        stroke-dasharray: 9 13;
        animation: route-flow 2.6s linear infinite;
    }
    .route-pin {
        fill: #f5fbef;
        stroke: #74d89e;
        stroke-width: 3;
        filter: drop-shadow(0 4px 4px rgba(6, 22, 16, 0.35));
    }
    .route-node-pulse {
        fill: rgba(171, 231, 160, 0.2);
        transform-box: fill-box;
        transform-origin: center;
        animation: node-pulse 2.4s ease-out infinite;
    }
    .hero-float-card {
        position: absolute;
        right: 2%;
        bottom: 0;
        padding: 0.65rem 0.85rem;
        color: #f3f8f0;
        background: rgba(239, 250, 238, 0.1);
        border: 1px solid rgba(235, 251, 232, 0.2);
        border-radius: 13px;
        backdrop-filter: blur(12px);
        box-shadow: 0 12px 24px rgba(4, 19, 12, 0.18);
        font-size: 0.76rem;
        letter-spacing: 0.04em;
        animation: chip-float 5s ease-in-out infinite;
    }
    .hero-float-card strong {
        display: block;
        color: #c9efa9;
        font-size: 0.66rem;
        letter-spacing: 0.13em;
        margin-bottom: 0.18rem;
    }
    @keyframes orbit-float {
        0%, 100% { transform: rotateX(54deg) rotateZ(-13deg) translateY(0); }
        50% { transform: rotateX(54deg) rotateZ(-13deg) translateY(-8px); }
    }
    @keyframes route-flow { to { stroke-dashoffset: -44; } }
    @keyframes node-pulse {
        0% { opacity: 0.8; transform: scale(0.7); }
        75%, 100% { opacity: 0; transform: scale(2.1); }
    }
    @keyframes chip-float {
        0%, 100% { transform: translateY(0) rotate(-1deg); }
        50% { transform: translateY(-6px) rotate(1deg); }
    }
    .form-panel {
        color: var(--ink) !important;
    }
    .section-title {
        color: var(--ink) !important;
        font-size: 1.05rem !important;
        font-weight: 750 !important;
        margin: 0 0 0.9rem 0 !important;
        display: flex;
        align-items: center;
        gap: 9px;
    }
    .section-title .icon {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--green);
        display: inline-block;
        box-shadow: 0 0 0 4px var(--mint);
    }
    [data-testid="stForm"] {
        background: var(--paper) !important;
        border: 1px solid var(--line) !important;
        border-radius: 20px !important;
        padding: 1.5rem 1.55rem 1.1rem !important;
        box-shadow: 0 16px 36px rgba(31, 62, 45, 0.065), 0 3px 8px rgba(31, 62, 45, 0.025);
        transition: transform 220ms ease, box-shadow 220ms ease;
    }
    [data-testid="stForm"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 42px rgba(31, 62, 45, 0.085), 0 4px 10px rgba(31, 62, 45, 0.035);
    }
    [data-testid="stForm"] [data-baseweb="select"] > div,
    [data-testid="stForm"] [data-testid="stDateInput"] input,
    [data-testid="stForm"] [data-testid="stTimeInput"] input,
    [data-testid="stForm"] [data-testid="stNumberInput"] input {
        background: #f7f9f6 !important;
        color: var(--ink) !important;
        border-color: #dce5dc !important;
        border-radius: 11px !important;
        min-height: 46px;
    }
    [data-testid="stForm"] [data-baseweb="select"] span,
    [data-testid="stForm"] input {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }
    .stSelectbox label,
    .stNumberInput label,
    .stDateInput label,
    .stTimeInput label {
        color: #42594e !important;
        font-size: 0.86rem !important;
        font-weight: 650 !important;
        margin-bottom: 0.38rem !important;
    }
    .stButton > button {
        min-height: 48px;
        border-radius: 12px;
        font-size: 0.98rem !important;
        font-weight: 720 !important;
        background: var(--green) !important;
        color: white !important;
        border: 1px solid var(--green) !important;
        box-shadow: 0 7px 16px rgba(24, 112, 82, 0.15);
        transition: background 120ms ease, transform 120ms ease;
    }
    .stButton > button:hover {
        background: var(--green-dark) !important;
        border-color: var(--green-dark) !important;
        transform: translateY(-1px);
    }
    [data-testid="stFormSubmitButton"] button {
        margin-top: 0.45rem;
        min-height: 52px;
        font-size: 1rem !important;
    }
    .result-banner {
        margin-top: 1.45rem;
        background: #eaf3ec;
        border: 1px solid #d6e7d9;
        border-left: 5px solid var(--green);
        border-radius: 16px;
        padding: 1.1rem 1.35rem;
        color: var(--ink);
    }
    .result-banner strong {
        display: inline-block;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .result-banner h3 {
        margin: 0;
        font-size: clamp(1.55rem, 2vw, 2rem);
        color: var(--ink) !important;
    }
    .result-banner p {
        margin: 0.5rem 0 0 0;
        color: #50655b;
        line-height: 1.5;
    }
    .card {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 17px;
        padding: 1.15rem 1.25rem 1rem;
        margin-top: 0.8rem;
        min-height: 165px;
        box-shadow: 0 9px 24px rgba(31, 62, 45, 0.045);
    }
    .card h4 {
        color: var(--ink);
        font-size: 1rem;
        font-weight: 720;
        margin: 0 0 0.75rem 0 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card h5 {
        margin: 0 0 0.5rem 0 !important;
        color: var(--ink);
        font-size: 0.94rem;
    }
    .badge {
        display: inline-block;
        background: var(--mint);
        color: var(--green-dark);
        border: 1px solid #d0e5d5;
        border-radius: 999px;
        padding: 0.28rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .metric {
        color: var(--ink);
        font-size: 0.98rem;
        margin-bottom: 0.45rem;
    }
    .muted {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.5;
    }
    [data-testid="stMetric"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 0.85rem 1rem;
        box-shadow: 0 10px 24px rgba(31, 62, 45, 0.055), inset 0 1px 0 #ffffff;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 30px rgba(31, 62, 45, 0.1);
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    [data-testid="stMetricValue"] { color: var(--ink) !important; }
    [data-testid="stProgress"] > div {
        background: #e3ebe4;
        border-radius: 999px;
    }
    [data-testid="stProgress"] [role="progressbar"] {
        background: var(--green) !important;
        border-radius: 999px;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
        background: var(--paper);
    }
    [data-testid="stCheckbox"] label { color: #40564b !important; }
    [data-testid="stCaptionContainer"] p { color: var(--muted); }
    [data-testid="stAlert"] { border-radius: 13px; }
    a { color: var(--green) !important; }
    [data-testid="stLinkButton"] a {
        border-radius: 11px;
    }
    .knowledge-list {
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
        margin-top: 0.45rem;
    }
    .knowledge-item {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        color: #40564b;
        line-height: 1.6;
        box-shadow: 0 7px 18px rgba(31, 62, 45, 0.035);
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    @media (max-width: 860px) {
        h1 { font-size: 1.8rem !important; }
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.2rem; }
        .hero-panel { grid-template-columns: 1fr; gap: 0; padding: 1.25rem; border-radius: 18px; }
        .hero-visual { min-height: 145px; margin-top: 0.35rem; }
        .route-orbit { height: 145px; }
        .hero-float-card { right: 3%; bottom: -2px; }
        [data-testid="stForm"] { padding: 1.1rem !important; }
    }
    @media (max-width: 560px) {
        .hero-visual { min-height: 118px; }
        .route-orbit { height: 120px; }
        .hero-float-card { font-size: 0.68rem; }
    }
    body {
        background:
            radial-gradient(ellipse at 7% 5%, rgba(201, 228, 207, 0.46), transparent 28rem),
            radial-gradient(ellipse at 96% 26%, rgba(218, 235, 220, 0.55), transparent 30rem),
            var(--canvas) !important;
    }
    .block-container {
        max-width: 1400px;
        padding-top: 1.55rem;
    }
    .hero-panel {
        min-height: 286px;
        padding: 1.55rem 2.1rem;
        background:
            radial-gradient(ellipse at 78% 20%, rgba(107, 206, 149, 0.24), transparent 34%),
            radial-gradient(ellipse at 4% 105%, rgba(69, 157, 116, 0.2), transparent 42%),
            linear-gradient(122deg, #10271f 0%, #15392c 48%, #20513b 100%);
        box-shadow: 0 28px 60px rgba(20, 55, 39, 0.2), inset 0 1px 0 rgba(255,255,255,0.14);
    }
    .hero-panel::after {
        content: "";
        position: absolute;
        z-index: -1;
        inset: 0;
        opacity: 0.18;
        background-image: radial-gradient(rgba(219, 243, 220, 0.6) 0.7px, transparent 0.7px);
        background-size: 18px 18px;
        mask-image: linear-gradient(90deg, transparent 15%, black 90%);
        pointer-events: none;
    }
    .hero-copy { max-width: 640px; }
    .hero-panel .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.42rem 0.72rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(209, 240, 200, 0.19);
        border-radius: 999px;
        background: rgba(235, 250, 233, 0.075);
        font-size: 0.68rem;
        letter-spacing: 0.15em;
    }
    .hero-panel .eyebrow::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #b8ed91;
        box-shadow: 0 0 12px rgba(184, 237, 145, 0.85);
    }
    .hero-panel h1 {
        font-size: clamp(2rem, 3.2vw, 3.15rem) !important;
        line-height: 1.08;
        letter-spacing: -0.055em;
    }
    .hero-panel .subtitle {
        max-width: 490px;
        margin-top: 0.8rem;
        font-size: 1.03rem;
    }
    .hero-visual {
        min-height: 220px;
        perspective: 1000px;
    }
    .route-orbit {
        width: min(100%, 410px);
        height: 190px;
        border: 1px solid rgba(225, 249, 221, 0.2);
        border-radius: 28px;
        background:
            linear-gradient(145deg, rgba(242, 255, 237, 0.11), rgba(227, 248, 226, 0.025)),
            repeating-linear-gradient(0deg, transparent 0 31px, rgba(218, 245, 218, 0.045) 32px),
            repeating-linear-gradient(90deg, transparent 0 31px, rgba(218, 245, 218, 0.045) 32px);
        box-shadow:
            0 28px 42px rgba(3, 20, 13, 0.23),
            inset 0 1px 0 rgba(255,255,255,0.14),
            0 0 45px rgba(114, 211, 153, 0.08);
        transform: rotateX(53deg) rotateZ(-12deg);
    }
    .route-orbit::before, .route-orbit::after {
        border-color: rgba(196, 235, 198, 0.2);
        box-shadow: 0 0 18px rgba(174, 237, 173, 0.055);
    }
    .route-grid { opacity: 0.35; }
    .route-svg { filter: drop-shadow(0 8px 12px rgba(92, 235, 158, 0.4)); }
    .route-line-active {
        stroke: #d2f5a9;
        stroke-width: 3.5;
        filter: drop-shadow(0 0 5px rgba(200, 255, 170, 0.8));
    }
    .hero-float-card {
        right: 0;
        bottom: 0.05rem;
        min-width: 172px;
        background: rgba(236, 250, 233, 0.13);
        border-color: rgba(235, 251, 232, 0.27);
        box-shadow: 0 16px 30px rgba(4, 19, 12, 0.24), inset 0 1px 0 rgba(255,255,255,0.15);
    }
    .section-title {
        margin-top: 0.4rem !important;
        font-size: 1.13rem !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stForm"] {
        border-color: #e1e9e1 !important;
        border-radius: 22px !important;
        padding: 1.45rem 1.65rem 1.2rem !important;
        box-shadow: 0 20px 48px rgba(31, 62, 45, 0.075), 0 3px 10px rgba(31, 62, 45, 0.025);
    }
    [data-testid="stForm"] [data-baseweb="select"] > div,
    [data-testid="stForm"] [data-testid="stDateInput"] input,
    [data-testid="stForm"] [data-testid="stTimeInput"] input,
    [data-testid="stForm"] [data-testid="stNumberInput"] input {
        min-height: 49px;
        border-radius: 12px !important;
        transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }
    [data-testid="stForm"] [data-baseweb="select"] > div:hover,
    [data-testid="stForm"] input:hover {
        border-color: #9abda5 !important;
        background: #fbfdfb !important;
    }
    [data-testid="stForm"] [data-baseweb="select"] > div:focus-within,
    [data-testid="stForm"] input:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 3px rgba(24, 112, 82, 0.12) !important;
    }
    [data-testid="stForm"] [data-testid="stCaptionContainer"] {
        padding: 0.66rem 0.82rem;
        margin-bottom: 0.8rem;
        border: 1px solid #e0ece2;
        border-radius: 11px;
        background: #f5f9f4;
    }
    [data-testid="stForm"] [data-testid="stCaptionContainer"] p {
        margin: 0;
        color: #5b7064 !important;
        font-size: 0.83rem;
    }
    .form-step-heading {
        display: flex;
        align-items: center;
        gap: 0.78rem;
        padding: 0.15rem 0 0.75rem;
        margin-top: 0.35rem;
        border-bottom: 1px solid #edf1ed;
    }
    .form-step-number {
        display: grid;
        flex: 0 0 34px;
        width: 34px;
        height: 34px;
        place-items: center;
        border: 1px solid #d5e8d9;
        border-radius: 11px;
        background: linear-gradient(145deg, #eff8f0, #e3f0e5);
        color: #187052;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.04em;
    }
    .form-step-copy strong {
        display: block;
        color: #1c3029;
        font-size: 0.94rem;
        font-weight: 760;
        line-height: 1.2;
    }
    .form-step-copy small {
        display: block;
        margin-top: 0.18rem;
        color: #718078;
        font-size: 0.76rem;
        line-height: 1.35;
    }
    .route-field-note {
        padding: 0.55rem 0.75rem;
        border-left: 3px solid #a8cba9;
        border-radius: 0 8px 8px 0;
        background: #f6f9f5;
        color: #65766c;
        font-size: 0.78rem;
        line-height: 1.45;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] {
        padding-top: 0.45rem;
        margin-top: 0.45rem;
        border-top: 1px solid #edf1ed;
    }
    [data-testid="stFormSubmitButton"] button {
        border-radius: 13px;
        background: linear-gradient(110deg, #187052, #208862) !important;
        color: #ffffff !important;
        box-shadow: 0 9px 20px rgba(24, 112, 82, 0.2), inset 0 1px 0 rgba(255,255,255,0.16);
        letter-spacing: 0.01em;
    }
    [data-testid="stFormSubmitButton"] button p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(110deg, #104c39, #187052) !important;
        box-shadow: 0 12px 24px rgba(24, 112, 82, 0.25);
        transform: translateY(-2px);
    }
    [data-testid="stFormSubmitButton"] button:focus-visible,
    .stButton > button:focus-visible,
    [data-testid="stLinkButton"] a:focus-visible {
        outline: 3px solid rgba(24, 112, 82, 0.34);
        outline-offset: 3px;
    }
    .result-banner {
        border-radius: 18px;
        box-shadow: 0 12px 28px rgba(31, 62, 45, 0.07);
    }
    .card {
        border-radius: 19px;
        box-shadow: 0 12px 30px rgba(31, 62, 45, 0.055), inset 0 1px 0 #fff;
        transition: transform 200ms ease, box-shadow 200ms ease;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 38px rgba(31, 62, 45, 0.1), inset 0 1px 0 #fff;
    }
    @media (max-width: 860px) {
        .block-container { padding-top: 1rem; }
        .hero-panel { min-height: 0; padding: 1.3rem 1.35rem; }
        .hero-visual { min-height: 155px; }
        .route-orbit { height: 145px; }
    }
    @media (max-width: 560px) {
        .hero-panel { padding: 1.15rem; }
        .hero-panel h1 { font-size: 1.9rem !important; }
        .hero-panel .subtitle { font-size: 0.94rem; }
        .hero-visual { min-height: 125px; }
        .route-orbit { height: 118px; border-radius: 18px; }
        .hero-float-card { right: -0.2rem; font-size: 0.66rem; }
        [data-testid="stForm"] { padding: 1rem !important; }
        .form-step-heading { gap: 0.62rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CITY_COORDINATES = {
    "Agartala": (91.2868, 23.8315),
    "Aizawl": (92.7176, 23.7271),
    "Amaravati": (80.5150, 16.5410),
    "Bhopal": (77.4126, 23.2599),
    "Bhubaneswar": (85.8245, 20.2961),
    "Hyderabad": (78.4867, 17.3850),
    "Bengaluru": (77.5946, 12.9716),
    "Chandigarh": (76.7794, 30.7333),
    "Chennai": (80.2707, 13.0827),
    "Daman": (72.8328, 20.3974),
    "Dehradun": (78.0322, 30.3165),
    "Delhi": (77.2090, 28.6139),
    "Dispur": (91.7898, 26.1433),
    "Gangtok": (88.6138, 27.3389),
    "Gandhinagar": (72.6369, 23.2156),
    "Imphal": (93.9368, 24.8170),
    "Itanagar": (93.6167, 27.0844),
    "Jaipur": (75.7873, 26.9124),
    "Kavaratti": (72.6420, 10.5667),
    "Kohima": (94.1086, 25.6751),
    "Kolkata": (88.3639, 22.5726),
    "Leh": (77.5771, 34.1526),
    "Lucknow": (80.9462, 26.8467),
    "Mumbai": (72.8777, 19.0760),
    "Panaji": (73.8278, 15.4909),
    "Patna": (85.1376, 25.5941),
    "Port Blair (Sri Vijaya Puram)": (92.7265, 11.6234),
    "Puducherry": (79.8083, 11.9416),
    "Raipur": (81.6296, 21.2514),
    "Ranchi": (85.3096, 23.3441),
    "Shillong": (91.8933, 25.5788),
    "Shimla": (77.1734, 31.1048),
    "Srinagar": (74.7973, 34.0837),
    "Thiruvananthapuram": (76.9366, 8.5241),
}

CITY_ADMIN_AREAS = {
    "Agartala": ("West Tripura", "Tripura"),
    "Aizawl": ("Aizawl", "Mizoram"),
    "Amaravati": ("Guntur", "Andhra Pradesh"),
    "Bengaluru": ("Bengaluru Urban", "Karnataka"),
    "Bhopal": ("Bhopal", "Madhya Pradesh"),
    "Bhubaneswar": ("Khordha", "Odisha"),
    "Chandigarh": ("Chandigarh", "Chandigarh"),
    "Chennai": ("Chennai", "Tamil Nadu"),
    "Daman": ("Daman", "Dadra and Nagar Haveli and Daman and Diu"),
    "Dehradun": ("Dehradun", "Uttarakhand"),
    "Delhi": ("Central Delhi", "Delhi"),
    "Dispur": ("Kamrup Metropolitan", "Assam"),
    "Gangtok": ("Gangtok", "Sikkim"),
    "Gandhinagar": ("Gandhinagar", "Gujarat"),
    "Hyderabad": ("Hyderabad", "Telangana"),
    "Imphal": ("Imphal West", "Manipur"),
    "Itanagar": ("Papum Pare", "Arunachal Pradesh"),
    "Jaipur": ("Jaipur", "Rajasthan"),
    "Kavaratti": ("Lakshadweep", "Lakshadweep"),
    "Kohima": ("Kohima", "Nagaland"),
    "Kolkata": ("Kolkata", "West Bengal"),
    "Leh": ("Leh", "Ladakh"),
    "Lucknow": ("Lucknow", "Uttar Pradesh"),
    "Mumbai": ("Mumbai City", "Maharashtra"),
    "Panaji": ("North Goa", "Goa"),
    "Patna": ("Patna", "Bihar"),
    "Port Blair (Sri Vijaya Puram)": ("South Andaman", "Andaman and Nicobar Islands"),
    "Puducherry": ("Puducherry", "Puducherry"),
    "Raipur": ("Raipur", "Chhattisgarh"),
    "Ranchi": ("Ranchi", "Jharkhand"),
    "Shillong": ("East Khasi Hills", "Meghalaya"),
    "Shimla": ("Shimla", "Himachal Pradesh"),
    "Srinagar": ("Srinagar", "Jammu and Kashmir"),
    "Thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
}

DISTRICT_DATA_PATH = Path(__file__).parent / "data" / "india_districts.json"
with DISTRICT_DATA_PATH.open(encoding="utf-8") as district_data_file:
    DISTRICT_DATA = json.load(district_data_file)

DISTRICT_COORDINATES_PATH = Path(__file__).parent / "data" / "india_district_coordinates.json"
with DISTRICT_COORDINATES_PATH.open(encoding="utf-8") as coordinates_file:
    DISTRICT_COORDINATE_DATA = json.load(coordinates_file)

DISTRICT_LOCATIONS = {
    f"{district}|{entry['state']}": (district, entry["state"])
    for entry in DISTRICT_DATA
    for district in entry["districts"]
}
INDIAN_LOCATIONS = sorted(
    DISTRICT_LOCATIONS,
    key=lambda location: (
        DISTRICT_LOCATIONS[location][1],
        DISTRICT_LOCATIONS[location][0],
    ),
)
CAPITAL_DISTRICT_ALIASES = {
    ("Central Delhi", "Delhi"): ("New Delhi", "Delhi"),
    ("Kamrup Metropolitan", "Assam"): ("Kamrup Metro", "Assam"),
    ("Lakshadweep", "Lakshadweep"): ("Lakshadweep District", "Lakshadweep"),
    ("Leh", "Ladakh"): ("Leh Ladakh", "Ladakh"),
    ("Mumbai City", "Maharashtra"): ("Mumbai", "Maharashtra"),
    ("South Andaman", "Andaman and Nicobar Islands"): (
        "South Andamans",
        "Andaman and Nicobar Islands",
    ),
}
DISTRICT_GEOCODING_ALIASES = {
    ("Ananthapuramu", "Andhra Pradesh"): ("Anantapuram",),
    ("Dr. B.R. Ambedkar Konaseema", "Andhra Pradesh"): ("Konaseema",),
}
DISTRICT_COORDINATES = {}
for location, coordinates in DISTRICT_COORDINATE_DATA["coordinates"].items():
    if location in DISTRICT_LOCATIONS:
        DISTRICT_COORDINATES[location] = tuple(coordinates)
for city, (district, state) in CITY_ADMIN_AREAS.items():
    district, state = CAPITAL_DISTRICT_ALIASES.get((district, state), (district, state))
    location = f"{district}|{state}"
    if location in DISTRICT_LOCATIONS and location not in DISTRICT_COORDINATES:
        DISTRICT_COORDINATES[location] = CITY_COORDINATES[city]


def format_location(location):
    district, state = DISTRICT_LOCATIONS[location]
    return f"{district} · {state}"


class LocationLookupError(Exception):
    pass


def normalize_location_name(value):
    return "".join(character for character in value.casefold() if character.isalnum())


def is_matching_district_result(result, district_names, state):
    if (
        not isinstance(result, dict)
        or result.get("category") != "boundary"
        or result.get("type") != "administrative"
    ):
        return False

    address = result.get("address")
    if (
        not isinstance(address, dict)
        or address.get("country_code") != "in"
        or not isinstance(address.get("state"), str)
        or normalize_location_name(address["state"]) != normalize_location_name(state)
    ):
        return False

    expected_names = {normalize_location_name(name) for name in district_names}
    administrative_name = next(
        (
            address[key]
            for key in ("state_district", "district", "county")
            if isinstance(address.get(key), str) and address[key].strip()
        ),
        None,
    )
    if isinstance(administrative_name, str):
        return normalize_location_name(administrative_name) in expected_names

    result_name = result.get("name")
    return (
        isinstance(result_name, str)
        and normalize_location_name(result_name) in expected_names
    )


_GEOCODING_LOCK = Lock()
_LAST_GEOCODING_REQUEST = 0.0


@st.cache_data(ttl=30 * 24 * 60 * 60)
def get_location_coordinates(location):
    if location in DISTRICT_COORDINATES:
        return DISTRICT_COORDINATES[location]
    district, state = DISTRICT_LOCATIONS[location]
    district_names = (district, *DISTRICT_GEOCODING_ALIASES.get((district, state), ()))
    last_lookup_error = None

    global _LAST_GEOCODING_REQUEST
    for search_name in dict.fromkeys(district_names):
        parameters = urlencode(
            {
                "q": f"{search_name}, {state}, India",
                "format": "jsonv2",
                "addressdetails": 1,
                "countrycodes": "in",
                "limit": 5,
            }
        )
        request = Request(
            f"https://nominatim.openstreetmap.org/search?{parameters}",
            headers={
                "User-Agent": (
                    "GenAI-Smart-Traffic-Assistant/1.0 "
                    "(https://github.com/mohankrishnareddymandadi7/"
                    "Gen-AI-Powered-Smart-Track-Assistant-main)"
                )
            },
        )
        with _GEOCODING_LOCK:
            delay = 1.0 - (monotonic() - _LAST_GEOCODING_REQUEST)
            if delay > 0:
                sleep(delay)
            _LAST_GEOCODING_REQUEST = monotonic()
            try:
                with urlopen(request, timeout=15) as response:
                    results = json.load(response)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
                last_lookup_error = error
                continue

        if not isinstance(results, list):
            raise LocationLookupError(
                f"The location service returned invalid data for {district}, {state}."
            )

        for result in results:
            if not is_matching_district_result(result, district_names, state):
                continue
            try:
                longitude = float(result["lon"])
                latitude = float(result["lat"])
            except (KeyError, TypeError, ValueError, OverflowError):
                continue
            if (
                math.isfinite(longitude)
                and math.isfinite(latitude)
                and -180 <= longitude <= 180
                and -90 <= latitude <= 90
            ):
                return longitude, latitude

    if last_lookup_error is not None:
        raise LocationLookupError(
            f"Unable to find a map location for {district}, {state}: {last_lookup_error}"
        ) from last_lookup_error
    raise LocationLookupError(
        f"No matching map location was found for {district}, {state}, India."
    )


WEATHER_CODE_DESCRIPTIONS = {
    0: ("Clear sky", "Clear"),
    1: ("Mainly clear", "Clear"),
    2: ("Partly cloudy", "Cloudy"),
    3: ("Overcast", "Cloudy"),
    45: ("Fog", "Fog"),
    48: ("Rime fog", "Fog"),
    51: ("Light drizzle", "Rain"),
    53: ("Moderate drizzle", "Rain"),
    55: ("Dense drizzle", "Rain"),
    56: ("Light freezing drizzle", "Rain"),
    57: ("Dense freezing drizzle", "Rain"),
    61: ("Slight rain", "Rain"),
    63: ("Moderate rain", "Rain"),
    65: ("Heavy rain", "Rain"),
    66: ("Light freezing rain", "Rain"),
    67: ("Heavy freezing rain", "Rain"),
    71: ("Slight snowfall", "Snow"),
    73: ("Moderate snowfall", "Snow"),
    75: ("Heavy snowfall", "Snow"),
    77: ("Snow grains", "Snow"),
    80: ("Slight rain showers", "Rain"),
    81: ("Moderate rain showers", "Rain"),
    82: ("Violent rain showers", "Rain"),
    85: ("Slight snow showers", "Snow"),
    86: ("Heavy snow showers", "Snow"),
    95: ("Thunderstorm", "Thunderstorm"),
    96: ("Thunderstorm with slight hail", "Thunderstorm"),
    99: ("Thunderstorm with heavy hail", "Thunderstorm"),
}


class WeatherLookupError(Exception):
    pass


@st.cache_data(ttl=900)
def get_live_weather(city, forecast_date, forecast_time):
    longitude, latitude = get_location_coordinates(city)
    parameters = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "precipitation,weather_code,wind_speed_10m"
            ),
            "hourly": (
                "temperature_2m,precipitation,precipitation_probability,"
                "weather_code,wind_speed_10m"
            ),
            "forecast_days": 16,
            "wind_speed_unit": "ms",
            "timezone": "auto",
        }
    )
    request = Request(
        f"https://api.open-meteo.com/v1/forecast?{parameters}",
        headers={"User-Agent": "GenAI-Smart-Traffic-Assistant"},
    )

    try:
        with urlopen(request, timeout=15) as response:
            weather_response = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise WeatherLookupError(
            f"Unable to contact the weather service for {city}: {error}"
        ) from error

    current = weather_response.get("current") if isinstance(weather_response, dict) else None
    required_fields = (
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "weather_code",
        "wind_speed_10m",
        "time",
    )
    if not isinstance(current, dict) or any(field not in current for field in required_fields):
        raise WeatherLookupError(f"The weather service returned incomplete data for {city}.")

    try:
        weather_code = int(current["weather_code"])
        description, category = WEATHER_CODE_DESCRIPTIONS[weather_code]
        hourly = weather_response["hourly"]
        hourly_times = hourly["time"]
        hourly_temperatures = hourly["temperature_2m"]
        hourly_precipitation_mm = hourly["precipitation"]
        hourly_precipitation = hourly["precipitation_probability"]
        hourly_codes = hourly["weather_code"]
        hourly_wind_speeds = hourly["wind_speed_10m"]
        current_time = datetime.fromisoformat(current["time"])
        hourly_start = next(
            (
                index
                for index, timestamp in enumerate(hourly_times)
                if datetime.fromisoformat(timestamp) >= current_time
            ),
            None,
        )
        if hourly_start is None:
            raise ValueError("No upcoming hourly forecast")
        outlook = []
        for index in range(hourly_start, min(hourly_start + 6, len(hourly_times))):
            hour_description, _ = WEATHER_CODE_DESCRIPTIONS[int(hourly_codes[index])]
            outlook.append(
                {
                    "Local time": hourly_times[index],
                    "Conditions": hour_description,
                    "Temperature (°C)": round(float(hourly_temperatures[index]), 1),
                    "Precipitation chance (%)": int(hourly_precipitation[index]),
                }
            )
        if not outlook:
            raise ValueError("No hourly forecast available")
        requested_forecast_time = datetime.combine(forecast_date, forecast_time)
        forecast_range_start = datetime.fromisoformat(hourly_times[0]).date()
        forecast_range_end = datetime.fromisoformat(hourly_times[-1]).date()
        same_day_forecast_indices = [
            index
            for index, timestamp in enumerate(hourly_times)
            if datetime.fromisoformat(timestamp).date() == forecast_date
        ]
        forecast_index = (
            min(
                same_day_forecast_indices,
                key=lambda index: abs(
                    (
                        datetime.fromisoformat(hourly_times[index])
                        - requested_forecast_time
                    ).total_seconds()
                ),
            )
            if same_day_forecast_indices
            else None
        )
        travel_forecast = None
        forecast_status = "outside_provider_range"
        if (
            forecast_range_start <= forecast_date <= forecast_range_end
            and forecast_index is not None
            and requested_forecast_time >= current_time
        ):
            forecast_description, forecast_category = WEATHER_CODE_DESCRIPTIONS[
                int(hourly_codes[forecast_index])
            ]
            travel_forecast = {
                "time": hourly_times[forecast_index],
                "description": forecast_description,
                "category": forecast_category,
                "temperature": float(hourly_temperatures[forecast_index]),
                "precipitation": float(hourly_precipitation_mm[forecast_index]),
                "precipitation_probability": int(
                    hourly_precipitation[forecast_index]
                ),
                "wind_speed": float(hourly_wind_speeds[forecast_index]),
            }
            forecast_status = "available"
        elif forecast_date == current_time.date() and requested_forecast_time < current_time:
            forecast_status = "departure_time_passed"
        weather = {
            "temperature": float(current["temperature_2m"]),
            "feels_like": float(current["apparent_temperature"]),
            "humidity": int(current["relative_humidity_2m"]),
            "wind_speed": float(current["wind_speed_10m"]),
            "precipitation": float(current["precipitation"]),
            "description": description,
            "category": category,
            "observed_at": current["time"],
            "timezone": weather_response["timezone"],
            "outlook": outlook,
            "travel_forecast": travel_forecast,
            "forecast_status": forecast_status,
            "forecast_range_start": forecast_range_start.isoformat(),
            "forecast_range_end": forecast_range_end.isoformat(),
        }
    except (KeyError, IndexError, TypeError, ValueError, OverflowError) as error:
        raise WeatherLookupError(
            f"The weather service returned invalid data for {city}."
        ) from error

    numeric_values = (
        weather["temperature"],
        weather["feels_like"],
        weather["wind_speed"],
        weather["precipitation"],
    )
    if (
        not all(math.isfinite(value) for value in numeric_values)
        or not 0 <= weather["humidity"] <= 100
        or weather["wind_speed"] < 0
        or weather["precipitation"] < 0
    ):
        raise WeatherLookupError(f"The weather service returned invalid measurements for {city}.")
    return weather


def build_weather_card(title, city, weather):
    weather_details = (
        f'<div class="badge">{weather["description"]}</div>'
        f'<div class="metric">Location: {city}</div>'
        f'<div class="metric">Temperature: {weather["temperature"]:.1f} °C</div>'
        f'<div class="metric">Feels Like: {weather["feels_like"]:.1f} °C</div>'
        f'<div class="metric">Humidity: {weather["humidity"]}%</div>'
        f'<div class="metric">Wind Speed: {weather["wind_speed"]:.1f} m/s</div>'
        f'<div class="metric">Precipitation: {weather["precipitation"]:.1f} mm</div>'
        f'<div class="muted">Updated: {weather["observed_at"]} ({weather["timezone"]})</div>'
    )
    return f"""
        <div class="card">
            <h4><span class='icon' style='background: linear-gradient(180deg, #5fb1ff, #7ecaff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>{title}</h4>
            {weather_details}
        </div>
    """


def build_travel_forecast_card(title, location, weather):
    forecast = weather["travel_forecast"]
    if forecast is None:
        if weather["forecast_status"] == "departure_time_passed":
            message = "The selected departure/arrival time has already passed; no forecast is shown."
        else:
            message = (
                "No forecast is available for this selected time. "
                f"Provider range: {weather['forecast_range_start']} to "
                f"{weather['forecast_range_end']} (local time)."
            )
        return f"""
            <div class="card">
                <h4>{title}</h4>
                <div class="metric">Location: {location}</div>
                <div class="muted">{message}</div>
            </div>
        """
    return f"""
        <div class="card">
            <h4>{title}</h4>
            <div class="badge">{forecast["description"]}</div>
            <div class="metric">Location: {location}</div>
            <div class="metric">Forecast time: {forecast["time"]} ({weather["timezone"]})</div>
            <div class="metric">Temperature: {forecast["temperature"]:.1f} °C</div>
            <div class="metric">Precipitation chance: {forecast["precipitation_probability"]}%</div>
            <div class="metric">Wind speed: {forecast["wind_speed"]:.1f} m/s</div>
            <div class="muted">Open-Meteo forecast · nearest model grid point</div>
        </div>
    """


class RouteLookupError(Exception):
    pass


def get_live_route(source, destination):
    start_lon, start_lat = get_location_coordinates(source)
    end_lon, end_lat = get_location_coordinates(destination)
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        "?overview=full&geometries=geojson"
    )
    request = Request(url, headers={"User-Agent": "GenAI-Smart-Traffic-Assistant"})

    try:
        with urlopen(request, timeout=15) as response:
            route_response = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RouteLookupError(f"Unable to contact the routing service: {error}") from error

    routes = route_response.get("routes")
    if route_response.get("code") != "Ok" or not routes:
        raise RouteLookupError(
            f"The routing service could not find a driving route ({route_response.get('code', 'unknown error')})."
        )

    route = routes[0]
    coordinates = route.get("geometry", {}).get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        raise RouteLookupError("The routing service returned no usable route geometry.")
    if any(
        not isinstance(point, list)
        or len(point) < 2
        or not all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in point[:2]
        )
        for point in coordinates
    ):
        raise RouteLookupError("The routing service returned invalid route coordinates.")

    return {
        "distance_km": route["distance"] / 1000,
        "duration_hours": route["duration"] / 3600,
        "coordinates": coordinates,
    }


class IncidentLookupError(Exception):
    pass


TOMTOM_INCIDENT_CATEGORIES = {
    0: "Unknown",
    1: "Accident",
    2: "Fog",
    3: "Dangerous conditions",
    4: "Rain",
    5: "Ice",
    6: "Traffic jam",
    7: "Lane closed",
    8: "Road closed",
    9: "Road works",
    10: "Wind",
    11: "Flooding",
    14: "Broken-down vehicle",
}


def get_tomtom_api_key():
    environment_key = os.environ.get("TOMTOM_API_KEY")
    if environment_key:
        return environment_key
    try:
        return st.secrets.get("TOMTOM_API_KEY")
    except StreamlitSecretNotFoundError:
        return None


def route_incident_bboxes(coordinates):
    chunks = []
    chunk = [coordinates[0]]
    chunk_distance_km = 0.0
    previous = coordinates[0]
    for point in coordinates[1:]:
        longitude_1, latitude_1 = previous[:2]
        longitude_2, latitude_2 = point[:2]
        latitude_delta = math.radians(latitude_2 - latitude_1)
        longitude_delta = math.radians(longitude_2 - longitude_1)
        haversine = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(math.radians(latitude_1))
            * math.cos(math.radians(latitude_2))
            * math.sin(longitude_delta / 2) ** 2
        )
        segment_distance_km = 6371 * 2 * math.asin(math.sqrt(haversine))
        if chunk_distance_km + segment_distance_km > 90 and len(chunk) > 1:
            chunks.append(chunk)
            chunk = [previous]
            chunk_distance_km = 0.0
        chunk.append(point)
        chunk_distance_km += segment_distance_km
        previous = point
    if len(chunk) > 1:
        chunks.append(chunk)

    boxes = []
    for points in chunks:
        latitudes = [point[1] for point in points]
        longitudes = [point[0] for point in points]
        middle_latitude = (min(latitudes) + max(latitudes)) / 2
        latitude_padding = 0.06
        longitude_padding = latitude_padding / max(
            math.cos(math.radians(middle_latitude)), 0.25
        )
        box = (
            min(longitudes) - longitude_padding,
            min(latitudes) - latitude_padding,
            max(longitudes) + longitude_padding,
            max(latitudes) + latitude_padding,
        )
        area_km2 = (
            (box[3] - box[1])
            * 111.32
            * (box[2] - box[0])
            * 111.32
            * math.cos(math.radians(middle_latitude))
        )
        if area_km2 > 10000:
            raise IncidentLookupError(
                "A route search area exceeded TomTom's 10,000 km² bounding-box limit."
            )
        boxes.append(box)
    return boxes


@st.cache_data(ttl=300)
def get_tomtom_incidents_for_bbox(api_key, bbox):
    parameters = urlencode(
        {
            "key": api_key,
            "bbox": ",".join(f"{value:.6f}" for value in bbox),
            "fields": (
                "incidents{type,geometry{type,coordinates},"
                "properties{id,iconCategory,magnitudeOfDelay,events{description}}}"
            ),
            "language": "en-GB",
            "timeValidityFilter": "present",
        }
    )
    request = Request(
        f"https://api.tomtom.com/traffic/services/5/incidentDetails?{parameters}",
        headers={"User-Agent": "GenAI-Smart-Traffic-Assistant/1.0"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise IncidentLookupError(
            f"TomTom returned HTTP {error.code} for a route-incident query."
        ) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise IncidentLookupError(
            f"Unable to retrieve route incidents from TomTom: {error}"
        ) from error
    if not isinstance(payload, dict) or not isinstance(payload.get("incidents"), list):
        raise IncidentLookupError("TomTom returned an invalid incident response.")
    return payload["incidents"]


def get_route_incidents(route, api_key):
    incidents_by_id = {}
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for bbox in route_incident_bboxes(route["coordinates"]):
        for feature in get_tomtom_incidents_for_bbox(api_key, bbox):
            if not isinstance(feature, dict):
                raise IncidentLookupError("TomTom returned a malformed incident item.")
            properties = feature.get("properties")
            geometry = feature.get("geometry")
            if not isinstance(properties, dict) or not isinstance(geometry, dict):
                raise IncidentLookupError(
                    "TomTom returned an incident without valid properties or geometry."
                )
            geometry_type = geometry.get("type")
            geometry_coordinates = geometry.get("coordinates")
            if geometry_type == "Point":
                geometry_points = [geometry_coordinates]
            elif geometry_type == "LineString":
                geometry_points = geometry_coordinates
            else:
                raise IncidentLookupError(
                    "TomTom returned an unsupported incident geometry."
                )
            if (
                not isinstance(geometry_points, list)
                or not geometry_points
                or any(
                    not isinstance(point, list)
                    or len(point) < 2
                    or not all(
                        isinstance(value, (int, float))
                        and math.isfinite(value)
                        for value in point[:2]
                    )
                    or not -180 <= point[0] <= 180
                    or not -90 <= point[1] <= 90
                    for point in geometry_points
                )
            ):
                raise IncidentLookupError(
                    "TomTom returned invalid incident coordinates."
                )
            incident_id = properties.get("id")
            if not isinstance(incident_id, (str, int)) or not incident_id:
                incident_id = json.dumps(feature, sort_keys=True, separators=(",", ":"))
            else:
                incident_id = str(incident_id)
            event_list = properties.get("events")
            description = (
                event_list[0].get("description")
                if isinstance(event_list, list)
                and event_list
                and isinstance(event_list[0], dict)
                else None
            )
            icon_category = properties.get("iconCategory")
            if not isinstance(icon_category, int) or isinstance(icon_category, bool):
                raise IncidentLookupError(
                    "TomTom returned an incident without a valid category."
                )
            incidents_by_id[incident_id] = {
                "id": incident_id,
                "category": TOMTOM_INCIDENT_CATEGORIES.get(
                    icon_category, f"Category {icon_category}"
                ),
                "description": (
                    description
                    if isinstance(description, str) and description.strip()
                    else TOMTOM_INCIDENT_CATEGORIES.get(
                        icon_category, "Traffic incident"
                    )
                ),
                "geometry": geometry,
                "magnitude_of_delay": properties.get("magnitudeOfDelay"),
                "source": "TomTom Traffic Incidents API v5",
                "retrieved_at": fetched_at,
            }
    return list(incidents_by_id.values())


def build_directions_url(source, destination):
    source_address = source.replace(" · ", ", ")
    destination_address = destination.replace(" · ", ", ")
    return "https://www.google.com/maps/dir/?" + urlencode(
        {
            "api": 1,
            "origin": f"{source_address}, India",
            "destination": f"{destination_address}, India",
            "travelmode": "driving",
            "dir_action": "navigate",
        }
    )


def build_route_map(route, source, destination, risk, incidents):
    coordinates = json.dumps(route["coordinates"], separators=(",", ":"))
    source_label = json.dumps(source, ensure_ascii=False)
    destination_label = json.dumps(destination, ensure_ascii=False)
    incident_features = json.dumps(
        [
            {
                "type": "Feature",
                "geometry": incident["geometry"],
                "properties": {
                    "category": incident["category"],
                    "description": incident["description"],
                    "source": incident["source"],
                    "retrieved_at": incident["retrieved_at"],
                },
            }
            for incident in incidents
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    route_color = "#16845e" if risk < 35 else "#c47a12" if risk < 60 else "#c34d46"
    risk_label = "Lower estimated risk" if risk < 35 else "Moderate estimated risk" if risk < 60 else "Elevated estimated risk"
    return f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
            <style>
              html, body, #map {{ height: 100%; margin: 0; }}
              .leaflet-container {{ background: #edf2ed; font-family: "Segoe UI", Arial, sans-serif; }}
              .route-legend {{
                position: absolute; z-index: 1000; right: 14px; bottom: 24px;
                padding: 10px 13px; border: 1px solid rgba(20, 50, 36, 0.12);
                border-radius: 12px; background: rgba(255, 255, 255, 0.96);
                box-shadow: 0 5px 18px rgba(19, 44, 31, 0.16); color: #1c3029;
                font-size: 12px; line-height: 1.45;
              }}
              .route-legend strong {{ display: block; margin-bottom: 2px; font-size: 12px; }}
              .route-legend span {{ color: #5d7066; }}
              .track-location-button {{
                padding: 9px 12px; border: 1px solid #c9d8cc; border-radius: 10px;
                background: #fff; color: #1c3029; font-weight: 700; cursor: pointer;
                box-shadow: 0 3px 12px rgba(19, 44, 31, 0.15);
              }}
            </style>
          </head>
          <body>
            <div id="map"></div>
            <div class="route-legend"><strong style="color:{route_color}">● {risk_label}</strong><span>Estimated risk only; incident markers are separate</span></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
              const coordinates = {coordinates};
              const incidents = {incident_features};
              const map = L.map("map");
              L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
              }}).addTo(map);
              const route = L.polyline(
                coordinates.map(([longitude, latitude]) => [latitude, longitude]),
                {{ color: "{route_color}", weight: 7, opacity: 0.88 }}
              ).addTo(map);
              L.marker([coordinates[0][1], coordinates[0][0]])
                .addTo(map)
                .bindTooltip("START · " + {source_label}, {{ permanent: true, direction: "top", offset: [0, -8] }})
                .bindPopup("<strong>Start</strong><br>" + {source_label});
              L.marker([coordinates[coordinates.length - 1][1], coordinates[coordinates.length - 1][0]])
                .addTo(map)
                .bindTooltip("DESTINATION · " + {destination_label}, {{ permanent: true, direction: "top", offset: [0, -8] }})
                .bindPopup("<strong>Destination</strong><br>" + {destination_label});
              if (incidents.length) {{
                L.geoJSON(incidents, {{
                  pointToLayer: function (_feature, latlng) {{
                    return L.circleMarker(latlng, {{
                      radius: 8, color: "#a72f2f", weight: 2, fillColor: "#e75b4f", fillOpacity: 0.9
                    }});
                  }},
                  style: {{ color: "#a72f2f", weight: 5, opacity: 0.9 }},
                  onEachFeature: function (feature, layer) {{
                    const properties = feature.properties || {{}};
                    const content = document.createElement("div");
                    const title = document.createElement("strong");
                    title.textContent = properties.category || "Traffic incident";
                    const description = document.createElement("p");
                    description.textContent = properties.description || "";
                    const source = document.createElement("small");
                    source.textContent = properties.source + " · retrieved " + properties.retrieved_at;
                    content.append(title, description, source);
                    layer.bindPopup(content);
                  }}
                }}).addTo(map);
              }}
              let locationWatchId = null;
              let userLocationMarker = null;
              const trackingControl = L.control({{ position: "topleft" }});
              trackingControl.onAdd = function () {{
                const button = L.DomUtil.create("button", "track-location-button");
                button.type = "button";
                button.textContent = "Start live location";
                L.DomEvent.disableClickPropagation(button);
                button.addEventListener("click", function () {{
                  if (locationWatchId !== null) {{
                    navigator.geolocation.clearWatch(locationWatchId);
                    locationWatchId = null;
                    button.textContent = "Start live location";
                    return;
                  }}
                  if (!navigator.geolocation) {{
                    button.textContent = "Location unavailable";
                    return;
                  }}
                  button.textContent = "Waiting for permission…";
                  locationWatchId = navigator.geolocation.watchPosition(
                    function (position) {{
                      const point = [position.coords.latitude, position.coords.longitude];
                      if (!userLocationMarker) {{
                        userLocationMarker = L.circleMarker(point, {{
                          radius: 9, color: "#1268c4", weight: 3, fillColor: "#6bb6ff", fillOpacity: 0.95
                        }}).addTo(map);
                        userLocationMarker.bindTooltip("Your device location");
                      }} else {{
                        userLocationMarker.setLatLng(point);
                      }}
                      map.panTo(point);
                      button.textContent = "Stop live location";
                    }},
                    function (error) {{
                      const messages = {{
                        1: "Location permission denied",
                        2: "Device location unavailable",
                        3: "Location request timed out"
                      }};
                      button.textContent = messages[error.code] || "Location failed";
                      locationWatchId = null;
                    }},
                    {{ enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 }}
                  );
                }});
                return button;
              }};
              trackingControl.addTo(map);
              window.addEventListener("beforeunload", function () {{
                if (locationWatchId !== null && navigator.geolocation) {{
                  navigator.geolocation.clearWatch(locationWatchId);
                }}
              }});
              map.fitBounds(route.getBounds(), {{ padding: [24, 24] }});
            </script>
          </body>
        </html>
    """


def build_knowledge_items(result):
    knowledge_path = Path(__file__).parent / "data" / "safety_guidance.json"
    with knowledge_path.open(encoding="utf-8") as knowledge_file:
        knowledge_items = json.load(knowledge_file)

    query_tags = {"always"}
    road_condition = result["road_condition"].casefold()
    if road_condition in {"rain", "wet", "fog", "flooded"}:
        query_tags.add(road_condition)
    if result["traffic_density"] == "High":
        query_tags.update({"congestion", "incident"})
    if result["risk"] >= 60:
        query_tags.add("high-risk")
    if result["departure_time"].hour < 6 or result["departure_time"].hour >= 19:
        query_tags.add("night")

    for weather_key in ("weather", "destination_weather"):
        forecast = result[weather_key]["travel_forecast"]
        if forecast is None:
            continue
        weather_tag = forecast["category"].casefold()
        if weather_tag in {"rain", "fog", "thunderstorm", "snow"}:
            query_tags.add(weather_tag)
        if forecast["precipitation"] > 0 and weather_tag == "rain":
            query_tags.add("wet")
        if weather_tag == "thunderstorm":
            query_tags.add("rain")

    ranked_items = []
    for item in knowledge_items:
        matched_tags = query_tags.intersection(item["tags"])
        if matched_tags:
            score = sum(5 if tag != "always" else 1 for tag in matched_tags)
            ranked_items.append((score, item))
    ranked_items.sort(key=lambda entry: entry[0], reverse=True)
    return [item for _, item in ranked_items[:5]]


def analyze_trip(
    source,
    destination,
    vehicle_count,
    avg_speed,
    traffic_density,
    road_condition,
    weather_city,
    travel_date,
    departure_time,
):
    route = get_live_route(source, destination)
    arrival_datetime = datetime.combine(travel_date, departure_time) + timedelta(
        hours=route["duration_hours"]
    )
    weather = get_live_weather(weather_city, travel_date, departure_time)
    destination_weather = get_live_weather(
        destination,
        arrival_datetime.date(),
        arrival_datetime.time().replace(second=0, microsecond=0),
    )
    risk_score = 0

    if traffic_density == "High":
        risk_score += 30
    elif traffic_density == "Medium":
        risk_score += 18

    if avg_speed < 50:
        risk_score += 18
    elif avg_speed < 70:
        risk_score += 10

    if vehicle_count > 150:
        risk_score += 16
    elif vehicle_count > 80:
        risk_score += 8

    condition = road_condition.lower()
    if condition in {"rain", "wet", "fog", "flooded"}:
        risk_score += 20 if condition != "wet" else 12

    departure_forecast = weather["travel_forecast"]
    if departure_forecast is not None:
        if departure_forecast["category"] in {"Rain", "Cloudy"}:
            risk_score += 8
        elif departure_forecast["category"] in {"Fog", "Snow", "Thunderstorm"}:
            risk_score += 20

    if risk_score >= 60:
        status = "Travel with caution"
        message = "The entered conditions and available travel-time forecast indicate elevated planning risk. Allow additional time, maintain a safe following distance and drive carefully."
        tone = "warning"
    elif risk_score >= 35:
        status = "Proceed with attention"
        message = "Overall route conditions are manageable, but intermittent congestion and weather changes may affect comfort and safety."
        tone = "notice"
    else:
        status = "Travel is smooth"
        message = "No elevated planning signals were detected from the information provided and available forecast. Check current local advisories before travelling."
        tone = "good"

    risk_score = min(risk_score, 100)

    return {
        "route": route,
        "weather": weather,
        "destination_weather": destination_weather,
        "weather_city": weather_city,
        "travel_date": travel_date,
        "departure_time": departure_time,
        "arrival_datetime": arrival_datetime,
        "risk": risk_score,
        "status": status,
        "message": message,
        "tone": tone,
        "source": source,
        "destination": destination,
        "traffic_density": traffic_density,
        "road_condition": road_condition,
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
    }


def build_safety_checklist(result):
    checklist = [
        "Check that your phone is charged and navigation is ready before departure.",
        "Wear your seat belt and keep a safe following distance.",
    ]
    forecast = result["weather"]["travel_forecast"]
    if forecast is not None and forecast["category"] == "Fog":
        checklist.append("Use low-beam headlights in fog and avoid sudden lane changes.")
    elif forecast is not None and forecast["category"] in {"Rain", "Thunderstorm"}:
        checklist.append("Slow down on wet roads, use headlights, and avoid flooded sections.")
    elif forecast is not None and forecast["category"] == "Snow":
        checklist.append("Check for slippery road conditions and consider delaying travel if visibility is poor.")
    if result["road_condition"].lower() in {"wet", "rain", "fog", "flooded"}:
        checklist.append("Allow extra braking distance for the selected road condition.")
    if result["risk"] >= 60:
        checklist.append("Conditions are elevated-risk; consider postponing or checking local advisories.")
    return checklist


def build_trip_challenges(result):
    challenges = []
    if result["traffic_density"] == "High":
        challenges.append(
            (
                "High selected traffic density",
                "Congestion may mean slower progress and stop-and-go driving.",
                "Allow extra time and keep a safe following distance.",
            )
        )
    elif result["traffic_density"] == "Medium":
        challenges.append(
            (
                "Medium selected traffic density",
                "Some congestion or slowdowns may affect the journey.",
                "Keep your schedule flexible and follow current road signs.",
            )
        )

    if result["avg_speed"] < 50:
        challenges.append(
            (
                "Low planned average speed",
                "The trip may take longer than the routing estimate.",
                "Allow more travel time; do not compensate by speeding.",
            )
        )
    elif result["avg_speed"] < 70:
        challenges.append(
            (
                "Moderate planned average speed",
                "The trip may take longer than the routing estimate.",
                "Keep your schedule flexible and take breaks as needed.",
            )
        )

    if result["vehicle_count"] > 150:
        challenges.append(
            (
                "High vehicle count entered",
                "A busier traffic environment can increase delays and driver workload.",
                "Plan for delays and avoid distractions.",
            )
        )
    elif result["vehicle_count"] > 80:
        challenges.append(
            (
                "Elevated vehicle count entered",
                "Traffic interactions may be more frequent.",
                "Stay alert and maintain a safe following distance.",
            )
        )

    condition = result["road_condition"].lower()
    condition_challenges = {
        "rain": (
            "Rain selected as the road condition",
            "Wet-road grip and visibility may be reduced.",
            "Slow down, use headlights, and avoid flooded sections.",
        ),
        "wet": (
            "Wet road selected",
            "Braking distance may increase on wet surfaces.",
            "Increase following distance and brake gently.",
        ),
        "fog": (
            "Fog selected as the road condition",
            "Visibility may be reduced.",
            "Use low-beam headlights and avoid sudden lane changes.",
        ),
        "flooded": (
            "Flooded road selected",
            "Floodwater can hide road damage and become unsafe quickly.",
            "Do not drive through floodwater; stop and use a safe alternative.",
        ),
    }
    if condition in condition_challenges:
        challenges.append(condition_challenges[condition])

    weather = result["weather"]
    weather_forecast = weather["travel_forecast"]
    weather_location = format_location(result["weather_city"])
    if weather_forecast is not None and weather_forecast["category"] in {"Rain", "Thunderstorm"}:
        challenges.append(
            (
                f"{weather_forecast['category']} forecast near {weather_location}",
                "The travel-time forecast may indicate reduced visibility or road grip near this weather point.",
                "Reduce speed, use headlights, and check local conditions before departure.",
            )
        )
    elif weather_forecast is not None and weather_forecast["category"] == "Fog":
        challenges.append(
            (
                f"Fog forecast near {weather_location}",
                "Fog may reduce visibility near the selected weather point at the forecast time.",
                "Use low beams, increase following distance, and delay travel if visibility is unsafe.",
            )
        )
    elif weather_forecast is not None and weather_forecast["category"] == "Snow":
        challenges.append(
            (
                f"Snow forecast near {weather_location}",
                "Snow may make roads slippery near the selected weather point at the forecast time.",
                "Check local advisories and consider delaying travel if conditions are unsafe.",
            )
        )
    elif weather_forecast is not None and weather_forecast["category"] == "Cloudy":
        challenges.append(
            (
                f"Cloudy weather forecast near {weather_location}",
                "Cloud cover is forecast at the selected weather point, not along the entire route.",
                "Check the latest local forecast along your route before departure.",
            )
        )

    destination_forecast = result["destination_weather"]["travel_forecast"]
    if (
        destination_forecast is not None
        and destination_forecast["category"] in {"Rain", "Thunderstorm", "Fog", "Snow"}
    ):
        challenges.append(
            (
                f"{destination_forecast['category']} forecast near destination",
                f"{destination_forecast['category']} is forecast near {format_location(result['destination'])} at the estimated arrival time.",
                "Check the destination forecast and local advisories before arrival.",
            )
        )
    return challenges


def build_trip_report(
    result, travel_date, departure_time, incidents, incident_status, incident_error
):
    weather = result["weather"]
    destination_weather = result["destination_weather"]
    lines = [
        "SMART TRAFFIC ASSISTANT — TRIP BRIEF",
        "=" * 44,
        "",
        "YOUR JOURNEY",
        "-" * 44,
        f"From: {format_location(result['source'])}",
        f"To: {format_location(result['destination'])}",
        f"Travel date: {travel_date.strftime('%A, %d %B %Y')}",
        f"Departure time: {departure_time.strftime('%I:%M %p')}",
        f"Route distance: {result['route']['distance_km']:.1f} km",
        f"Estimated driving time: {result['route']['duration_hours']:.1f} hours",
        "",
        "TRIP CONDITIONS",
        "-" * 44,
        f"Overall planning assessment: {result['status']}",
        f"Estimated risk score: {result['risk']} / 100",
        "This is a planning estimate based on the information entered and the",
        "travel-time forecast when available. It is not a safety guarantee.",
        f"Traffic level entered: {result['traffic_density']}",
        f"Vehicle count entered: {result['vehicle_count']}",
        f"Average speed entered: {result['avg_speed']} km/h",
        f"Road condition entered: {result['road_condition']}",
        "",
        "POTENTIAL CHALLENGES AND WHAT TO DO",
        "-" * 44,
    ]
    challenges = build_trip_challenges(result)
    if challenges:
        for index, (title, detail, action) in enumerate(challenges, start=1):
            lines.extend(
                [
                    f"{index}. {title}",
                    f"   What this could mean: {detail}",
                    f"   Recommended action: {action}",
                ]
            )
    else:
        lines.extend(
            [
                "No elevated challenges were identified from the information entered",
                "and available travel-time forecast. Check official and local travel",
                "advisories; no result is a guarantee of safe conditions.",
            ]
        )
    lines.extend(
        [
            "",
            "TRAVEL-TIME FORECAST",
            "-" * 44,
            f"Departure forecast point: {format_location(result['weather_city'])}",
            f"Forecast for: {travel_date.isoformat()} at {departure_time.strftime('%I:%M %p')} local time",
        ]
    )
    if weather["travel_forecast"] is not None:
        forecast = weather["travel_forecast"]
        lines.append(
            f"Conditions: {forecast['description']}, {forecast['temperature']:.1f} °C, "
            f"rain chance {forecast['precipitation_probability']}%, "
            f"wind {forecast['wind_speed']:.1f} m/s."
        )
    else:
        lines.append(
            f"Unavailable for this requested time. Open-Meteo returned "
            f"{weather['forecast_range_start']} through {weather['forecast_range_end']} "
            "for this location."
        )
    lines.append(
        f"Estimated destination arrival: {result['arrival_datetime'].strftime('%A, %d %B %Y %I:%M %p')} "
        f"({destination_weather['timezone']})."
    )
    if destination_weather["travel_forecast"] is not None:
        forecast = destination_weather["travel_forecast"]
        lines.append(
            f"Destination forecast: {forecast['description']}, "
            f"{forecast['temperature']:.1f} °C, rain chance "
            f"{forecast['precipitation_probability']}%."
        )
    else:
        lines.append(
            f"Destination forecast unavailable for the estimated arrival time. "
            f"Provider range: {destination_weather['forecast_range_start']} through "
            f"{destination_weather['forecast_range_end']}."
        )
    lines.extend(
        [
            "Source: Open-Meteo forecast API; nearest forecast model grid point.",
            "",
            "WEATHER SNAPSHOTS",
            "-" * 44,
            "Current observations are shown for context only; they are not substituted",
            "for an unavailable travel-date forecast.",
            (
                f"Selected weather point ({format_location(result['weather_city'])}): "
                f"{weather['description']}, {weather['temperature']:.1f} °C, "
                f"wind {weather['wind_speed']:.1f} m/s, "
                f"precipitation {weather['precipitation']:.1f} mm."
            ),
            (
                f"Destination ({format_location(result['destination'])}): "
                f"{destination_weather['description']}, "
                f"{destination_weather['temperature']:.1f} °C, "
                f"wind {destination_weather['wind_speed']:.1f} m/s, "
                f"precipitation {destination_weather['precipitation']:.1f} mm."
            ),
            f"Weather observed at: {weather['observed_at']} ({weather['timezone']})",
            "",
            "SIX-HOUR WEATHER OUTLOOK (SELECTED WEATHER POINT)",
            "-" * 44,
        ]
    )
    for forecast in weather["outlook"]:
        lines.append(
            " | ".join(
                (
                    forecast["Local time"],
                    forecast["Conditions"],
                    f"{forecast['Temperature (°C)']:.1f} °C",
                    f"Rain chance {forecast['Precipitation chance (%)']}%",
                )
            )
        )
    lines.extend(
        [
            "",
            "SAFETY CHECKLIST",
            "-" * 44,
            *[f"[ ] {item}" for item in build_safety_checklist(result)],
            "",
            "MAP AND DATA LIMITS",
            "-" * 44,
            "The map line color represents a heuristic planning-risk estimate;",
            "TomTom markers are separate provider-reported incidents with fetch times.",
            "Incident coverage may be incomplete and does not identify every hazard.",
            "Weather forecasts are point forecasts and do not describe every route section.",
            "Check official local weather, police, road authority, and emergency",
            "advisories before and during travel. Follow signs and local authorities.",
            "",
            "Route and distance: OSRM / OpenStreetMap contributors.",
            "Weather: Open-Meteo. Incidents: TomTom Traffic Incidents API v5.",
            "District points: geoBoundaries IND ADM2 / Pathways Data Pvt. Ltd.; approximate.",
            "",
        ]
    )
    lines.extend(["", "LIVE ROUTE INCIDENTS", "-" * 44])
    if incident_status == "not_configured":
        lines.append("Unavailable: configure TOMTOM_API_KEY to enable incident checks.")
    elif incident_status == "error":
        lines.append(f"Unavailable: {incident_error}")
    elif incidents:
        for incident in incidents:
            lines.append(
                f"{incident['category']}: {incident['description']} "
                f"(Source: {incident['source']}; retrieved {incident['retrieved_at']})."
            )
    else:
        lines.append(
            "No incidents were returned for the checked route corridor at retrieval time."
        )
    lines.extend(["A no-results response is not proof that the route is incident-free.", ""])
    lines.extend(["RETRIEVED SAFETY GUIDANCE", "-" * 44])
    for item in build_knowledge_items(result):
        lines.extend(
            [
                f"{item['title']}: {item['advice']}",
                f"Source: {item['source_title']} — {item['source_url']}",
            ]
        )
    lines.extend(
        [
            "",
            "LIVE INCIDENT SOURCE",
            "-" * 44,
            "TomTom Traffic Incidents API v5. Results reflect fetched provider data and",
            "may be incomplete or delayed; verify official advisories and road signs.",
            "The optional device-location marker is shown only in the browser after",
            "the user grants location permission; location is not sent to the app.",
            "",
        ]
    )
    return "\n".join(lines)


with st.container():
    st.markdown(
        '<div class="hero-panel"><div class="hero-copy">'
        '<div class="eyebrow">SMART MOBILITY · INDIA</div>'
        '<div class="header-wrap"><div class="traffic-light"></div>'
        '<h1>Smart Traffic Assistant</h1></div>'
        '<div class="subtitle">Plan with route intelligence, local weather, and a practical safety brief.</div>'
        '</div><div class="hero-visual" aria-hidden="true"><div class="route-orbit">'
        '<div class="route-grid"></div>'
        '<svg class="route-svg" viewBox="0 0 420 210" role="presentation">'
        '<path class="route-line-base" d="M42 145 C88 38 130 182 187 100 S273 34 315 112 366 170 388 62"/>'
        '<path class="route-line-active" d="M42 145 C88 38 130 182 187 100 S273 34 315 112 366 170 388 62"/>'
        '<circle class="route-node-pulse" cx="42" cy="145" r="11"/>'
        '<circle class="route-pin" cx="42" cy="145" r="6"/>'
        '<circle class="route-node-pulse" cx="388" cy="62" r="11" style="animation-delay:1.1s"/>'
        '<circle class="route-pin" cx="388" cy="62" r="6"/>'
        '<circle cx="187" cy="100" r="4" fill="#d9edbf"/>'
        '<circle cx="315" cy="112" r="4" fill="#d9edbf"/>'
        '</svg></div><div class="hero-float-card"><strong>ROUTE INTELLIGENCE</strong>784 districts · India</div></div></div>',
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="icon"></span>Plan your journey</div>', unsafe_allow_html=True)

        with st.form("trip_form"):
            st.markdown(
                '<div class="form-step-heading"><span class="form-step-number">01</span>'
                '<div class="form-step-copy"><strong>Choose your route</strong>'
                '<small>Pick a starting district and destination.</small></div></div>',
                unsafe_allow_html=True,
            )
            route_col1, route_col2 = st.columns(2)
            with route_col1:
                source = st.selectbox(
                    "Source",
                    INDIAN_LOCATIONS,
                    index=INDIAN_LOCATIONS.index("Hyderabad|Telangana"),
                    format_func=format_location,
                )
            with route_col2:
                destination = st.selectbox(
                    "Destination",
                    INDIAN_LOCATIONS,
                    index=INDIAN_LOCATIONS.index("Mumbai|Maharashtra"),
                    format_func=format_location,
                )
            st.markdown(
                '<div class="route-field-note">Type a district or state name in either box to search. '
                'District map points are approximate and may not be district headquarters.</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="form-step-heading"><span class="form-step-number">02</span>'
                '<div class="form-step-copy"><strong>Set your timing</strong>'
                '<small>Choose when you plan to leave.</small></div></div>',
                unsafe_allow_html=True,
            )
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                travel_date = st.date_input("Travel Date", value=datetime.now().date(), min_value=datetime(2024, 1, 1).date(), max_value=datetime(2030, 12, 31).date())
            with time_col2:
                departure_time = st.time_input("Departure Time", value=datetime.strptime("08:00", "%H:%M").time())

            st.markdown(
                '<div class="form-step-heading"><span class="form-step-number">03</span>'
                '<div class="form-step-copy"><strong>Add driving conditions</strong>'
                '<small>These details personalize your planning risk estimate.</small></div></div>',
                unsafe_allow_html=True,
            )
            driving_col1, driving_col2 = st.columns(2)
            with driving_col1:
                vehicle_count = st.number_input("Vehicles on route (estimate)", min_value=10, max_value=500, value=100, step=10, help="Approximate traffic volume for your journey; this is used as an estimate, not a live vehicle count.")
                avg_speed = st.number_input("Average Speed (km/h)", min_value=0, max_value=200, value=80, step=5)
                traffic_density = st.selectbox("Traffic Density", ["Low", "Medium", "High"], index=0)
            with driving_col2:
                road_condition = st.selectbox("Road Condition", ["Dry", "Wet", "Rain", "Fog", "Flooded"], index=0)
                weather_city = st.selectbox(
                    "Weather District",
                    INDIAN_LOCATIONS,
                    index=INDIAN_LOCATIONS.index("Hyderabad|Telangana"),
                    format_func=format_location,
                    help="Current weather and a forecast for your selected departure time are checked for this district and your destination.",
                )

            submit = st.form_submit_button("Build my trip plan", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        try:
            result = analyze_trip(
                source,
                destination,
                vehicle_count,
                avg_speed,
                traffic_density,
                road_condition,
                weather_city,
                travel_date,
                departure_time,
            )
        except RouteLookupError as error:
            st.error(f"Could not load the live driving route. {error}")
            st.stop()
        except WeatherLookupError as error:
            st.error(f"Could not load weather data. {error}")
            st.stop()
        except LocationLookupError as error:
            st.error(f"Could not locate a selected district. {error}")
            st.stop()

        incident_error = None
        incident_key = get_tomtom_api_key()
        incidents = []
        incident_status = "not_configured"
        incident_box_count = 0
        if incident_key:
            incident_status = "available"
            try:
                incident_box_count = len(
                    route_incident_bboxes(result["route"]["coordinates"])
                )
                with st.spinner("Checking live traffic incidents along the route..."):
                    incidents = get_route_incidents(result["route"], incident_key)
            except IncidentLookupError as error:
                incident_status = "error"
                incident_error = str(error)

        status_color = {"Travel with caution": "#f5c86a", "Proceed with attention": "#f0b56d", "Travel is smooth": "#7ae0ba"}

        st.markdown(
            f"""
            <div class="result-banner">
                <strong style="color:{status_color[result['status']]};">{result['status'].upper()}</strong>
                <h3>{result['status']}</h3>
                <p>{result['message']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(4)
        metric_cols[0].metric("Route distance", f"{result['route']['distance_km']:.1f} km")
        metric_cols[1].metric("Estimated drive", f"{result['route']['duration_hours']:.1f} hr")
        metric_cols[2].metric("Risk index", f"{result['risk']} / 100")
        metric_cols[3].metric("Weather at", format_location(result["weather_city"]))
        st.progress(result["risk"], text="Trip risk index · heuristic estimate, not a live traffic score")

        st.markdown(
            '<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Potential Challenges &amp; Precautions</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Weather challenges use the forecast for the selected departure/arrival time when available. "
            "Entered driving conditions are planning signals; only separately sourced incident markers are reported as incidents."
        )
        trip_challenges = build_trip_challenges(result)
        if trip_challenges:
            for title, detail, action in trip_challenges:
                st.warning(f"**{title}**  \n{detail}  \n**What to do:** {action}")
        else:
            st.success(
                "No elevated challenges were identified from the entered details and available travel-time forecasts. "
                "This is not a guarantee of safe conditions; check local advisories."
            )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #3ad1a3, #57d3ff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Route Information</h4>
                    <div class='metric'>Source: <span class='muted'>{format_location(source)}</span></div>
                    <div class='metric'>Destination: <span class='muted'>{format_location(destination)}</span></div>
                    <div class='metric'>Distance: <span class='muted'>{result['route']['distance_km']:.1f} km</span></div>
                    <div class='metric'>Estimated Duration: <span class='muted'>{result['route']['duration_hours']:.1f} hours</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #4ad38d, #6ce2c5); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Traffic Analysis</h4>
                    <div class='badge'>{result['traffic_density'].upper()}</div>
                    <div class='metric'>Vehicles: <span class='muted'>{result['vehicle_count']}</span></div>
                    <div class='metric'>Average Speed: <span class='muted'>{result['avg_speed']} km/h</span></div>
                    <div class='metric'>Density: <span class='muted'>{result['traffic_density']}</span></div>
                    <div class='muted'>Road condition: {result['road_condition']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Driving Route &amp; Risk Overview</div>', unsafe_allow_html=True)
        if incident_status == "not_configured":
            st.info(
                "Live incident markers are disabled because TOMTOM_API_KEY is not configured. "
                "Add the key using the README instructions; no estimated hazard is shown as a confirmed incident."
            )
        elif incident_status == "error":
            st.error(f"Live incident lookup failed. {incident_error}")
        elif incidents:
            st.caption(
                f"TomTom returned {len(incidents)} current incident(s) from "
                f"{incident_box_count} route-corridor searches. Each marker is a provider-reported item, "
                "not a model estimate; confirm conditions with authorities."
            )
        else:
            st.info(
                f"TomTom returned no current incidents in {incident_box_count} checked route-corridor areas. "
                "Coverage can be incomplete; this does not establish that the route is incident-free."
            )
        st.caption(
            "The route line color is a heuristic planning-risk estimate. Click “Start live location” "
            "on the map to share location with this browser view only; the app does not receive or store it."
        )
        components.html(
            build_route_map(
                result["route"],
                format_location(source),
                format_location(destination),
                result["risk"],
                incidents,
            ),
            height=480,
            scrolling=False,
        )
        for incident in incidents:
            st.warning(f"**{incident['category']}** — {incident['description']}")
            st.caption(
                f"Source: {incident['source']} · Retrieved: {incident['retrieved_at']}"
            )
        directions_url = build_directions_url(
            format_location(source),
            format_location(destination),
        )
        st.link_button("Open turn-by-turn directions", directions_url, icon="🧭")

        st.caption("Current observations and 16-day forecasts are provided by Open-Meteo and cached for up to 15 minutes. Forecasts may represent the nearest model grid point.")
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown(
                build_weather_card(
                    "Weather Snapshot",
                    format_location(result["weather_city"]),
                    result["weather"],
                ),
                unsafe_allow_html=True,
            )

        with col_d:
            st.markdown(
                build_weather_card(
                    "Destination Weather",
                    format_location(destination),
                    result["destination_weather"],
                ),
                unsafe_allow_html=True,
            )
        st.markdown(
            '<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Forecast for Your Travel Time</div>',
            unsafe_allow_html=True,
        )
        forecast_cols = st.columns(2)
        with forecast_cols[0]:
            st.markdown(
                build_travel_forecast_card(
                    "Departure forecast",
                    format_location(result["weather_city"]),
                    result["weather"],
                ),
                unsafe_allow_html=True,
            )
        with forecast_cols[1]:
            st.markdown(
                build_travel_forecast_card(
                    "Estimated arrival forecast",
                    format_location(destination),
                    result["destination_weather"],
                ),
                unsafe_allow_html=True,
            )
        st.markdown('<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Next 6 Hours · Weather Location</div>', unsafe_allow_html=True)
        st.dataframe(result["weather"]["outlook"], use_container_width=True, hide_index=True)

        col_e, col_f = st.columns(2)
        with col_e:
            st.markdown('<div class="section-title"><span class="icon"></span>Personalized Safety Checklist</div>', unsafe_allow_html=True)
            for item in build_safety_checklist(result):
                st.checkbox(item, key=f"safety_check_{item}")
        with col_f:
            st.markdown('<div class="section-title"><span class="icon"></span>Save Trip Brief</div>', unsafe_allow_html=True)
            st.write(
                "Download a plain-language trip brief with the route summary, possible challenges, "
                "weather snapshots, and a printable safety checklist. No JSON or code."
            )
            st.download_button(
                "Download readable trip brief (.txt)",
                data=build_trip_report(
                    result,
                    travel_date,
                    departure_time,
                    incidents,
                    incident_status,
                    incident_error,
                ),
                file_name=f"trip-brief-{travel_date:%Y%m%d}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        st.markdown(
            '<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Retrieved Safety Guidance</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Relevant entries are retrieved from a small, locally curated source set "
            "by matching your road condition, traffic, weather forecast, and departure time."
        )
        knowledge_items = build_knowledge_items(result)
        for item in knowledge_items:
            st.info(f"**{item['title']}**  \n{item['advice']}  \nSource: [{item['source_title']}]({item['source_url']})")

    else:
        st.caption("Choose your route, timing, and driving conditions, then build your trip plan.")
