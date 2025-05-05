from typing import Dict, List, Union
import pandas as pd
import os
from datetime import datetime


def write_links(output_file: str, data: list[str], data_csv_format: Dict[str, Union[str, int, List[Dict[str, str]]]]) -> None:
    if not os.path.exists(output_file):
        data_frame = pd.DataFrame(data_csv_format)
        data_frame.to_csv(output_file, index=False)

    data_frame = pd.DataFrame(data)
    data_frame.to_csv(output_file, mode="a", index=False, header=False)

    print(f"Data written to {output_file}")
    return None

def get_last_date(output_file: str) -> datetime:
    try:
        csv_file = pd.read_csv(output_file)
        last_year = int(csv_file["Year"].iloc[-1])
        last_month = csv_file["Month"].iloc[-1]
        last_month = last_month[0].upper() + last_month[1:]  # Делаем первую букву заглавной 
        last_day = int(csv_file["Date"].iloc[-1])
        date = datetime.strptime(f"{last_year} {last_month} {last_day}", '%Y %B %d')
    except Exception as e:
        print(f"Error in csv_workflow get_last_date: {e}")
        date = datetime(2000, 1, 1)
    return date

def print_csv(file_path: str) -> None:
    print(pd.read_csv(file_path))
    return None