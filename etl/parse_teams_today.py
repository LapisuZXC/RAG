from util.selenium_workflow import driver_context_manager, await_of_load
from util.csv_workflow import write_links
from util.datetime_util import get_date_current
from etl.parse_teams_all import extract_data, data_csv_format, TABLE_SELECTOR


from logger.logger import Loger
log = Loger(__file__)


URL = 'https://www.hltv.org/ranking/teams'
output_file = "data/raw/team_ranking.csv"


def main(TEST_MODE = False):
    log.prnt("Начали работу с файлом")

    current_data = get_date_current()
    current_url = f"{URL}/{current_data}"
    log.prnt(f'Getting commands tier-list: {current_url}')

    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver

        
        if TEST_MODE:
            current_url = "https://www.hltv.org/ranking/teams/2025/april/14"
            current_data = "2025/april/14"


        log.prnt(f"Getting data from: {current_url}")
        driver.get(current_url)
        
        isValid = await_of_load(driver, TABLE_SELECTOR)
        if isValid:
            log.prnt("Found data")
            cur_data = extract_data(str("1/" + current_data), driver)
            write_links(output_file, cur_data, data_csv_format)
        else:
            log.prnt("Cant find data")


    log.prnt("Закончили работу с файлом")

if __name__ == "__main__":
    main()