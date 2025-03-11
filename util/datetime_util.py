from datetime import datetime, timedelta


def get_date_range(time_filter: str = "last_3_months"):
    """
    Возвращает строку с параметрами startDate и endDate в зависимости от выбранного фильтра времени.

    Параметры:
        time_filter (str): Определяет временной диапазон для статистики. Может быть:
            - "last_month" (по умолчанию возвращает последние 30 дней),
            - "last_3_months" (по умолчанию возвращает последние 3 месяца),
            - "last_6_months" (возвращает последние 6 месяцев).

    Возвращает:
        str: Строку с параметрами startDate и endDate, готовую для использования в URL.

    Пример:
        base_url = "https://www.hltv.org/stats/teams"
        time_filter = get_date_range()  # Получаем параметры для последних 3 месяцев
        url = base_url + "?" + time_filter + "&rankingFilter=Top50"
        print(url)
        # Вывод: https://www.hltv.org/stats/teams?startDate=2024-12-11&endDate=2025-03-11&rankingFilter=Top50
    """
    # Получаем текущую дату
    today = datetime.today()

    # В зависимости от выбора времени фильтра, вычисляем соответствующий диапазон
    if time_filter == "last_month":
        # За последний месяц (30 дней)
        start_date = today - timedelta(days=30)
    elif time_filter == "last_3_months":
        # За последние 3 месяца
        # Среднее количество дней в месяце - 30
        start_date = today - timedelta(days=90)
    elif time_filter == "last_6_months":
        # За последние 6 месяцев
        start_date = today - timedelta(days=180)  # 6 месяцев * 30 дней
    else:
        # По умолчанию последние 3 месяца
        start_date = today - timedelta(days=90)

    # Форматируем даты в нужный формат для URL
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")

    return f"startDate={start_date_str}&endDate={end_date_str}"
