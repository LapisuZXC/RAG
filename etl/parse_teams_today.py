from util.selenium_workflow import driver_context_manager, await_of_load
from util.datetime_util import get_date_current
from etl.parse_teams_all import extract_data, update_links, data_csv_format, TABLE_SELECTOR
import argparse

from logger.logger import Loger
log = Loger(__file__)


URL = 'https://www.hltv.org/ranking/teams'
output_file = "data/raw/team_ranking.csv"


def main(test_mode = False):
    log.prnt("Начали работу с файлом")

    current_data = get_date_current()
    current_url = f"{URL}/{current_data}"
    log.prnt(f'Getting commands tier-list: {current_url}')

    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver

        
        if test_mode:
            current_url = "https://www.hltv.org/ranking/teams/2025/april/14"
            current_data = "2025/april/14"


        log.prnt(f"Getting data from: {current_url}")
        driver.get(current_url)
        
        isValid = await_of_load(driver, TABLE_SELECTOR)
        if isValid:
            log.prnt("Found data")
            cur_data = extract_data(str("1/" + current_data), driver)
            update_links(output_file, cur_data, data_csv_format)
        else:
            log.prnt("Cant find data")


    log.prnt("Закончили работу с файлом")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)