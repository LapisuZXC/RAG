import pandas as pd
import re
from pathlib import Path

# экстрактим данные об игроках (а не просто ссылки), это практически мусорный файл для удобства

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = f"{BASE_DIR}/data/raw/team_ranking.csv"
OUTPUT_FILE = f"{BASE_DIR}/data/processed/players_ranking.csv"

df = pd.read_csv(INPUT_FILE)
unique_players = {}

for _, row in df.iterrows():
    members_dict = eval(row["Members"])
    for i in range(1, 6):
        player_name_key = f"Name_player_{i}"
        player_link_key = f"Link_player_{i}"

        if player_name_key in members_dict and player_link_key in members_dict:
            player_name = members_dict[player_name_key]
            player_link = members_dict[player_link_key]
            player_id_match = re.search(r"player/(\d+)/", player_link)
            player_id = player_id_match.group(1) if player_id_match else "Unknown"

            unique_players[player_name] = [
                player_id,
                player_link,
            ]  # чтобы без дубликатов

# Преобразуем словарь в DataFrame
unique_players_df = pd.DataFrame.from_dict(
    unique_players, orient="index", columns=["ID", "Ссылка"]
).reset_index().rename(columns={"index": "Имя"})

# Сохраняем в CSV
unique_players_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

