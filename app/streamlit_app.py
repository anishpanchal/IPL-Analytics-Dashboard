import streamlit as st
import pandas as pd
import pickle
import os
import sys
from sqlalchemy import create_engine

# Page Config
st.set_page_config(
    page_title="IPL Match Predictor & Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Connection (Cached for performance)
@st.cache_resource
def get_db_engine():
    try:
        DATABASE_URL = 'postgresql://postgres:root@localhost:5432/ipl_db'
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        return None

# Load ML Assets
@st.cache_resource
def load_ml_assets():
    assets_path = "IPL_Project/app/model_assets.pkl"
    if not os.path.exists(assets_path):
        return None
    with open(assets_path, "rb") as f:
        assets = pickle.load(f)
    return assets

# Custom Glassmorphic Dark Theme CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    /* Global Font & Background Styling */
    html, body, div, span, label, p, h1, h2, h3, h4, h5, h6, select, button {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(18, 20, 34) 0%, rgb(10, 10, 16) 90%);
        color: #f8f9fa;
    }
    
    /* Header Container */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        color: #a0aec0;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Cards and Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 242, 254, 0.4);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        color: #00f2fe;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Metric styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Result Display */
    .result-container {
        padding: 2rem;
        border-radius: 16px;
        background: rgba(0, 242, 254, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.15);
        text-align: center;
        margin-top: 1rem;
    }
    
    .winner-badge {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0d1117;
        font-weight: 700;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }
    
    .winner-name {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1.5rem;
    }
    
    .probability-label {
        font-size: 1.1rem;
        color: #a0aec0;
        margin-bottom: 0.3rem;
    }
    
    .probability-bar-container {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 12px;
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    
    .probability-bar-fill {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        height: 100%;
        border-radius: 10px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgb(15, 17, 28) !important;
    }
</style>
""", unsafe_allow_html=True)

# Layout Setup
st.markdown("""
<div class="header-container">
    <div class="header-title">🏏 IPL PREDICTOR & LEAGUE INSIGHTS</div>
    <div class="header-subtitle">Interactive Win Probability Modeling & PostgreSQL Database Analytics (2008–2026)</div>
</div>
""", unsafe_allow_html=True)

# Database connections and ML checks
engine = get_db_engine()
assets = load_ml_assets()

if not assets:
    st.error("❌ Machine Learning assets could not be found! Please make sure you run the training script `scripts/model.py` first.")
    st.stop()

# Extract attributes from ML assets
model = assets["model"]
team_encoder = assets["team_encoder"]
venue_encoder = assets["venue_encoder"]
toss_decision_encoder = assets["toss_decision_encoder"]

teams_list = sorted(list(team_encoder.classes_))
venues_list = sorted(list(venue_encoder.classes_))

# Sidebar Navigation
st.sidebar.markdown("<h2 style='color:#00f2fe;'>Navigation</h2>", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Go To", ["🔮 Win Predictor", "📊 Live DB Analytics", "📋 Project Details"])

# -----------------🔮 MODE 1: WIN PREDICTOR -----------------
if app_mode == "🔮 Win Predictor":
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">⚙️ MATCH CONFIGURATION</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Form inputs inside container
        with st.container():
            team1 = st.selectbox("Select Team 1", teams_list, index=teams_list.index("Chennai Super Kings") if "Chennai Super Kings" in teams_list else 0)
            
            # Filter Team 2 dropdown to prevent selecting same team
            available_teams2 = [t for t in teams_list if t != team1]
            team2 = st.selectbox("Select Team 2", available_teams2, index=available_teams2.index("Mumbai Indians") if "Mumbai Indians" in available_teams2 else 0)
            
            venue = st.selectbox("Select Match Venue", venues_list, index=0)
            
            # Toss options based on selected teams
            toss_winner = st.selectbox("Toss Winner", [team1, team2])
            toss_decision = st.selectbox("Toss Decision", ["field", "bat"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            predict_btn = st.button("🔮 Calculate Win Probability", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">📊 PREDICTION ENGINE OUTPUT</div>
        </div>
        """, unsafe_allow_html=True)
        
        if predict_btn:
            try:
                # Prepare features for prediction
                # Encoded columns: team1, team2, venue, toss_winner, toss_decision
                team1_encoded = team_encoder.transform([team1])[0]
                team2_encoded = team_encoder.transform([team2])[0]
                venue_encoded = venue_encoder.transform([venue])[0]
                toss_winner_encoded = team_encoder.transform([toss_winner])[0]
                toss_decision_encoded = toss_decision_encoder.transform([toss_decision])[0]
                
                # Construct input DataFrame
                input_df = pd.DataFrame([{
                    "team1": team1_encoded,
                    "team2": team2_encoded,
                    "venue": venue_encoded,
                    "toss_winner": toss_winner_encoded,
                    "toss_decision": toss_decision_encoded
                }])
                
                # Get probabilities
                probabilities = model.predict_proba(input_df)[0]
                
                # Since the model predicts class labels (encoded team numbers),
                # let's map the prediction probabilities to our specific teams
                classes = model.classes_
                prob_dict = {team_encoder.inverse_transform([c])[0]: p for c, p in zip(classes, probabilities)}
                
                # Retrieve probability for selected teams
                p1 = prob_dict.get(team1, 0.0)
                p2 = prob_dict.get(team2, 0.0)
                
                # Normalize just in case other teams got minor probabilities in RF
                total_p = p1 + p2
                if total_p > 0:
                    p1_norm = p1 / total_p
                    p2_norm = p2 / total_p
                else:
                    p1_norm = 0.5
                    p2_norm = 0.5
                
                winner = team1 if p1_norm > p2_norm else team2
                winner_prob = p1_norm if p1_norm > p2_norm else p2_norm
                
                # Render beautiful output
                st.markdown(f"""
                <div class="result-container">
                    <div class="winner-badge">🏆 Predicted Winner</div>
                    <div class="winner-name">{winner}</div>
                    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.5rem 0;">
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600;">{team1}</span>
                        <span style="color: #00f2fe; font-weight: 700;">{p1_norm * 100:.1f}%</span>
                    </div>
                    <div class="probability-bar-container">
                        <div class="probability-bar-fill" style="width: {p1_norm * 100}%;"></div>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600;">{team2}</span>
                        <span style="color: #ff3366; font-weight: 700;">{p2_norm * 100:.1f}%</span>
                    </div>
                    <div class="probability-bar-container">
                        <div class="probability-bar-fill" style="width: {p2_norm * 100}%; background: linear-gradient(90deg, #ff3366 0%, #ff5e62 100%);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.success(f"🎉 Model predicts {winner} has a {winner_prob * 100:.1f}% probability of winning!")
                
            except Exception as e:
                st.error(f"Error executing prediction: {e}")
        else:
            st.info("👈 Set the match details in the left panel and click 'Calculate Win Probability' to run prediction.")

# -----------------📊 MODE 2: LIVE DB ANALYTICS -----------------
elif app_mode == "📊 Live DB Analytics":
    if not engine:
        st.warning("⚠️ PostgreSQL Database connection is offline. Make sure the database exists and upload_db.py has been run.")
        st.stop()
        
    st.markdown("<h3 style='color:#00f2fe;'>PostgreSQL ipl_db Live Dashboard</h3>", unsafe_allow_html=True)
    
    # Quick Stats Row
    try:
        total_matches_df = pd.read_sql("SELECT COUNT(*) FROM matches", engine)
        total_runs_df = pd.read_sql("SELECT SUM(total_runs) FROM deliveries", engine)
        total_wickets_df = pd.read_sql("SELECT COUNT(*) FROM deliveries WHERE dismissal_kind IN ('bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket')", engine)
        
        stat1, stat2, stat3 = st.columns(3)
        with stat1:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="metric-value">{total_matches_df.iloc[0,0]}</div>
                <div class="metric-label">Total Matches (2008-2026)</div>
            </div>
            """, unsafe_allow_html=True)
        with stat2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="metric-value">{int(total_runs_df.iloc[0,0]):,}</div>
                <div class="metric-label">Total Runs Scored</div>
            </div>
            """, unsafe_allow_html=True)
        with stat3:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div class="metric-value">{total_wickets_df.iloc[0,0]:,}</div>
                <div class="metric-label">Total Wickets Taken</div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching aggregate stats: {e}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">🏏 Top 10 Batsmen of All Time</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            q_bat = "SELECT batsman, SUM(batsman_runs) AS runs FROM deliveries GROUP BY batsman ORDER BY runs DESC LIMIT 10"
            df_bat = pd.read_sql(q_bat, engine)
            st.dataframe(df_bat, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(e)
            
    with col_b:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">☝️ Top 10 Wicket Takers of All Time</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            q_bowl = "SELECT bowler, COUNT(*) AS wickets FROM deliveries WHERE dismissal_kind IN ('bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket') GROUP BY bowler ORDER BY wickets DESC LIMIT 10"
            df_bowl = pd.read_sql(q_bowl, engine)
            st.dataframe(df_bowl, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(e)

    # Season Wise Stats
    st.markdown("""
    <div class="glass-card">
        <div class="card-title">📈 Total Matches Played Per Season</div>
    </div>
    """, unsafe_allow_html=True)
    try:
        q_season = "SELECT season, COUNT(*) AS total_matches FROM matches GROUP BY season ORDER BY season"
        df_season = pd.read_sql(q_season, engine)
        st.line_chart(data=df_season.set_index("season"), y="total_matches", color="#00f2fe")
    except Exception as e:
        st.error(e)

# -----------------📋 MODE 3: PROJECT DETAILS -----------------
elif app_mode == "📋 Project Details":
    st.markdown("""
    <div class="glass-card">
        <div class="card-title">📋 Pipeline Architecture</div>
        <p>The project follows an end-to-end data engineering and data science structure:</p>
        <ul>
            <li><b>Data Cleaning:</b> Matches and ball-by-ball files from Cricsheet were cleaned, normalized (team names standardized, null values handled), and fuzzy date-matched to align their primary keys.</li>
            <li><b>PostgreSQL Ingestion:</b> Cleaned datasets are streamed into a PostgreSQL database with relational keys (matches as primary, deliveries as foreign key).</li>
            <li><b>Machine Learning:</b> A Random Forest Classifier was trained to predict the winner based on Team 1, Team 2, Venue, Toss Winner, and Toss Decision. Model assets are serialized and loaded dynamically by this app.</li>
            <li><b>Web App:</b> Interactive dashboard built using Streamlit, styled with a modern dark theme and direct database indicators.</li>
        </ul>
    </div>
    <div class="glass-card">
        <div class="card-title">⚙️ Database Configurations</div>
        <ul>
            <li><b>Server:</b> localhost</li>
            <li><b>Database:</b> ipl_db</li>
            <li><b>Username:</b> postgres</li>
            <li><b>Password:</b> root</li>
            <li><b>Port:</b> 5432</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
