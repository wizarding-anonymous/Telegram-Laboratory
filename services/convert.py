import os
import chardet
import codecs
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для определения и конвертации файла в UTF-8
def convert_to_utf8(file_path):
    try:
        # Открываем файл и определяем его кодировку с помощью chardet
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)  # Определение кодировки

            # Проверка, была ли найдена кодировка
            if result['encoding'] is None:
                logger.warning(f"Не удалось определить кодировку файла {file_path}. Пропускаем.")
                return

            file_encoding = result['encoding']

        # Если кодировка уже UTF-8, пропускаем
        if file_encoding.lower() == 'utf-8':
            logger.info(f"Файл {file_path} уже в кодировке UTF-8.")
            return

        # Если кодировка не UTF-8, читаем файл с его текущей кодировкой и записываем в UTF-8
        with codecs.open(file_path, 'r', encoding=file_encoding, errors='ignore') as file:
            content = file.read()

        with codecs.open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        logger.info(f"Файл {file_path} успешно преобразован в кодировку UTF-8.")

    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {str(e)}")

# Функция для обхода всех файлов в папке и конвертации их в UTF-8
def convert_files_in_directory(directory: str, excluded_folders: list):
    for root, dirs, files in os.walk(directory):
        # Исключаем указанные папки из обхода
        dirs[:] = [d for d in dirs if d not in excluded_folders]

        for file in files:
            # Проверяем только текстовые файлы
            if file.endswith(".py") or file.endswith(".ini") or file.endswith(".txt"):
                file_path = os.path.join(root, file)
                convert_to_utf8(file_path)

# Укажите директорию для проверки и преобразования
directory_to_check = "C:/Users/Oleg/Documents/GitHub/tg_lab/services/data_storage_service"

# Список папок, которые нужно исключить из проверки
excluded_folders = ["venv", "__pycache__", "migrations"]

# Запускаем конвертацию всех файлов, кроме исключённых папок
convert_files_in_directory(directory_to_check, excluded_folders)

# Обрабатываем файл 'env.py' в папке миграций вручную
env_file = "C:/Users/Oleg/Documents/GitHub/tg_lab/services/data_storage_service/src/db/migrations/env.py"
convert_to_utf8(env_file)
