import os
import time
import argparse
from pathlib import Path

import hnswlib

from utils import (
    load_dsc_file,
    build_index,
    save_index,
    save_bf_search_result,
    load_bf_search_result,
)


def build_bf_index(data, query: Path, target_dir: Path):
    target_filepath = target_dir / "BF.idx"
    try:
        # Пробуем подгрузить
        bf_index, _ = build_index(
            data, method=hnswlib.BFIndex, index_path=target_filepath
        )
    except FileNotFoundError:
        print(f"Делается BF индекс для {query.stem}")
        bf_index, _ = build_index(data, method=hnswlib.BFIndex)
        save_index(bf_index, str(target_filepath))
    return bf_index, target_filepath


def bf_search(bf_index, bf_path, data, q: Path, k=2):
    bf_search_results: Path = bf_path.parent / "BF.npy"
    if bf_search_results.exists():
        print(f"Выгружаются BF результаты из {bf_search_results}")
        labels_bf = load_bf_search_result(bf_search_results)
    else:
        print(f"Вычисляется по BF индекс для {q.stem}")
        labels_bf, _ = bf_index.knn_query(data, k)
        save_bf_search_result(labels_bf, str(bf_search_results))

    return labels_bf


def search(
    index: list[Path],
    queries: list[Path],
    output_dir: Path,
    ef,
    thr_num,
    append=False,
    k=2,
):
    # Идем по списку dsc файлов
    for query in queries:
        # Подгружаем данные
        data = load_dsc_file(query)
        # Создаем директорию для сохранения BF-индекса и результатов поисков по индексам
        target_dir = output_dir / query.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        # Подгружаем BF-индекс либо строим
        bf_index, bf_path = build_bf_index(data, query, target_dir)
        # Определяем лэйблы
        dsc_bf_results = bf_search(bf_index, bf_path, data, query, k)
        # Идем по списку индексов
        for idx in index:
            if "0_BF" in str(idx):
                continue
            print(f"Используется индекс {idx.stem}")
            target_idx_dir = target_dir / idx.stem
            target_idx_dir.mkdir(parents=True, exist_ok=True)
            print(f"Поиск в файле {query.stem}")

            # # Парсим название сгенерированного индекса по следующему формату '<название>_M_ef_thr-num'
            _, ef_c, M = list(map(int, idx.stem.split("_")[-1:-4:-1]))
            # hnsw_index, _ = build_index(
            #     data, M=M, ef_construction=ef_c, threads_num=thr_num
            # )

            # Подгружаем сгенерированный ранее индекс
            hnsw_index, _ = build_index(data, index_path=idx)
            # Устанавливаем параметры поиска
            hnsw_index.set_ef(ef)
            hnsw_index.set_num_threads(thr_num)

            start_time = time.time()
            labels_hnsw, distances_hnsw = hnsw_index.knn_query(data, k)
            search_time = time.time() - start_time

            correct = 0
            for i in range(data.shape[0]):
                for label in labels_hnsw[i]:
                    for correct_label in dsc_bf_results[i]:
                        if label == correct_label:
                            correct += 1
                            break

            recall = float(correct) / (k * data.shape[0])
            print("recall is :", recall)
            logpath = target_idx_dir / (idx.stem + ".log")
            log_info = f"{str(query)},{str(idx)},{M},{ef_c},{ef},{thr_num},{recall:.6f},{search_time:.6f}\n"
            if append:
                with open(logpath, "a") as log_file:
                    log_file.write(log_info)
            else:
                with open(logpath, "w") as log_file:
                    log_file.write(log_info)

            print(f"Сохранён лог: {logpath}\n")


def main():
    parser = argparse.ArgumentParser(description="Поиск по hnswlib индексу")
    parser.add_argument(
        "--output_dir",
        default="./search_results",
        help="Директория для сохранения лог файлов",
    )
    parser.add_argument("--ef", default=100, type=int, help="Значение ef для поиска")
    parser.add_argument(
        "--thr_num",
        default=os.cpu_count(),
        type=int,
        help="Количество потоков для поиска",
    )

    idx_group = parser.add_mutually_exclusive_group(required=True)
    idx_group.add_argument("--idx_file", help="Путь к IDX файлу с индексом")
    idx_group.add_argument("--idx_dir", help="Путь к директории с IDX файлами")

    dsc_group = parser.add_mutually_exclusive_group(required=True)
    dsc_group.add_argument("--dsc_file", help="Путь к DSC файлу с запросами")
    dsc_group.add_argument("--dsc_dir", help="Путь к директории с DSC файлами")

    parser.add_argument(
        "-a", action="store_true", help="Добавить в логи результат, оставляя предыдущий"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if (args.ef or args.thr_num) and not (args.ef and args.thr_num):
        parser.error(
            "Если указан хотя бы один из параметров --ef или --thr_num, то необходимо указать оба"
        )

    ef = args.ef
    thr_num = args.thr_num

    idx = (
        [Path(args.idx_file)]
        if args.idx_file
        else sorted(
            [
                file.resolve()
                for file in Path(args.idx_dir).iterdir()
                if file.is_file() and file.suffix.lower() == ".idx"
            ]
        )
    )
    dsc = (
        [Path(args.dsc_file)]
        if args.dsc_file
        else sorted(
            [
                file.resolve()
                for file in Path(args.dsc_dir).iterdir()
                if file.is_file() and file.suffix.lower() == ".dsc"
            ]
        )
    )

    search(idx, dsc, Path(args.output_dir), ef, thr_num, append=args.a)


if __name__ == "__main__":
    main()
