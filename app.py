import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import base64

# Page Setup
st.set_page_config(
    page_title="Fantasy Basketball Category Analyzer",
    layout="wide",
)

# Sidebar Title and LinkedIn Hyperlink
st.sidebar.title("Fantasy Basketball 9CAT Analyzer")

linkedin_url = "https://www.linkedin.com/in/karthik-selvaraj-purdue/"
linkedin_icon_url = "https://cdn-icons-png.flaticon.com/512/174/174857.png"
linkedin_html = f"""
<div style="display: flex; align-items: center;  margin-bottom: 20px;">
    <span style='font-size:14px; margin-right: 5px;'>Developed by </span>
    <a href="{linkedin_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none;">
         <img src="{linkedin_icon_url}" width="14" height="14" style="margin-right: 5px;" />
        <span style='font-size:14px;'>Karthik Selvaraj</span>
    </a>
</div>
"""
st.sidebar.markdown(linkedin_html, unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("player_2025_summary.csv")
    return df

df = load_data()

# Function for helping with image display
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Sidebar Navigation
page = st.sidebar.selectbox("Tools", ["Player Comparison", "Trade Tool", "Ranking Viewer"], index=0)

# Player Comparison Tool
if page == "Player Comparison":
    st.title("NBA 9CAT Fantasy Player Comparison")
    
    # Sidebar Inputs
    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Comparison Inputs")
    
    player_names = df["ascii_name"].sort_values().tolist()
    player1_comp = st.sidebar.selectbox("Player 1", player_names, index=player_names.index("LeBron James"), placeholder="LeBron James")
    player2_comp = st.sidebar.selectbox("Player 2", player_names, index=player_names.index("Stephen Curry"), placeholder="Stephen Curry")

    st.sidebar.markdown("""---""")
    st.sidebar.subheader("League Settings")
    num_teams = st.sidebar.number_input("Number of Teams", min_value=1, max_value=20, value=12, help="Here you want to enter the number of teams there are in your fantasy league. This will matter with the G Score calculations, since we use the Z score to select the top rostered players for evaluation.")
    players_per_team = st.sidebar.number_input("Players per Team", min_value=1, max_value=20, value=13, help="Here you want to enter the number of players each team can roster in your league. This will matter with the G Score calculations, since we use the Z score to select the top rostered players for evaluation.")
    
    df_top_q = df.sort_values(by="z_avg_across_9_cats", ascending=False).head(num_teams * players_per_team)
    kappa = (2 * players_per_team) / (2 * (players_per_team) - 1)
    
    # punt_cats = st.sidebar.multiselect("Punted Categories (Max 4)", options=all_punt_options, max_selections=4)

    # Select player rows
    p1 = df[df['ascii_name'] == player1_comp].iloc[0]
    p2 = df[df['ascii_name'] == player2_comp].iloc[0]

    # Get the images to display for each player
    img1_path = f"player_images/{player1_comp}.png"
    img2_path = f"player_images/{player2_comp}.png"
    if not os.path.exists(img1_path):
        img1_path = "player_images/default.png"
    if not os.path.exists(img2_path):
        img2_path = "player_images/default.png"

    # Sets up columns with images and headers
    cols_top = st.columns([2, 3, 2])

    with cols_top[0]:
            # st.image(img1_path, use_column_width=True)
            st.markdown(
                f"<div style='display: flex; justify-content: center;'><img src='data:image/png;base64,{get_base64_image(img1_path)}' width='250'/></div>",
                unsafe_allow_html=True
            )

    with cols_top[2]:
        # st.image(img2_path, use_column_width=True)
        st.markdown(
            f"<div style='display: flex; justify-content: center;'><img src='data:image/png;base64,{get_base64_image(img2_path)}' width='250'/></div>",
            unsafe_allow_html=True
        )

    all_punt_options = ["FG%", "FT%", "3PTM", "PTS", "REB", "AST", "STL", "BLK", "TOV"]
    with cols_top[1]:
        # st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        punt_cats = st.multiselect("Punting Categories", options=all_punt_options, max_selections=4, help="Use this dropdown menu to select categories you may want to \"punt\", or strategically ignore to prioritize other categories. You can then compare which players may be more beneficial for your punting strategy!")

    # Categories and display mappings
    categories = [
        ("field_goals_made", "field_goals_attempted", "FGM/FGA"),
        ("fg_pct", None, "FG%"),
        ("free_throws_made", "free_throws_attempted", "FTM/FTA"),
        ("ft_pct", None, "FT%"),
        ("avg_three_pointers_made", None, "3PTM"),
        ("avg_points", None, "PTS"),
        ("avg_rebounds", None, "REB"),
        ("avg_assists", None, "AST"),
        ("avg_steals", None, "STL"),
        ("avg_blocks", None, "BLK"),
        ("avg_turnovers", None, "TOV")
    ]

    g1 = []
    g2 = []

    for base_col, denom_col, label in categories:
        # Skip over any categories that are being punted
        if label in punt_cats:
            g1.append("-")
            g2.append("-")
            continue

        if base_col.startswith("avg_"):
            cat = base_col.replace("avg_", "")

            # Get both selected players' and the top q players weekly totals for the category
            w1 = np.array(json.loads(p1[f"weekly_{cat}"]))
            w2 = np.array(json.loads(p2[f"weekly_{cat}"]))
            w_each = np.array([np.array(json.loads(row[f"weekly_{cat}"])) for _, row in df_top_q.iterrows()]) # Shape: [num_players (q), num_weeks]

            # Get both selected players' and top q players' weekly average of category
            avg_w1 = np.average(w1)
            avg_w2 = np.average(w2)
            avg_each = np.average(w_each, axis=1)

            # Calculate the league average for the category (for top q players)
            avg_all = np.average(avg_each)

            # Calculate league variance for category (with top q players)
            sigma_sq = np.std(avg_each)

            # Obtain league weekly variance for category (with top q players)
            tau_player = np.std(w_each, axis=1)
            tau_sq = np.average(tau_player**2)

            # Calculate G scores, invert for turnovers, and save to running list
            cat_g1 = (avg_w1 - avg_all) / np.sqrt(sigma_sq + (kappa * tau_sq))
            cat_g2 = (avg_w2 - avg_all) / np.sqrt(sigma_sq + (kappa * tau_sq))

            # print()
            # print(cat, "1: avg - ", avg_w1)
            # print(cat, "2: avg - ", avg_w2)
            # print("league avg: ", avg_all)
            # print("sigma_sq: ", sigma_sq)
            # print("tau_sq: ", tau_sq)
            # print(cat, "1: ", cat_g1)
            # print(cat, "2: ", cat_g2)
            # print()

            g1.append(-cat_g1 if cat == "turnovers" else cat_g1)
            g2.append(-cat_g2 if cat == "turnovers" else cat_g2)

        elif base_col in ["fg_pct", "ft_pct"]:
            cat_key = "field_goals" if base_col == "fg_pct" else "free_throws"

            # Load weekly attempts for both players and both makes and attempts per week for all players
            w_fga1 = np.array(json.loads(p1[f"weekly_{cat_key}_attempted"]))
            w_fga2 = np.array(json.loads(p2[f"weekly_{cat_key}_attempted"]))

            w_fgm_each = np.array([np.array(json.loads(row[f"weekly_{cat_key}_made"])) for _, row in df_top_q.iterrows()]) # Shape: [num_players (q), num_weeks]
            w_fga_each = np.array([np.array(json.loads(row[f"weekly_{cat_key}_attempted"])) for _, row in df_top_q.iterrows()])

            # Gets the composite rates of both chosen players and across top q players
            rate_p1, rate_p2 = p1[base_col], p2[base_col]

            total_made = df_top_q[f"total_{cat_key}_made"]
            total_att = df_top_q[f"total_{cat_key}_attempted"]
            rate_all = total_made.sum() / total_att.sum() if total_att.sum() > 0 else 0
            
            # Get the total attempts for both players - may not be needed (typo in paper?)
            total_fga1 = p1[f"total_{cat_key}_attempted"]
            total_fga2 = p2[f"total_{cat_key}_attempted"]

            # Get mean attempts for both chosen players and across top q players
            avg_fga1 = np.average(w_fga1)
            avg_fga2 = np.average(w_fga2)
            avg_att = np.average(np.average(w_fga_each, axis=1))

            # Gets variance across players (sigma^2) and RMS of weekly standard deviation of each player (tau)
            player_rates = df_top_q[base_col]
            sigma_sq = np.average((player_rates - rate_all)**2)
            
            tau_player = np.std((w_fga_each / avg_att) * ((w_fgm_each / np.where(w_fga_each == 0, 1, w_fga_each)) - rate_all), axis=1)
            tau_sq = np.average(tau_player**2)

            # Calculate percentage G scores for both players and save them
            per_g1 = ((avg_fga1 / avg_att) * (rate_p1 - rate_all)) / np.sqrt(sigma_sq + (kappa * tau_sq))
            per_g2 = ((avg_fga2 / avg_att) * (rate_p2 - rate_all)) / np.sqrt(sigma_sq + (kappa * tau_sq))

            # print()
            # print(cat_key, "1: avg - ", rate_p1)
            # print(cat_key, "2: avg - ", rate_p2)
            # print("league avg: ", rate_all)
            # print("sigma_sq: ", sigma_sq)
            # print("tau_sq: ", tau_sq)
            # print(cat_key, "1: ", per_g1)
            # print(cat_key, "2: ", per_g2)
            # print()

            g1.append(per_g1)
            g2.append(per_g2)

        else:
            g1.append("-")
            g2.append("-")

    stats1 = [
        f"{int(p1['total_field_goals_made'])}/{int(p1['total_field_goals_attempted'])}",
        f"{round(p1['fg_pct'] * 100, 2)}%",
        f"{int(p1['total_free_throws_made'])}/{int(p1['total_free_throws_attempted'])}",
        f"{round(p1['ft_pct'] * 100, 2)}%",
        round(p1['avg_three_pointers_made'], 2),
        round(p1['avg_points'], 2),
        round(p1['avg_rebounds'], 2),
        round(p1['avg_assists'], 2),
        round(p1['avg_steals'], 2),
        round(p1['avg_blocks'], 2),
        round(p1['avg_turnovers'], 2)
    ]

    stats2 = [
        f"{int(p2['total_field_goals_made'])}/{int(p2['total_field_goals_attempted'])}",
        f"{round(p2['fg_pct'] * 100, 2)}%",
        f"{int(p2['total_free_throws_made'])}/{int(p2['total_free_throws_attempted'])}",
        f"{round(p2['ft_pct'] * 100, 2)}%",
        round(p2['avg_three_pointers_made'], 2),
        round(p2['avg_points'], 2),
        round(p2['avg_rebounds'], 2),
        round(p2['avg_assists'], 2),
        round(p2['avg_steals'], 2),
        round(p2['avg_blocks'], 2),
        round(p2['avg_turnovers'], 2)
    ]

    ratios = [2, 1, 1, 1, 2]

    def render_cell(content, is_header=False, font_size="1rem", margin_top="0px", bold=False, bg_color=None):
        border_style = "border:none;" if is_header else "border:1px solid #444;"
        base_style = (
            f"{border_style}margin-top:{margin_top};padding:8px;"
            "display:flex;align-items:center;justify-content:center;"
            f"font-size:{font_size};"
        )
        if bold or is_header:
            base_style += "font-weight:bold;"
        else:
            base_style += "width:100%;"

        if bg_color:
            base_style += f"background-color:{bg_color};"

        st.markdown(f"<div style='{base_style}'>{content}</div>", unsafe_allow_html=True)

    headers   = [player1_comp, "G Score", "Category", "G Score", player2_comp]
    font_sz   = ["2rem",       "1.25rem",     "1.25rem",     "1.25rem",     "2rem"    ]

    
    cols = st.columns(ratios)

    for i, (col, txt, fs) in enumerate(zip(cols, headers, font_sz)):
        with col:
            render_cell(txt, is_header=True, font_size=fs, margin_top=("15px" if i in (1, 2, 3) else "0px"))

    # Displays categories, player averages, and G Scores
    for i, cat in enumerate(categories):
        row = st.columns(ratios)
        better_color = "#1C293A"

        # G-score comparison
        g1_val = g1[i]
        g2_val = g2[i]

        # Determine highlight (ignore "-" entries)
        highlight1 = highlight2 = False
        if isinstance(g1_val, (int, float)) and isinstance(g2_val, (int, float)):
            if g1_val > g2_val:
                highlight1 = True
            elif g2_val > g1_val:
                highlight2 = True

            g1_val = 0.0 if round(g1_val, 2) == -0.0 else round(g1_val, 2)
            g2_val = 0.0 if round(g2_val, 2) == -0.0 else round(g2_val, 2)


        vals = [stats1[i], g1_val, cat[-1], g2_val, stats2[i]]
        for j, (c, v) in enumerate(zip(row, vals)):
            with c:
                is_bold = (j == 2)
                bg = None
                if j in [0, 1] and highlight1:
                    bg = better_color
                elif j in [3, 4] and highlight2:
                    bg = better_color
                render_cell(v, bold=is_bold, bg_color=bg)

    # Overall G-score row
    valid_g1 = [g1[i] for i, cat in enumerate(categories) if cat[-1] not in punt_cats and isinstance(g1[i], (int, float))]
    valid_g2 = [g2[i] for i, cat in enumerate(categories) if cat[-1] not in punt_cats and isinstance(g2[i], (int, float))]
    overall_g1 = round(sum(valid_g1) / len(valid_g1), 2) if valid_g1 else "-"
    overall_g2 = round(sum(valid_g2) / len(valid_g2), 2) if valid_g2 else "-"

    # Normalize -0.0 to 0.0
    overall_g1 = 0.0 if overall_g1 == -0.0 else overall_g1
    overall_g2 = 0.0 if overall_g2 == -0.0 else overall_g2

    # Determines how we highlight the box
    highlight1 = highlight2 = False
    if isinstance(overall_g1, (int, float)) and isinstance(overall_g2, (int, float)):
        if overall_g1 > overall_g2:
            highlight1 = True
        elif overall_g2 > overall_g1:
            highlight2 = True

    # Render the "Overall" row
    overall_vals = ["–", overall_g1, "OVERALL", overall_g2, "–"]
    overall_row = st.columns(ratios)
    for j, (c, v) in enumerate(zip(overall_row, overall_vals)):
        with c:
            is_bold = (j in [1, 2, 3])
            bg = "#25BE41" if (j == 1 and highlight1) or (j == 3 and highlight2) else None
            bg = "#BE2525" if (j == 1 and not highlight1) or (j == 3 and not highlight2) else bg
            bg = "#F5BB1B" if (j == 1 or j == 3) and (not highlight1 and not highlight2) else bg
            render_cell(v, bold=is_bold, bg_color=bg)



# Trade Tool
elif page == "Trade Tool":
    st.title("NBA 9CAT Fantasy Trade Analyzer")

    # Sidebar Inputs
    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Trade Tool Inputs")


# Trade Tool
elif page == "Ranking Viewer":
    st.title("NBA 9CAT Fantasy Player Rankings")

    # Sidebar Inputs
    st.sidebar.markdown("""---""")
    st.sidebar.subheader("Ranking Inputs")

