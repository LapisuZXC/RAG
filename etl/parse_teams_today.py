from util.selenium_workflow import driver_context_manager, await_of_load
from util.csv_workflow import write_links
from util.datetime_util import get_date_current
from etl.parse_teams_all import extract_data, data_csv_format, TABLE_SELECTOR


URL = 'https://www.hltv.org/ranking/teams'
output_file = "Data/raw/team_ranking.csv"


def main():
    current_data = get_date_current()
    current_url = f"{URL}/{current_data}"
    print(f'Getting commands tier-list: {current_url}')

    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver
        
        print(f"Getting data from: {current_url}")
        driver.get(current_url)
        
        isValid = await_of_load(driver, TABLE_SELECTOR)
        if isValid:
            print("Found data")
            cur_data = extract_data(current_url, driver)
            write_links(output_file, cur_data, data_csv_format)
        else:
            print("Cant find data")


if __name__ == "__main__":
    main()