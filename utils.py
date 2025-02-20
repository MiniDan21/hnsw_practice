import os
import time
from pathlib import Path
from typing import Optional

import hnswlib
import rasterio


def save_index(index, index_path):
    print("\nСохранение индекса по пути: '%s'" % index_path)
    index.save_index(index_path)


def load_index(index, index_path):
    print("\nВыгрузка индекса из '%s'\n" % index_path)
    index.load_index(index_path)


def load_dsc_file(filepath):
    try:
        with rasterio.open(filepath) as src:
            data = src.read()
    except Exception as e:
        raise ValueError(f"Ошибка при загрузке файла {filepath}: {e}")
    return data.squeeze()


def build_index(
    data,
    M=None,
    ef_construction=None,
    threads_num=os.cpu_count(),  # // 2
    method=hnswlib.Index,
    index_path: Optional[Path] = None,
):
    build_time = 0.0
    num_elements, dim = data.shape
    index = method(space="l2", dim=dim)

    # Если указан путь к индексу, то выгрузит его
    if index_path is not None:
        if index_path.exists():
            start_time = time.time()
            load_index(index, str(index_path))
            build_time = time.time() - start_time
            return index, build_time
        else:
            raise FileNotFoundError(index_path)

    max_elements = 2 * num_elements

    if method == hnswlib.BFIndex:
        index.init_index(max_elements=max_elements)
    else:
        index.init_index(
            max_elements=max_elements,
            ef_construction=ef_construction,
            M=M,
            allow_replace_deleted=True,
        )

    index.set_num_threads(threads_num)
    start_time = time.time()
    index.add_items(data)
    build_time = time.time() - start_time

    return index, build_time
