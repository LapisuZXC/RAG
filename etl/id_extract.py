import pandas as pd
import re


from logger.logger import Loger
log = Loger(__file__)



def main():
    log.prnt("Начали работу с файлом")

    # Загружаем CSV (замени 'your_file.csv' на свой файл)
    df = pd.read_csv('data/raw/team_ranking.csv')

    # Оставляем только уникальные команды
    df_unique = df[['Name_of_team', 'Link']].drop_duplicates()

    # Функция для извлечения ID команды из ссылки
    def extract_team_id(link):
        match = re.search(r'/team/(\d+)/', link)
        return match.group(1) if match else None

    # Чистим ссылки и извлекаем ID
    df_unique['Link'] = df_unique['Link'].str.strip("[]'")  # Убираем лишние символы
    df_unique['team_id'] = df_unique['Link'].apply(extract_team_id)

    # Оставляем только нужные столбцы и переименовываем
    df_final = df_unique[['Name_of_team', 'team_id']].rename(columns={'Name_of_team': 'team_name'})

    # Сохраняем в CSV
    df_final.to_csv('data/processed/unique_teams.csv', index=False)

    log.prnt("Файл unique_teams.csv успешно сохранён!")
    
    log.prnt("Закончили работу с файлом")



if __name__ == "__main__":
    main()
