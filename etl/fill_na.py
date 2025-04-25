import pandas as pd

INPUT_CSV_PATH = "data/processed/matches.csv"

OUTPUT_CSV_PATH = "data/processed/matches_cleaned.csv"

df = pd.read_csv(INPUT_CSV_PATH)

df = df.dropna(ignore_index=True)

df.to_csv(OUTPUT_CSV_PATH)
