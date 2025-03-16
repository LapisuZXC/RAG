from datetime import datetime, timedelta
from typing import Literal


def get_date_range(
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
