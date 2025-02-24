import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Необходимо для 3D графиков
import numpy as np
from scipy.interpolate import griddata
import argparse


def plot_xyz(file_path, x=None, y=None, z1=None, z2=None, smooth=False):
    """
    Читает CSV файл формата:
      input.dsc, test.dsc, M, ef_constr, ef, num_threads, recall, time
    и строит два 3D графика:
      - Первый график: x - ef, y - num_threads, z - recall
      - Второй график: x - ef, y - num_threads, z - time

    При smooth=True данные интерполируются для построения гладкой поверхности.
    """
    x = x or "M"
    y = y or "ef_constr"
    z1 = z1 or "recall"
    z2 = z2 or "time"
    # Чтение данных
    data = pd.read_csv(file_path)

    # Создание фигуры с двумя подграфиками
    fig = plt.figure(figsize=(14, 6))

    # Первый подграфик для recall
    ax1 = fig.add_subplot(121, projection="3d")
    if smooth:
        # Создаем регулярную сетку по осям x и y
        xi = np.linspace(data[x].min(), data[x].max(), 100)
        yi = np.linspace(data[y].min(), data[y].max(), 100)
        xi, yi = np.meshgrid(xi, yi)
        # Интерполируем значения z1 (recall) на сетке
        zi = griddata((data[x], data[y]), data[z1], (xi, yi), method="cubic")
        # Построение гладкой поверхности
        ax1.plot_surface(xi, yi, zi, cmap="viridis", edgecolor="none", alpha=0.8)
    else:
        ax1.scatter(data[x], data[y], data[z1], c="blue", marker="o", s=50)
    ax1.set_xlabel(x)
    ax1.set_ylabel(y)
    ax1.set_zlabel(z1)
    ax1.set_title(f"3D график: {x} vs {y} vs {z1}")

    # Второй подграфик для time
    ax2 = fig.add_subplot(122, projection="3d")
    if smooth:
        xi = np.linspace(data[x].min(), data[x].max(), 100)
        yi = np.linspace(data[y].min(), data[y].max(), 100)
        xi, yi = np.meshgrid(xi, yi)
        zi = griddata((data[x], data[y]), data[z2], (xi, yi), method="cubic")
        ax2.plot_surface(xi, yi, zi, cmap="plasma", edgecolor="none", alpha=0.8)
    else:
        ax2.scatter(data[x], data[y], data[z2], c="red", marker="^", s=50)
    ax2.set_xlabel(x)
    ax2.set_ylabel(y)
    ax2.set_zlabel(z2)
    ax2.set_title(f"3D график: {x} vs {y} vs {z2}")

    # Подгонка макета и отображение графиков
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Визуализация CSV данных с использованием matplotlib"
    )

    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Путь к CSV файлу формата: input.dsc, test.dsc, M, ef_constr, ef, num_threads, recall, time",
    )

    parser.add_argument("-x", type=str, help="Ось X. По умолчанию M")
    parser.add_argument("-y", type=str, help="Ось Y. По умолчанию ef_constr")
    parser.add_argument("-z1", type=str, help="Ось Z. По умолчанию recall")
    parser.add_argument("-z2", type=str, help="Ось Z. По умолчанию time")
    parser.add_argument(
        "--smooth", action="store_true", help="Построить сглаженную аппроксимацию"
    )

    args = parser.parse_args()

    plot_xyz(args.csv, x=args.x, y=args.y, z1=args.z1, z2=args.z2, smooth=args.smooth)
