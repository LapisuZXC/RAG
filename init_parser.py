from etl.parse_teams_all import main as parse_teams_all_main  # 1

from etl.id_extract import main as id_extract_main    # 2

from etl.parse_match_history import main as parse_match_history_main  # 3

from etl.extract_match_id import main as extract_match_id_main  # 4

from etl.parse_map_picks import main as parse_map_picks_main  # 5



from logger.logger import Loger
log = Loger(__file__)

TEST_MODE = True

def main():
    log.prnt("Начали работу с файлом")

    parse_teams_all_main(TEST_MODE)

    id_extract_main()

    parse_match_history_main(TEST_MODE)

    extract_match_id_main()

    parse_map_picks_main(TEST_MODE)

    log.prnt("Закончили работу с файлом")



if __name__ == "__main__":
    main()
