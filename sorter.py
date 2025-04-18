import pandas as pd
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

# Загрузка данных
df = pd.read_csv('./data/processed/matches.csv')

# Создание описания для каждого матча
df['description'] = df.apply(
    lambda row: f"{row['true_name']} сыграли против {row['opponent']} {row['date']} на турнире {row['event']} на карте {row['map']}. "
    f"Результат: {'победа' if row['win_loss'] == 'W' else 'поражение'}.",
    axis=1
)

# Функция для фильтрации команд
def filter_teams(df):
    # Подсчет количества матчей и винрейта для каждой команды
    team_stats = df.groupby('true_name').agg(
        total_matches=('win_loss', 'count'),
        win_rate=('win_loss', lambda x: (x == 'W').mean())
    ).reset_index()
    
    # Фильтрация команд с >=5 матчей и винрейтом <=75%
    valid_teams = team_stats[
        (team_stats['total_matches'] >= 5) & 
        (team_stats['win_rate'] <= 0.75)
    ]['true_name']
    
    # Возвращаем отфильтрованный DataFrame
    return df[df['true_name'].isin(valid_teams)]

# Функция для управления папками с эмбеддингами
def manage_embeddings_folder():
    embeddings_dir = './data/embeddings'
    old_embeddings_dir = './data/old_embeddings'
    
    os.makedirs(embeddings_dir, exist_ok=True)
    os.makedirs(old_embeddings_dir, exist_ok=True)
    
    if os.listdir(embeddings_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_folder = os.path.join(old_embeddings_dir, f'embeddings_{timestamp}')
        os.makedirs(new_folder, exist_ok=True)
        
        for file in os.listdir(embeddings_dir):
            os.rename(
                os.path.join(embeddings_dir, file),
                os.path.join(new_folder, file)
            )
    
    return embeddings_dir

# Создание и сохранение эмбеддингов
def create_and_save_embeddings(filtered_df, embeddings_dir):
    # Сортировка по дате
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    df_sorted = filtered_df.sort_values('date')
    
    # Инициализация модели
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Создание эмбеддингов
    embeddings = embedding_model.encode(df_sorted['description'].tolist(), show_progress_bar=True)
    
    # Сохранение с метаданными
    embeddings_data = {
        'embeddings': embeddings,
        'dates': df_sorted['date'].dt.strftime('%Y-%m-%d').tolist(),
        'descriptions': df_sorted['description'].tolist(),
        'team_names': df_sorted['true_name'].tolist()
    }
    
    save_path = os.path.join(embeddings_dir, f'embeddings_{datetime.now().strftime("%Y%m%d")}.npz')
    np.savez(save_path, **embeddings_data)
    
    return embeddings_data

# Основной процесс
if __name__ == "__main__":
    # Фильтрация данных
    filtered_df = filter_teams(df)
    print(f"После фильтрации осталось {len(filtered_df)} матчей")
    
    # Управление папками
    embeddings_dir = manage_embeddings_folder()
    
    # Создание эмбеддингов
    embeddings_data = create_and_save_embeddings(filtered_df, embeddings_dir)
    
    print(f"Эмбеддинги успешно созданы и сохранены в {embeddings_dir}")
    print(f"Учтено {len(embeddings_data['descriptions'])} матчей от {len(set(embeddings_data['team_names']))} команд")