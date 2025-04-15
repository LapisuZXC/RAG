import os


from logger.logger import Loger
log = Loger(__file__)


from etl.parse_teams_today import main as parse_teams_today_main  # 1

from etl.parse_news_links import main as parse_news_links_main   # 1
from etl.parse_news_text import main as parse_news_text_main     # 2


TEST_MODE = False

def create_data_dir():
    log.prnt("Создаём директории данных")
    try:
        os.mkdir("data/raw")
    except:
        pass
    try:
        os.mkdir("data/processed")
    except:
        pass
    try:
        os.mkdir("data/embedding")
    except:
        pass

    log.prnt("Директории данных созданы")


def main():
    log.prnt("Начали работу с файлом")

    create_data_dir()

    parse_teams_today_main(TEST_MODE)

    parse_news_links_main()

    parse_news_text_main(TEST_MODE)

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()