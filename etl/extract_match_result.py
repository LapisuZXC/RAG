import pandas as pd

from util.selenium_workflow import driver_context_manager, await_of_load

PATH_TO_MATCHES = "data/processed/matches.csv"


def prepare_df():
    df = pd.read_csv(PATH_TO_MATCHES)

    source = df[["team_id", "opponent_id", "date", "match_link"]].copy()
    del df
    source['series_result'] = None
    return source


def parse_series_results(link: str, driver) -> str:
