from etl.parse_teams_today import main as parse_teams_today_main  # 1

from etl.parse_news_links import main as parse_news_links_main   # 1

from etl.parse_news_text import main as parse_news_text_main     # 2


from logger.logger import Loger
log = Loger(__file__)

TEST_MODE = True


def main():
    log.prnt("Начали работу с файлом")

    parse_teams_today_main()

    parse_news_links_main(TEST_MODE)

    parse_news_text_main(TEST_MODE)

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()