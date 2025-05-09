import pandas as pd
import re


from logger.logger import Loger

log = Loger(__file__)


def extract_match_id(url):
    """Извлекает ID матча из ссылки"""
    if isinstance(url, str):  # Проверяем, является ли url строкой
        match = re.search(r"mapstatsid/(\d+)/", url)
        return match.group(1) if match else None
    return None


def load_team_ids(team_file):
    """Загружает соответствие team_name -> team_id из CSV"""
    team_df = pd.read_csv(team_file)
    team_df["team_name"] = team_df[
        "team_name"
    ].str.lower()  # Приводим к нижнему регистру
    return dict(zip(team_df["team_name"], team_df["team_id"]))


def modify_csv(input_file, team_file):
    """Модифицирует CSV, добавляя ID матча и team_id/opponent_id"""
    df = pd.read_csv(input_file)
    team_ids = load_team_ids(team_file)

    # Добавляем match_id, если его ещё нет
    if "match_id" not in df.columns:
        df.insert(0, "match_id", df["match_link"].apply(extract_match_id))
    else:
        df["match_id"] = df["match_link"].apply(extract_match_id)

    # Добавляем team_id, если его нет
    if "team_id" not in df.columns:
        df.insert(
            2, "team_id", df["team_name"].str.lower().map(
                team_ids).astype("Int64")
        )
    else:
        df["team_id"] = df["team_name"].str.lower().map(
            team_ids).astype("Int64")

    # Добавляем opponent_id, если его нет
    if "opponent_id" not in df.columns:
        df.insert(
            6, "opponent_id", df["opponent"].str.lower().map(
                team_ids).astype("Int64")
        )
    else:
        df["opponent_id"] = df["opponent"].str.lower().map(
            team_ids).astype("Int64")

    # Упорядочиваем столбцы по требованиям
    columns_order = [
        "match_id",
        "team_name",
        "team_id",
        "date",
        "event",
        "opponent",
        "opponent_id",
        "map",
        "result",
        "win_loss",
        "match_link",
    ]
    df = df[columns_order]

    df.to_csv(input_file, index=False)
    log.prnt(f"Файл обновлён: {input_file}")


def main():
    log.prnt("Начали работу с файлом")
    modify_csv("data/processed/matches.csv", "data/processed/unique_teams.csv")
    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()
