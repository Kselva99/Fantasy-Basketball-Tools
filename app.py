import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page Setup
st.set_page_config(
    page_title="Fantasy Basketball Category Analyzer",
    layout="wide",
)

# Sidebar Title and LinkedIn Hyperlink
st.sidebar.title("Fantasy Basketball 9CAT Analyzer")

linkedin_url = "https://www.linkedin.com/in/karthik-selvaraj-purdue/"
linkedin_html = f"""
<div style="display: flex; align-items: center;  margin-bottom: 20px;">
    <span style='font-size:14px; margin-right: 5px;'>Developed by </span>
    <a href="{linkedin_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none;">
        <span style='font-size:14px;'>Karthik Selvaraj</span>
    </a>
</div>
"""
st.sidebar.markdown(linkedin_html, unsafe_allow_html=True)

# Sidebar Navigation
# page = st.sidebar.selectbox("Tools", ["Player Comparison", "Drafting Strategy"], index=0)
page = "Player Comparison"

# Player Comparison Tool
if page == "Player Comparison":
    st.title("NBA 9CAT Fantasy Player Comparison")
    
    # Sidebar Inputs
    st.sidebar.subheader("Comparison Inputs")
    player1_comp = st.sidebar.selectbox("Player 1", ["Test Player 1", "Test Player 2"])
    player2_comp = st.sidebar.selectbox("Player 2", ["Test Player 3", "Test Player 4"])

    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Trade Tool Inputs")

    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Ranking Inputs")


    # Comparison Code
    categories = ["FGM/FGA", "FG%", "FTM/FTA", "FT%", "3PTM", "PTS", "REB", "AST", "STL", "BLK", "TOV"]

    stats1 = [27.1, 7.4, 7.4, 1.3, 0.8, 50.4, 34.5, 73.4, 3.5, 25.6, 10.2]
    stats2 = [24.1, 4.6, 6.5, 1.7, 0.2, 47.2, 41.1, 90.6, 3.0, 24.2, 9.8]

    g1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    g2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    ratios = [2, 1, 1, 1, 2]

    def render_cell(content, is_header=False, font_size="1rem", margin_top="0px"):
        if is_header:
            style = (
                "border:none;"                     # NO visible border
                f"margin-top:{margin_top};"
                "padding:8px;"                     # same padding as data
                "display:flex;align-items:flex-end;justify-content:center;"
                f"font-size:{font_size};font-weight:bold;"
            )
        else:
            style = (
                "border:1px solid #444;"
                "padding:8px;"
                "display:flex;align-items:center;justify-content:center;"
                "width:100%;"
            )
        st.markdown(f"<div style='{style}'>{content}</div>", unsafe_allow_html=True)

    headers   = [player1_comp, "G Score", "Category", "G Score", player2_comp]
    font_sz   = ["2rem",       "1rem",     "1rem",     "1rem",     "2rem"      ]

    cols = st.columns(ratios)
    for i, (col, txt, fs) in enumerate(zip(cols, headers, font_sz)):
        with col:
            render_cell(txt, is_header=True, font_size=fs, margin_top=("20px" if i in (1, 2, 3) else "0px"))

    for i, cat in enumerate(categories):
        row = st.columns(ratios)
        vals = [stats1[i], g1[i], cat, g2[i], stats2[i]]
        for c, v in zip(row, vals):
            with c:
                render_cell(v)
    
    
    # Trade Tool Code


    # Ranking Inputs



# Drafting Tool
elif page == "Drafting Strategy":
    st.title("Drafting Strategy - H Algorithm")

    # Sidebar Inputs
    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Drafting Inputs")

