import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

print("=== Training Machine Learning Model ===")

# Load cleaned matches
matches_path = "IPL_Project/data/matches.csv"
if not os.path.exists(matches_path):
    print(f"Error: {matches_path} not found. Please run clean_data.py first.")
    sys.exit(1)

df = pd.read_csv(matches_path)

# Filter out 'No Result' matches as they don't have a valid winner
df = df[df['winner'] != 'No Result']
df = df[df['winner'].notna()]

# Define feature columns and target
feature_cols = ['team1', 'team2', 'venue', 'toss_winner', 'toss_decision']
target_col = 'winner'

# Extract unique classes for encoders
all_teams = pd.concat([df['team1'], df['team2'], df['toss_winner'], df['winner']]).unique()
all_venues = df['venue'].unique()
all_decisions = df['toss_decision'].unique()

print(f"Number of unique teams: {len(all_teams)}")
print(f"Number of unique venues: {len(all_venues)}")

# Initialize and fit encoders
team_encoder = LabelEncoder()
team_encoder.fit(all_teams)

venue_encoder = LabelEncoder()
venue_encoder.fit(all_venues)

toss_decision_encoder = LabelEncoder()
toss_decision_encoder.fit(all_decisions)

# Encode features and target
X = pd.DataFrame()
X['team1'] = team_encoder.transform(df['team1'])
X['team2'] = team_encoder.transform(df['team2'])
X['venue'] = venue_encoder.transform(df['venue'])
X['toss_winner'] = team_encoder.transform(df['toss_winner'])
X['toss_decision'] = toss_decision_encoder.transform(df['toss_decision'])

y = team_encoder.transform(df['winner'])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training set size: {len(X_train)}")
print(f"Testing set size: {len(X_test)}")

# Initialize and train RandomForest Classifier
# Tune hyperparameters for generalizability and to avoid overfitting
model = RandomForestClassifier(n_estimators=150, max_depth=12, min_samples_split=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"Testing Accuracy: {test_accuracy * 100:.2f}%")

# Save model and encoders
app_dir = "IPL_Project/app"
os.makedirs(app_dir, exist_ok=True)
model_assets_path = os.path.join(app_dir, "model_assets.pkl")

print(f"Saving model and encoders to {model_assets_path}...")
assets = {
    "model": model,
    "team_encoder": team_encoder,
    "venue_encoder": venue_encoder,
    "toss_decision_encoder": toss_decision_encoder
}

with open(model_assets_path, "wb") as f:
    pickle.dump(assets, f)

print("Machine Learning Model Training Complete!")
