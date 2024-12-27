import os
import io
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_encoding(file_path: str):
    """
    Проверяет кодировку файла и записывает в лог.
    """
    try:
        # Попытка открыть файл с кодировкой UTF-8
        with io.open(file_path, 'r', encoding='utf-8') as f:
            f.read()  # Пробуем прочитать файл
        logger.info(f"Файл {file_path} успешно открыт с кодировкой UTF-8.")
    except UnicodeDecodeError as e:
        # Логируем ошибку, если кодировка неправильная
        logger.error(f"Ошибка при открытии файла {file_path}. Кодировка неправильная: {str(e)}")
    except Exception as e:
        # Логируем другие возможные ошибки
        logger.error(f"Неизвестная ошибка при чтении файла {file_path}: {str(e)}")

def check_files_in_directory(directory: str, excluded_folders: list, specific_file: str = None):
    """
    Функция для обхода всех файлов в папке и подкаталогах, с исключением указанных папок.
    Принимает дополнительный параметр specific_file для проверки только одного файла.
    """
    for root, dirs, files in os.walk(directory):
        # Исключаем указанные папки из обхода
        dirs[:] = [d for d in dirs if d not in excluded_folders]
        
        for file in files:
            # Если указан конкретный файл для проверки, проверяем только его
            if specific_file and os.path.join(root, file) == specific_file:
                check_file_encoding(os.path.join(root, file))
            # Проверяем только файлы с расширениями .ini и .py, и добавляем условие для других файлов
            elif file.endswith(".ini") or file.endswith(".py"):
                file_path = os.path.join(root, file)
                check_file_encoding(file_path)

# Укажите директорию, в которой нужно искать файлы
directory_to_check = "C:/Users/Oleg/Documents/GitHub/tg_lab/services/data_storage_service"

# Список папок, которые нужно исключить из проверки
excluded_folders = ["venv", "migrations", "__pycache__"]

# Укажите конкретный файл, который нужно проверить
specific_file_to_check = "C:/Users/Oleg/Documents/GitHub/tg_lab/services/data_storage_service/src/db/migrations/env.py"

# Проверка файлов в указанной директории с исключением папок и проверкой конкретного файла
check_files_in_directory(directory_to_check, excluded_folders, specific_file=specific_file_to_check)
