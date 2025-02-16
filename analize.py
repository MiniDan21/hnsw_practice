import os


def find_best_log(log_folder):
    best_time = None
    best_file = None

    for filename in os.listdir(log_folder):
        if filename.endswith(".log"):
            filepath = os.path.join(log_folder, filename)
            try:
                with open(filepath, "r") as f:
                    content = f.read().strip()
                    time_value = float(content)

                if best_time is None or time_value < best_time:
                    best_time = time_value
                    best_file = filename
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")

    if best_file is not None:
        best_file = os.path.splitext(best_file)[0]
    return best_file, best_time


# if __name__ == '__main__':
#     log_directory = 'path/to/log/folder'
#     best_filename, best_time = find_best_log(log_directory)
#     if best_filename is not None:
#         print(f"Лучшее время: {best_time} секунд, файл: {best_filename}")
#     else:
#         print("Лог файлы не найдены или произошла ошибка при чтении.")
