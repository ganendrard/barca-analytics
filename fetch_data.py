fetch_data.py

Tujuan:
- Ambil data pertandingan Barcelona (sample) untuk musim ini & musim sebelumnya.
- Default behavior:
  1) Jika pengguna memberi URL FBref tim/matchlog, script akan mencoba membaca tabel lewat pandas.read_html.
  2) Jika tidak ada URL, script akan fallback ke CSV publik (football-data.co.uk) untuk LaLiga.
- Output: data/matches.csv dan data/team_match_stats.csv (sample).

import os
import sys
import time
import argparse
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_fbref_table(url):
    """
    Try to fetch tables from an FBref team match log page using pandas.read_html.
    Note: FBref sometimes blocks scrapers; if read_html fails, the user may pass a different source.
    """
    try:
        print(f"Reading tables from {url} ...")
        tables = pd.read_html(url)
        print(f"Found {len(tables)} tables on page.")
        # Heuristic: find table with columns like 'Date' or 'Comp'
        for t in tables:
            cols = [c.lower() for c in t.columns.astype(str)]
            if any('date' in c for c in cols) and any('xg' in c for c in cols) or any('comp' in c for c in cols):
                return t
        # fallback: return first
        return tables[0]
    except Exception as e:
        print("Failed to read FBref tables:", e)
        return None

def fetch_football_data(season_year):
    """
    Fallback: download football-data.co.uk CSV for LaLiga (SP1).
    season_year -> ending year e.g., 2025 for 2024/25 uses mmz4281/2425 naming convention.
    """
    yy = season_year % 100
    yy_prev = (season_year - 1) % 100
    code = f"{yy_prev:02d}{yy:02d}"
    url = f"https://www.football-data.co.uk/mmz4281/{season_year}/SP1.csv"
    print(f"Downloading fallback CSV from {url} ...")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        csv_path = os.path.join(OUT_DIR, f"SP1_{season_year}.csv")
        with open(csv_path, "wb") as f:
            f.write(r.content)
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print("Failed to download fallback CSV:", e)
        return None

def normalize_and_export(df, team_name="Barcelona"):
    """
    Expect a DataFrame with at least Date, HomeTeam, AwayTeam, FTHG, FTAG (or columns variant).
    Normalize into two tables:
    - matches.csv : one row per match (date, home_team, away_team, home_goals, away_goals, competition)
    - team_match_stats.csv : one row per team per match (team, opponent, is_home, goals_for, goals_against, date, season)
    """
    df_cols = [c.lower() for c in df.columns.astype(str)]
    # heuristics to map columns
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if 'date' in cl:
            col_map['date'] = c
        if cl in ('home', 'hometeam', 'home_team', 'home team'):
            col_map['home'] = c
        if cl in ('away', 'awayteam', 'away_team', 'away team'):
            col_map['away'] = c
        if cl in ('fthg', 'homegoals', 'home_goals', 'home_goals'):
            col_map['home_goals'] = c
        if cl in ('ftag', 'awaygoals', 'away_goals', 'away_goals'):
            col_map['away_goals'] = c
        if 'competition' in cl or 'comp' in cl:
            col_map['competition'] = c

    # Basic validation
    needed = ['date', 'home', 'away', 'home_goals', 'away_goals']
    if not all(k in col_map for k in needed):
        print("Dataframe does not contain expected columns. Found columns:", df.columns.tolist())
        return None, None

    matches = pd.DataFrame()
    matches['date'] = pd.to_datetime(df[col_map['date']], dayfirst=True, errors='coerce')
    matches['home_team'] = df[col_map['home']].astype(str)
    matches['away_team'] = df[col_map['away']].astype(str)
    matches['home_goals'] = pd.to_numeric(df[col_map['home_goals']], errors='coerce').fillna(0).astype(int)
    matches['away_goals'] = pd.to_numeric(df[col_map['away_goals']], errors='coerce').fillna(0).astype(int)
    matches['competition'] = df[col_map['competition']] if 'competition' in col_map else "LaLiga"

    # make team_match_stats
    rows = []
    for idx, r in matches.iterrows():
        season = to_season(r['date'])
        home = {
            'match_id': idx,
            'date': r['date'],
            'team': r['home_team'],
            'opponent': r['away_team'],
            'is_home': 1,
            'goals_for': r['home_goals'],
            'goals_against': r['away_goals'],
            'competition': r['competition'],
            'season': season
        }
        away = {
            'match_id': idx,
            'date': r['date'],
            'team': r['away_team'],
            'opponent': r['home_team'],
            'is_home': 0,
            'goals_for': r['away_goals'],
            'goals_against': r['home_goals'],
            'competition': r['competition'],
            'season': season
        }
        rows.append(home)
        rows.append(away)
    team_stats = pd.DataFrame(rows)

    # Filter to team of interest for sample output
    sample_matches = matches[
        (matches['home_team'].str.contains(team_name, case=False, na=False)) |
        (matches['away_team'].str.contains(team_name, case=False, na=False))
    ].reset_index(drop=True)

    sample_team_stats = team_stats[team_stats['team'].str.contains(team_name, case=False, na=False)].reset_index(drop=True)

    matches.to_csv(os.path.join(OUT_DIR, "matches_all.csv"), index=False)
    team_stats.to_csv(os.path.join(OUT_DIR, "team_match_stats_all.csv"), index=False)

    sample_matches.to_csv(os.path.join(OUT_DIR, "matches.csv"), index=False)
    sample_team_stats.to_csv(os.path.join(OUT_DIR, "team_match_stats.csv"), index=False)

    print("Exported CSV to", OUT_DIR)
    return sample_matches, sample_team_stats

def to_season(dt):
    if pd.isna(dt):
        return ""
    year = dt.year
    if dt.month >= 7:
        return f"{year}/{year+1}"
    else:
        return f"{year-1}/{year}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fbref-url", help="FBref team match log URL (optional)", default=None)
    parser.add_argument("--team", help="Team name to filter sample (default: Barcelona)", default="Barcelona")
    parser.add_argument("--season-end", help="Season end year (e.g., 2025 for 2024/25) as fallback", type=int, default=datetime.now().year + (1 if datetime.now().month>=7 else 0))
    args = parser.parse_args()

    df = None
    if args.fbref_url:
        df = fetch_fbref_table(args.fbref_url)

    if df is None:
        df = fetch_football_data(args.season_end)

    if df is None:
        print("No data available. Please provide a FBref URL or ensure internet connectivity.")
        sys.exit(1)

    sample_matches, sample_team_stats = normalize_and_export(df, team_name=args.team)
    if sample_matches is None:
        print("Normalization failed. Please inspect input data.")
        sys.exit(1)


if __name__ == "__main__":
    main()