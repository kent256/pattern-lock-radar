import requests
import streamlit as st

# API Config
API_KEY = "eb716181022347133f61611c3c00831a"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Function to get upcoming fixtures
def get_fixtures():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    query = {"next": 10}  # You can increase this number
    response = requests.get(url, headers=HEADERS, params=query)
    data = response.json()
    return data['response']

# Simulate recent form for now
from random import randint, choice
def mock_form():
    return {
        "goals_scored": [randint(0, 3) for _ in range(10)],
        "goals_conceded": [randint(0, 3) for _ in range(10)],
        "bt_ts": [choice([True, False]) for _ in range(10)],
        "first_half_goals": [randint(0, 2) for _ in range(10)],
    }

# Pattern Detection Logic
def analyze_patterns(home, away):
    home_form = mock_form()
    away_form = mock_form()

    over_05 = sum([g > 0 for g in home_form["goals_scored"] + away_form["goals_scored"]]) / 20 * 100
    total_goals = [h + a for h, a in zip(home_form['goals_scored'], home_form['goals_conceded'])]
    total_goals += [h + a for h, a in zip(away_form['goals_scored'], away_form['goals_conceded'])]
    under_35 = sum([g < 4 for g in total_goals]) / 20 * 100
    btts_rate = sum(home_form['bt_ts'] + away_form['bt_ts']) / 20 * 100
    fh_goals = sum([g > 0 for g in home_form['first_half_goals'] + away_form['first_half_goals']]) / 20 * 100

    return {
        "Over 0.5 Goals": f"{over_05:.0f}% ✅" if over_05 == 100 else f"{over_05:.0f}% ⚠️",
        "Under 3.5 Goals": f"{under_35:.0f}% ✅" if under_35 >= 90 else f"{under_35:.0f}% ⚠️",
        "BTTS": f"{btts_rate:.0f}% ✅" if btts_rate >= 90 else f"{btts_rate:.0f}% ⚠️",
        "First Half Over 0.5 Goals": f"{fh_goals:.0f}% ✅" if fh_goals >= 85 else f"{fh_goals:.0f}% ⚠️"
    }

# Streamlit App Layout
st.set_page_config(page_title="Pattern Lock Radar", layout="wide")
st.title("🔐 Pattern Lock Radar - Global Fixture Tracker")

fixtures = get_fixtures()

for match in fixtures:
    teams = match['teams']
    home = teams['home']['name']
    away = teams['away']['name']
    st.subheader(f"📊 {home} vs {away}")
    patterns = analyze_patterns(home, away)
    for market, result in patterns.items():
        st.markdown(f"- **{market}**: {result}")
    st.markdown("---")
