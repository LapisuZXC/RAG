import pandas as pd
import re
from pathlib import Path

# экстрактим данные об игроках (а не просто ссылки), это практически мусорный файл для удобства


# чтобы нормально работала структура проекта
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = f'{BASE_DIR}/data/processed/team_ranking.csv'
OUTPUT_FILE = f'{BASE_DIR}/data/processed/players_ranking.csv'

df = pd.read_csv(INPUT_FILE)
unique_players = {}

for _, row in df.iterrows():
    members_dict = eval(row['Members'])
    
    for i in range(1, 6):
        player_name_key = f'Name_player{i}'
        player_link_key = f'Link_player{i}'
        
        if player_name_key in members_dict and player_link_key in members_dict:
            player_name = members_dict[player_name_key]
            player_link = members_dict[player_link_key]
            player_id_match = re.search(r'player/(\d+)/', player_link)
            player_id = player_id_match.group(1) if player_id_match else "Unknown"
            
            unique_players[player_name] = (player_id, player_link)  # чтобы чтоб без дупликатов

unique_players_df = pd.DataFrame(unique_players.items(), columns=["Player Name", "Player Info"])
unique_players_df[['Player ID', 'Link']] = pd.DataFrame(unique_players_df['Player Info'].tolist(), index=unique_players_df.index)
unique_players_df.drop(columns=['Player Info'], inplace=True)
unique_players_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

