from typing import Dict, List, Union
import pandas as pd
import os


def write_links(output_file: str, data: list[str], data_csv_format: Dict[str, Union[str, int, List[Dict[str, str]]]]) -> None:
    if not os.path.exists(output_file):
        data_frame = pd.DataFrame(data_csv_format)
        data_frame.to_csv(output_file, index=False)

    data_frame = pd.DataFrame(data)
    data_frame.to_csv(output_file, mode="a", index=False, header=False)

    print(f"Data written to {output_file}")
    return None


def print_csv(file_path: str) -> None:
    print(pd.read_csv(file_path))
    return None