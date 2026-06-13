import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database Connection
DATABASE_URL = 'postgresql://postgres:root@localhost:5432/ipl_db'
engine = create_engine(DATABASE_URL)

PLOTS_DIR = "IPL_Project/plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

# Helper function to print query results as markdown
def print_query_results(title, query):
    print(f"\n### {title}")
    df = pd.read_sql(query, engine)
    print(df.to_markdown(index=False))
    return df

# Execute SQL Queries
print("=== Running SQL Analysis ===")

q1_team_wins = """
SELECT winner, COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL AND winner != 'No Result'
GROUP BY winner
ORDER BY wins DESC;
"""
df_wins = print_query_results("Most Successful Teams (Wins)", q1_team_wins)

q2_seasons = """
SELECT season, COUNT(*) AS total_matches
FROM matches
GROUP BY season
ORDER BY season;
"""
df_seasons = print_query_results("Matches Played Per Season", q2_seasons)

q3_toss = """
SELECT 
    CASE WHEN toss_winner = winner THEN 'Won Toss & Won Match'
         ELSE 'Won Toss & Lost/No Result'
    END AS toss_match_outcome,
    COUNT(*) AS match_count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM matches) * 100, 2) AS percentage
FROM matches
GROUP BY toss_match_outcome;
"""
df_toss = print_query_results("Toss Decision Impact on Match Outcome", q3_toss)

q4_batsmen = """
SELECT batsman, SUM(batsman_runs) AS runs
FROM deliveries
GROUP BY batsman
ORDER BY runs DESC
LIMIT 10;
"""
df_batsmen = print_query_results("Top 10 Batsmen (Total Runs)", q4_batsmen)

q5_bowlers = """
SELECT bowler, COUNT(*) AS wickets
FROM deliveries
WHERE dismissal_kind IN ('bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10;
"""
df_bowlers = print_query_results("Top 10 Bowlers (Total Wickets)", q5_bowlers)

q6_venues_scoring = """
SELECT venue, ROUND(AVG(match_total_runs), 2) AS avg_match_runs, COUNT(DISTINCT match_id) AS matches_played
FROM (
    SELECT match_id, venue, SUM(total_runs) AS match_total_runs
    FROM deliveries
    GROUP BY match_id, venue
) t
GROUP BY venue
HAVING COUNT(DISTINCT match_id) >= 10
ORDER BY avg_match_runs DESC
LIMIT 10;
"""
df_venues_scoring = print_query_results("Highest Scoring Stadiums (Avg Match Runs, Min 10 Matches)", q6_venues_scoring)

# === Generate Python EDA Charts ===
print("\n=== Generating EDA Charts ===")

# Set visual style
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except Exception:
    try:
        plt.style.use('seaborn-whitegrid')
    except Exception:
        plt.style.use('ggplot')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Chart 1: Team Wins (Horizontal Bar Chart)
plt.figure(figsize=(10, 6))
# Create a beautiful blue-cyan gradient palette
colors = sns.color_palette("coolwarm", len(df_wins))
sns.barplot(x="wins", y="winner", data=df_wins, palette="Blues_r", hue="winner", legend=False)
plt.title("IPL - Total Match Wins by Team (2008-2026)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Total Wins", fontsize=11, labelpad=10)
plt.ylabel("Team Name", fontsize=11)
plt.tight_layout()
c1_path = os.path.join(PLOTS_DIR, "team_wins_chart.png")
plt.savefig(c1_path, dpi=150)
plt.close()
print(f"Saved Chart 1 to {c1_path}")

# Chart 2: Season Wise Match Counts (Line Chart with markers)
plt.figure(figsize=(12, 6))
plt.plot(df_seasons['season'], df_seasons['total_matches'], marker='o', color='#1d3557', linewidth=2.5, markersize=8, markerfacecolor='#e63946')
plt.title("IPL - Total Matches Played Per Season (2008-2026)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Season", fontsize=11, labelpad=10)
plt.ylabel("Number of Matches", fontsize=11, labelpad=10)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
c2_path = os.path.join(PLOTS_DIR, "seasons_chart.png")
plt.savefig(c2_path, dpi=150)
plt.close()
print(f"Saved Chart 2 to {c2_path}")

# Chart 3: Toss Impact (Pie Chart with custom colors)
plt.figure(figsize=(7, 7))
toss_colors = ['#457b9d', '#e63946']
plt.pie(df_toss['match_count'], labels=df_toss['toss_match_outcome'], autopct='%1.1f%%', startangle=90, 
        colors=toss_colors, textprops={'fontsize': 11, 'fontweight': 'bold'}, explode=(0.03, 0))
plt.title("IPL - Toss Decision Impact on Match Wins", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
c3_path = os.path.join(PLOTS_DIR, "toss_impact_chart.png")
plt.savefig(c3_path, dpi=150)
plt.close()
print(f"Saved Chart 3 to {c3_path}")

# Chart 4: Venue Wise Match Counts (Bar Chart for Top 10 Venues)
# Let's query the top 10 most played venues
q_venues = """
SELECT venue, COUNT(*) AS match_count
FROM matches
GROUP BY venue
ORDER BY match_count DESC
LIMIT 10;
"""
df_venues = pd.read_sql(q_venues, engine)

plt.figure(figsize=(10, 6))
sns.barplot(x="match_count", y="venue", data=df_venues, palette="flare", hue="venue", legend=False)
plt.title("IPL - Top 10 Most Played Venues (2008-2026)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Matches Played", fontsize=11, labelpad=10)
plt.ylabel("Venue", fontsize=11)
plt.tight_layout()
c4_path = os.path.join(PLOTS_DIR, "venues_chart.png")
plt.savefig(c4_path, dpi=150)
plt.close()
print(f"Saved Chart 4 to {c4_path}")

print("SQL Analysis and Python EDA Complete!")
