-- SQL Analysis Queries for IPL Database (ipl_db)

-- Query 1: Most successful team (by total wins)
-- Standard query to count match wins for each team
SELECT winner, COUNT(*) AS wins
FROM matches
WHERE winner IS NOT NULL AND winner != 'No Result'
GROUP BY winner
ORDER BY wins DESC;


-- Query 2: Matches per season
-- Standard query to count number of matches played each season
SELECT season, COUNT(*) AS total_matches
FROM matches
GROUP BY season
ORDER BY season;


-- Query 3: Toss impact
-- Standard query to analyze how many matches toss winners went on to win
SELECT 
    CASE WHEN toss_winner = winner THEN 'Won Toss & Won Match'
         ELSE 'Won Toss & Lost/No Result'
    END AS toss_match_outcome,
    COUNT(*) AS match_count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM matches) * 100, 2) AS percentage
FROM matches
GROUP BY toss_match_outcome;


-- Query 4: Top 10 batsman (by total runs off bat)
-- Runs accumulated by striker across all seasons
SELECT batsman, SUM(batsman_runs) AS runs
FROM deliveries
GROUP BY batsman
ORDER BY runs DESC
LIMIT 10;


-- Helper Query 5: Top 10 bowlers (by wickets taken)
-- Standard dismissals excluding run outs, retired hurt, etc.
SELECT bowler, COUNT(*) AS wickets
FROM deliveries
WHERE dismissal_kind IN ('bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 10;


-- Helper Query 6: Highest scoring stadiums (Average total runs per match by venue)
-- Restricts to venues that hosted at least 10 matches for statistical relevance
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
