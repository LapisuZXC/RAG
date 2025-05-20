import pandas as pd
import re

INPUT_FILE = "data/processed/player_stats.csv"
OUTPUT_FILE = "data/processed/unique_players.csv"
# Шаг 1: Загрузка исходного CSV
df = pd.read_csv(INPUT_FILE)

# Шаг 2: Функция для извлечения никнейма из строки


def extract_nickname(name):
    match = re.search(r"'([^']+)'", name)
    return match.group(1) if match else name


# Шаг 3: Применяем функцию ко всем строкам в столбце "Player Name"
df["Nickname"] = df["Player Name"].apply(extract_nickname)

# Шаг 4: Оставляем только нужные столбцы
new_df = df[["Nickname", "Player ID"]]
new_df.drop_duplicates(inplace=True)
# Шаг 5: Сохраняем результат в новый CSV
new_df.to_csv(OUTPUT_FILE, index=False)
