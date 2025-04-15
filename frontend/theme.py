import streamlit as st

def set_custom_theme():
    st.markdown("""
    <style>
    /* Main background */
    .main, .block-container {
        background-color: #FDFAF6;
        color: #030303;
    }

    /* All text */
    html, body, p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #030303;
        font-family: 'Verdana', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #9ACBD0;
        color: #030303;
    }

    /* Generic buttons (e.g., Add Submission, Add Exam) */
    .stButton > button {
        background-color: #FCB454 !important;
        color: #ffffff !important;
        border-radius: 10px;
        padding: 10px 16px;
        border: none;
        font-weight: bold;
    }

    /* Submit button (use custom class to differentiate it) */
    .form-submit-btn > button {
        background-color: #1DCD9F !important;
        color: black !important;
        border-radius: 10px;
        padding: 10px 16px;
        border: none;
    }

    /* Tabs */
    div[data-baseweb="tab"] {
        background-color: #123458 !important;
        color: #F2EFE7 !important;
        border-radius: 10px;
        padding: 10px 16px;
    }

    /* Active tab hover */
    div[data-baseweb="tab"]:hover {
        background-color: #0E2B45 !important;
    }

    /* Inputs (text fields, date pickers, etc.) */
    input, textarea {
        background-color: #CAE0BC !important;
        color: #030303;
    }

    /* Dataframes and tables */
    .css-1l269bu {
        background-color: #F1EFEC !important;
    }
    </style>
    """, unsafe_allow_html=True)
