# import requests

# API_KEY = open("api_key.txt").read().strip()
# BASE_URL = "https://v3.football.api-sports.io"

# headers = {
#     "x-apisports-key": API_KEY
# }

# params = {
#     "league": 39,     # Premier League
#     "season": 2018,   
# }

# url = f"{BASE_URL}"

# print("Requesting fixtures for PL 2018...")

# resp = requests.get(url, headers=headers, params=params)

# print("Status:", resp.status_code)

# try:
#     data = resp.json()
#     print("Keys:", data.keys())
#     print("Results count:", data.get("results"))
#     print("First 1 item:", str(data.get("response", [])[:1])[:300])
# except Exception as e:
#     print("Failed to parse JSON:", e)
#     print("Raw response:", resp.text[:300])

import pandas as pd

df_stats = pd.read_csv("data_api_football/All_matches_2018-2025_with_stats.csv")

bund_2025 = df_stats[(df_stats["league"] == "Bundesliga") & (df_stats["season"] == 2025)]
unfinished = bund_2025[bund_2025["home_goals"].isna() & bund_2025["away_goals"].isna()]

print("Total Bundesliga 2025:", len(bund_2025))
print("Unfinished Bundesliga 2025:", len(unfinished))


