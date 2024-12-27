import os
import pyperclip

# Папка для сканирования
root_folder = "auth_service"

# Списки исключений
excluded_files = ["setup.cfg", "alembic.log", "auth_service.log"]  # Укажите файлы, которые нужно пропустить
excluded_folders = ["venv","migrations","__pycache__"]  # Укажите папки, которые нужно пропустить

def collect_files_with_contents(folder, excluded_files, excluded_folders):
    file_list = []

    for root, dirs, files in os.walk(folder):
        # Исключение папок
        dirs[:] = [d for d in dirs if d not in excluded_folders]

        for file in files:
            if file not in excluded_files:
                relative_path = os.path.relpath(os.path.join(root, file), folder)
                full_path = os.path.join(root, file)

                # Чтение содержимого файла
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (UnicodeDecodeError, IOError):
                    content = "[Не удалось прочитать файл]"

                # Добавление пути и содержимого в список
                file_list.append(f"[{relative_path}]\n{content}\n")

    return file_list

def main():
    # Проверка, существует ли папка
    if not os.path.exists(root_folder):
        print(f"Папка '{root_folder}' не найдена. Проверьте путь.")
        return

    # Получаем список файлов с содержимым
    files_with_contents = collect_files_with_contents(root_folder, excluded_files, excluded_folders)

    if not files_with_contents:
        print("Нет файлов для копирования в буфер обмена.")
        return

    # Формируем текст для буфера обмена
    clipboard_text = "\n".join(files_with_contents)

    # Копируем в буфер обмена
    try:
        pyperclip.copy(clipboard_text)
        print("Список файлов с содержимым скопирован в буфер обмена!")
    except pyperclip.PyperclipException:
        print("Ошибка при копировании в буфер обмена. Убедитесь, что pyperclip поддерживает вашу ОС.")

if __name__ == "__main__":
    main()
