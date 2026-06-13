import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Numeric, Text, Boolean, ForeignKey
import sys

DATABASE_URL = 'postgresql://postgres:root@localhost:5432/ipl_db'
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the matches table
matches_table = Table(
    'matches', metadata,
    Column('match_id', Integer, primary_key=True),
    Column('date', Date),
    Column('season', String(50), index=True),
    Column('city', String(100)),
    Column('venue', String(255)),
    Column('team1', String(100)),
    Column('team2', String(100)),
    Column('toss_winner', String(100)),
    Column('toss_decision', String(50)),
    Column('team1_runs', Integer),
    Column('team1_wickets', Integer),
    Column('team2_runs', Integer),
    Column('team2_wickets', Integer),
    Column('winner', String(100)),
    Column('result_type', String(50)),
    Column('win_by_runs', Integer),
    Column('win_by_wickets', Integer),
    Column('player_of_match', String(100)),
    Column('match_referee', String(100)),
    Column('umpire1', String(100)),
    Column('umpire2', String(100)),
    Column('tv_umpire', String(100)),
    Column('reserve_umpire', String(100)),
    Column('overs_limit', Integer),
    Column('team1_players', Text),
    Column('team2_players', Text),
    Column('year', Integer, index=True)
)

# Define the deliveries table
deliveries_table = Table(
    'deliveries', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('match_id', Integer, ForeignKey('matches.match_id'), index=True),
    Column('season', String(50)),
    Column('start_date', Date),
    Column('venue', String(255)),
    Column('innings', Integer),
    Column('ball', Numeric(4, 2)),
    Column('actual_delivery', Integer),
    Column('batting_team', String(100)),
    Column('bowling_team', String(100)),
    Column('batsman', String(100), index=True),
    Column('non_striker', String(100)),
    Column('bowler', String(100), index=True),
    Column('batsman_runs', Integer),
    Column('extras', Integer),
    Column('wides', Integer),
    Column('noballs', Integer),
    Column('byes', Integer),
    Column('legbyes', Integer),
    Column('penalty', Integer),
    Column('non_boundary', Boolean),
    Column('dismissal_kind', String(100)),
    Column('player_dismissed', String(100)),
    Column('other_wicket_type', String(100)),
    Column('other_player_dismissed', String(100)),
    Column('fielder_1', String(100)),
    Column('fielder_2', String(100)),
    Column('fielder_3', String(100)),
    Column('total_runs', Integer)
)

print("Dropping existing tables if any...")
metadata.reflect(bind=engine)
metadata.drop_all(bind=engine)

print("Creating tables...")
metadata.create_all(bind=engine)
print("Tables created successfully!")

print("Loading cleaned matches from CSV...")
df_matches = pd.read_csv("IPL_Project/data/matches.csv")
df_matches['date'] = pd.to_datetime(df_matches['date'])

print("Loading cleaned deliveries from CSV...")
df_deliveries = pd.read_csv("IPL_Project/data/deliveries.csv", low_memory=False)
df_deliveries['start_date'] = pd.to_datetime(df_deliveries['start_date'])

# Handle Boolean or float issues for boolean fields
df_deliveries['non_boundary'] = df_deliveries['non_boundary'].fillna(False).astype(bool)

print("Uploading matches table to PostgreSQL...")
df_matches.to_sql('matches', engine, if_exists='append', index=False)
print("Matches uploaded successfully!")

print("Uploading deliveries table to PostgreSQL (using batch uploads)...")
# Using chunksize to handle memory and speed
df_deliveries.to_sql('deliveries', engine, if_exists='append', index=False, chunksize=15000)
print("Deliveries uploaded successfully!")

print("Database Upload Complete!")
