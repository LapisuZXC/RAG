from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Literal


def get_date_from(
    time_filter: Literal[
        "last_month", "last_3_months", "last_6_months", "2023-2024"
    ] = "last_3_months",
) -> str:
    """
    Возвращает строку с параметрами startDate и endDate в зависимости от выбранного фильтра времени.

    Параметры:
        time_filter (Literal["last_month", "last_3_months", "last_6_months", "2023-2024"]):
            Определяет временной диапазон для статистики. Может быть:
            - "last_month" (по умолчанию возвращает последние 30 дней),
            - "last_3_months" (по умолчанию возвращает последние 3 месяца),
            - "last_6_months" (возвращает последние 6 месяцев),
            - "2023-2024" (фиксированный диапазон с 01.01.2023 по 31.12.2024).

    Возвращает:
        str: Строку с параметрами startDate и endDate, готовую для использования в URL.

    Пример:
        base_url = "https://www.hltv.org/stats/teams"
        time_filter = get_date_range()  # Получаем параметры для последних 3 месяцев
        url = base_url + "?" + time_filter + "&rankingFilter=Top50"
        print(url)
    """
    today = datetime.today()
    match time_filter:
        case "last_month":
            start_date = today - timedelta(days=30)
        case "last_3_months":
            start_date = today - timedelta(days=90)
        case "last_6_months":
            start_date = today - timedelta(days=180)
        case "2023-2024":
            today = datetime(2024, 12, 31)
            start_date = datetime(2023, 1, 1)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")

    return f"startDate={start_date_str}&endDate={end_date_str}"


def get_date_current() -> datetime:
    """
    Возвращает текущий год, месяц (в формате слова с маленькой буквы) и день
    """

    current_data = datetime.today().strftime("%Y/%B/%d").lower()

    return current_data


def generate_date_list(year_from: int, year_to: int) -> list[str]:
    """
    Возвращает список всех дат в период с year_from до year_to в формате /год/месяц(наприме: march)/дата
    """
    if year_from > year_to:
        raise ValueError
    
    date_list = []
    start_date = datetime(year_from, 1, 1)
    end_date = datetime(year_to, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        date_list.append(f"/{current_date.year}/{current_date.strftime('%B').lower()}/{current_date.day}")
        current_date += timedelta(days=1)

    return date_list

def generate_date_list_every_week(start_date: int, end_date: int) -> list[str]:
    """
    Возвращает список всех дат каждые 7 дней
    """
    urls = []
    current_date = start_date
    while current_date <= end_date:
        url = f"/{current_date.year}/{current_date.strftime('%B').lower()}/{
            current_date.day
        }"
        urls.append(url)
        current_date += timedelta(days=7)  # Шаг в 7 дней
    return urls


def generate_month_list(monthes: int) -> list[str]:
    """
    Создаёт список месяцев в формате год/месяц (наприме: march)
    """
    today = datetime.now()
    last_months = []
    for i in range(0, monthes):
        month_date = today - relativedelta(months=i)
        month_str = month_date.strftime("%Y/%B").lower()
        last_months.append(month_str)

    return last_months[::-1]