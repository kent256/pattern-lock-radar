import requests
import streamlit as st
from random import randint, choice

# --- Primary API (API-Football) ---
API_KEY_PRIMARY = "eb716181022347133f61611c3c00831a"
HEADERS_PRIMARY = {
    "X-RapidAPI-Key": API_KEY_PRIMARY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# --- Backup API (Football-Data.org) ---
API_KEY_BACKUP = "8bbc74b52032420baaa66d3db6da6740"
HEADERS_BACKUP = {
    "X-Auth-Token": API_KEY_BACKUP
}

# --- Function: Primary API ---
def get_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    query = {"next": 150}  # Pull more games (next 7 days)
    response = requests.get(url, headers=HEADERS_PRIMARY, params=query)
    data = response.json()

    if 'response' not in data:
        raise ValueError("Primary API failed")

    return [(f['teams']['home']['name'], f['teams']['away']['name']) for f in data['response']]

# --- Function: Backup API ---
def get_fixtures_backup():
    url = "https://api.football-data.org/v4/matches"
    response = requests.get(url, headers=HEADERS_BACKUP)
    data = response.json()

    if 'matches' not in data:
        st.error("❌ Backup API also failed. Try again later.")
        return []

    fixtures = []
    for match in data['matches'][:100]:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        fixtures.append((home, away))
    return fixtures

# --- Simulate team form for now ---
def mock_form():
    return {
        "goals_scored": [randint(0, 3) for _ in range(10)],
        "goals_conceded": [randint(0, 3) for _ in range(10)],
        "bt_ts": [choice([True, False]) for _ in range(10)],
        "first_half_goals": [randint(0, 2) for _ in range(10)],
    }

# --- Pattern Detection Logic ---
def analyze_patterns(home, away):
    home_form = mock_form()
    away_form = mock_form()

    all_goals = home_form["goals_scored"] + away_form["goals_scored"]
    over_05 = sum([g > 0 for g in all_goals]) / 20 * 100
    over_15 = sum([g >= 2 for g in all_goals]) / 20 * 100

    total_goals = [h + a for h, a in zip(home_form['goals_scored'], home_form['goals_conceded'])]
    total_goals += [h + a for h, a in zip(away_form['goals_scored'], away_form['goals_conceded'])]
    under_35 = sum([g < 4 for g in total_goals]) / 20 * 100
    under_45 = sum([g < 5 for g in total_goals]) / 20 * 100

    btts_rate = sum(home_form['bt_ts'] + away_form['bt_ts']) / 20 * 100
    fh_goals = sum([g > 0 for g in home_form['first_half_goals'] + away_form['first_half_goals']]) / 20 * 100

    return {
        "Over 0.5 Goals": f"{over_05:.0f}% ✅" if over_05 >= 95 else f"{over_05:.0f}% ⚠️",
        "Over 1.5 Goals": f"{over_15:.0f}% ✅" if over_15 >= 85 else f"{over_15:.0f}% ⚠️",
        "Under 3.5 Goals": f"{under_35:.0f}% ✅" if under_35 >= 85 else f"{under_35:.0f}% ⚠️",
        "Under 4.5 Goals": f"{under_45:.0f}% ✅" if under_45 >= 90 else f"{under_45:.0f}% ⚠️",
        "BTTS": f"{btts_rate:.0f}% ✅" if btts_rate >= 90 else f"{btts_rate:.0f}% ⚠️",
        "First Half Over 0.5 Goals": f"{fh_goals:.0f}% ✅" if fh_goals >= 85 else f"{fh_goals:.0f}% ⚠️"
    }

# --- Streamlit UI ---
st.set_page_config(page_title="Pattern Lock Radar", layout="wide")
st.title("🔐 Pattern Lock Radar - Global Fixture Tracker")

# Try primary API, fallback to backup if needed
try:
    fixtures = get_fixtures()
except:
    fixtures = get_fixtures_backup()

# Show only games with 1 or more high-confidence patterns
if fixtures:
    for home, away in fixtures:
        patterns = analyze_patterns(home, away)
        strong_hits = [v for v in patterns.values() if "✅" in v]
        if len(strong_hits) >= 1:
            st.subheader(f"📊 {home} vs {away}")
            for market, result in patterns.items():
                st.markdown(f"- **{market}**: {result}")
            st.markdown("---")
