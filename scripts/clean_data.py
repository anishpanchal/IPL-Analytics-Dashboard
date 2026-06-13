import pandas as pd
import glob
import os
import shutil
from datetime import datetime

# Define file paths
RAW_MATCHES_PATH = "d:/DATASETS/IPL/ipl_data.csv"
CRICSHEET_DIR = "d:/DATASETS/IPL/extracted_ipl_csv"
OUTPUT_DIR = "d:/DATASETS/IPL/IPL_Project/data"
RAW_OUTPUT_DIR = "d:/DATASETS/IPL/IPL_Project/data/raw_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)

# 1. Copy raw matches to raw_data/
print("Copying raw matches to raw_data/matches.csv...")
shutil.copy(RAW_MATCHES_PATH, os.path.join(RAW_OUTPUT_DIR, "matches.csv"))

# 2. Team name standardization mapping
team_mapping = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru"
}

def standardize_team(name):
    if pd.isna(name):
        return name
    name_str = str(name).strip()
    return team_mapping.get(name_str, name_str)

# 3. Parse Cricsheet info files to construct match_id mapping
print("Parsing Cricsheet info files for match IDs...")
info_files = glob.glob(os.path.join(CRICSHEET_DIR, "*_info.csv"))
cricsheet_matches = []

for info_path in info_files:
    match_id = int(os.path.basename(info_path).replace("_info.csv", ""))
    date_val = None
    teams = []
    
    with open(info_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[0] == "info":
                key = parts[1]
                val = parts[2]
                if key == "date":
                    date_val = val.replace("/", "-")
                elif key == "team":
                    teams.append(val)
                    
    if date_val and len(teams) >= 2:
        try:
            parsed_date = datetime.strptime(date_val, "%Y-%m-%d").date()
            cricsheet_matches.append({
                "match_id": match_id,
                "date": parsed_date,
                "teams": {standardize_team(teams[0]), standardize_team(teams[1])}
            })
        except Exception as e:
            print(f"Error parsing date {date_val} in file {info_path}: {e}")

print(f"Loaded {len(cricsheet_matches)} Cricsheet matches.")

# 4. Load and clean local matches
print("Cleaning matches dataset...")
df_matches = pd.read_csv(RAW_MATCHES_PATH)

# Standardize teams and winner in matches dataframe
df_matches['team1'] = df_matches['team1'].apply(standardize_team)
df_matches['team2'] = df_matches['team2'].apply(standardize_team)
df_matches['toss_winner'] = df_matches['toss_winner'].apply(standardize_team)
df_matches['winner'] = df_matches['winner'].apply(standardize_team)

# Fill null values for winner and others (e.g. results)
df_matches['winner'] = df_matches['winner'].fillna("No Result")
df_matches['result_type'] = df_matches['result_type'].fillna("No Result")
df_matches['player_of_match'] = df_matches['player_of_match'].fillna("Unknown")

# Handle other missing values
df_matches['city'] = df_matches['city'].fillna("Unknown")
df_matches['umpire1'] = df_matches['umpire1'].fillna("Unknown")
df_matches['umpire2'] = df_matches['umpire2'].fillna("Unknown")
df_matches['tv_umpire'] = df_matches['tv_umpire'].fillna("Unknown")
df_matches['reserve_umpire'] = df_matches['reserve_umpire'].fillna("Unknown")
df_matches['match_referee'] = df_matches['match_referee'].fillna("Unknown")

# Drop duplicates
df_matches.drop_duplicates(inplace=True)

# 5. Fuzzy map match IDs
print("Mapping match IDs from Cricsheet matches...")
match_ids = []
unmapped_count = 0

for idx, row in df_matches.iterrows():
    row_date_str = str(row['date']).replace("/", "-")
    row_date = datetime.strptime(row_date_str, "%Y-%m-%d").date()
    row_teams = {row['team1'], row['team2']}
    
    match_found = None
    # 1. Try exact match
    for cm in cricsheet_matches:
        if cm['teams'] == row_teams and cm['date'] == row_date:
            match_found = cm['match_id']
            break
            
    # 2. Try +/- 1 day match
    if not match_found:
        for cm in cricsheet_matches:
            if cm['teams'] == row_teams and abs((cm['date'] - row_date).days) <= 1:
                match_found = cm['match_id']
                print(f"  Fuzzy Matched Row {idx}: Local Date {row_date} -> Cricsheet Date {cm['date']} (ID: {match_found})")
                break
                
    if match_found:
        match_ids.append(match_found)
    else:
        match_ids.append(None)
        unmapped_count += 1
        print(f"  FAILED to map: Row {idx}: {row_date} - {row['team1']} vs {row['team2']}")

df_matches['match_id'] = match_ids

# Move match_id to be the first column
cols = ['match_id'] + [col for col in df_matches.columns if col != 'match_id']
df_matches = df_matches[cols]

# Save cleaned matches
matches_clean_path = os.path.join(OUTPUT_DIR, "matches.csv")
df_matches.to_csv(matches_clean_path, index=False)
print(f"Saved cleaned matches to {matches_clean_path}. Unmapped: {unmapped_count}")

# 6. Load ball-by-ball deliveries
print("Loading ball-by-ball delivery files...")
master_csv_path = os.path.join(CRICSHEET_DIR, "all_matches.csv")
if os.path.exists(master_csv_path):
    print("Found Cricsheet master deliveries file 'all_matches.csv'. Loading directly...")
    df_deliveries = pd.read_csv(master_csv_path, low_memory=False)
else:
    print("Master deliveries file not found. Fallback to merging individual match files...")
    ball_csv_paths = glob.glob(os.path.join(CRICSHEET_DIR, "*.csv"))
    # Filter out info files, master file, and README
    ball_csv_paths = [p for p in ball_csv_paths if not p.endswith("_info.csv") and not os.path.basename(p) in ["README.txt", "all_matches.csv"]]
    dfs = []
    for idx, path in enumerate(ball_csv_paths):
        try:
            df_temp = pd.read_csv(path)
            dfs.append(df_temp)
            if (idx + 1) % 200 == 0:
                print(f"  Loaded {idx + 1} files...")
        except Exception as e:
            print(f"  Error reading {path}: {e}")
    df_deliveries = pd.concat(dfs, ignore_index=True)

print("Deliveries shape:", df_deliveries.shape)

# Clean and standardize deliveries
print("Standardizing deliveries columns and team names...")
df_deliveries['batting_team'] = df_deliveries['batting_team'].apply(standardize_team)
df_deliveries['bowling_team'] = df_deliveries['bowling_team'].apply(standardize_team)

# Rename columns to match SQL analysis query requirements
# striker -> batsman, runs_off_bat -> batsman_runs, wicket_type -> dismissal_kind
df_deliveries = df_deliveries.rename(columns={
    "striker": "batsman",
    "runs_off_bat": "batsman_runs",
    "wicket_type": "dismissal_kind"
})

# Calculate total runs
df_deliveries['total_runs'] = df_deliveries['batsman_runs'] + df_deliveries['extras']

# Filter deliveries to only contain match_ids present in matches.csv
valid_match_ids = set(df_matches['match_id'].dropna().astype(int))
original_len = len(df_deliveries)
df_deliveries = df_deliveries[df_deliveries['match_id'].isin(valid_match_ids)]
print(f"Filtered deliveries from {original_len} to {len(df_deliveries)} based on valid matches.")

# Fill NaN values in deliveries
df_deliveries['wides'] = df_deliveries['wides'].fillna(0).astype(int)
df_deliveries['noballs'] = df_deliveries['noballs'].fillna(0).astype(int)
df_deliveries['byes'] = df_deliveries['byes'].fillna(0).astype(int)
df_deliveries['legbyes'] = df_deliveries['legbyes'].fillna(0).astype(int)
df_deliveries['penalty'] = df_deliveries['penalty'].fillna(0).astype(int)
df_deliveries['player_dismissed'] = df_deliveries['player_dismissed'].fillna("Not Out")
df_deliveries['dismissal_kind'] = df_deliveries['dismissal_kind'].fillna("None")

# Save cleaned deliveries
deliveries_clean_path = os.path.join(OUTPUT_DIR, "deliveries.csv")
print("Saving deliveries to CSV (this might take a few seconds)...")
df_deliveries.to_csv(deliveries_clean_path, index=False)
print(f"Saved cleaned deliveries to {deliveries_clean_path}.")
print("Data Cleaning Complete!")
