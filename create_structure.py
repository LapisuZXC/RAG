import os

base_dir = os.getcwd()
print(f"Текущая рабочая директория: {base_dir}")

directories = [
    "data/raw",
    "data/processed",
    "data/embeddings",
    "etl",
    "models",
    "retriever",
    "notebooks",
    "config",
    "scripts",
]


def create_directories(base, dirs):
    for directory in dirs:
        path = os.path.join(base, directory)
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Директория '{path}' успешно создана или уже существует.")
        except Exception as e:
            print(f"Ошибка при создании директории '{path}': {e}")


if __name__ == "__main__":
    create_directories(base_dir, directories)
