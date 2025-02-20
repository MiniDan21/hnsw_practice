import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Необходимо для 3D графиков
import argparse


def plot_first_csv(file_path):
    """
    Читает CSV файл формата:
      input.dsc, M, ef_constr, num_threads, time
    и строит 3D график:
      x - M, y - ef_constr, z - time,
    где данные группируются по 'num_threads'.
    """
    # Чтение данных
    data = pd.read_csv(file_path)

    # Группировка по num_threads
    groups = data.groupby("num_threads")

    # Создание фигуры и 3D оси
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Построение точек для каждой группы
    for thread_val, group in groups:
        ax.scatter(
            group["M"],
            group["ef_constr"],
            group["time"],
            label=f"num_threads = {thread_val}",
            s=50,
        )

    # Настройка подписей осей и заголовка
    ax.set_xlabel("M")
    ax.set_ylabel("ef_constr")
    ax.set_zlabel("time")
    ax.set_title("3D график: M vs ef_constr vs time (по num_threads)")
    ax.legend()

    # Отображение графика
    plt.show()


def plot_second_csv(file_path):
    """
    Читает CSV файл формата:
      input.dsc, test.dsc, M, ef_constr, ef, num_threads, recall, time
    и строит два 3D графика:
      - Первый график: x - ef, y - num_threads, z - recall
      - Второй график: x - ef, y - num_threads, z - time
    """
    # Чтение данных
    data = pd.read_csv(file_path)

    # Создание фигуры с двумя подграфиками
    fig = plt.figure(figsize=(14, 6))

    # Первый подграфик для recall
    ax1 = fig.add_subplot(121, projection="3d")
    ax1.scatter(
        data["ef"], data["num_threads"], data["recall"], c="blue", marker="o", s=50
    )
    ax1.set_xlabel("ef")
    ax1.set_ylabel("num_threads")
    ax1.set_zlabel("recall")
    ax1.set_title("3D график: ef vs num_threads vs recall")

    # Второй подграфик для time
    ax2 = fig.add_subplot(122, projection="3d")
    ax2.scatter(
        data["ef"], data["num_threads"], data["time"], c="red", marker="^", s=50
    )
    ax2.set_xlabel("ef")
    ax2.set_ylabel("num_threads")
    ax2.set_zlabel("time")
    ax2.set_title("3D график: ef vs num_threads vs time")

    # Подгонка макета и отображение графиков
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Визуализация CSV данных с использованием matplotlib"
    )
    parser.add_argument(
        "--index_csv",
        type=str,
        help="Путь к CSV файлу формата: input.dsc, M, ef_constr, num_threads, time",
    )
    parser.add_argument(
        "--search_csv",
        type=str,
        help="Путь к CSV файлу формата: input.dsc, test.dsc, M, ef_constr, ef, num_threads, recall, time",
    )
    args = parser.parse_args()

    if args.index_csv:
        plot_first_csv(args.index_csv)
    if args.search_csv:
        plot_second_csv(args.search_csv)
