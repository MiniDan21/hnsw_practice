import os
import time
import argparse
from pathlib import Path

import hnswlib

from utils import (
    load_dsc_file,
    load_index,
    save_bf_search_result,
    load_bf_search_result,
)


def build_bf_index(dim, idx_dir: Path):
    target_filepath = idx_dir / "BF.idx"
    bf_index = hnswlib.BFIndex(space="l2", dim=dim)
    load_index(bf_index, str(target_filepath))

    return bf_index, target_filepath


def bf_search(bf_index, bf_path, data, q: Path, k=2, rewrite=False):
    bf_search_results: Path = bf_path / "BF.npy"
    if bf_search_results.exists() and not rewrite:
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
    rewrite=False,
    k=2,
):
    # Идем по списку dsc файлов
    for query in queries:
        data = load_dsc_file(query)
        num_elements, dim = data.shape
        target_dir = output_dir / query.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        # Идем по списку индексов
        for idx in index:
            if "BF" in str(idx):
                continue
            # Подгружаем BF-индекс
            bf_index, bf_path = build_bf_index(dim, Path(idx.parent))
            dsc_bf_results = bf_search(bf_index, target_dir, data, query, k, rewrite)

            target_idx_dir = target_dir / idx.stem
            target_idx_dir.mkdir(parents=True, exist_ok=True)
            print(f"Поиск в файле {query.stem}")

            # # Парсим название сгенерированного индекса по следующему формату '<название>_M_ef_thr-num'
            _, ef_c, M = list(map(int, idx.stem.split("_")[-1:-4:-1]))

            # Подгружаем сгенерированный ранее индекс
            hnsw_index = hnswlib.Index(space="l2", dim=dim)
            load_index(hnsw_index, str(idx))

            # Устанавливаем параметры поиска
            hnsw_index.set_ef(ef)
            hnsw_index.set_num_threads(thr_num)

            start_time = time.time()
            labels_hnsw, distances_hnsw = hnsw_index.knn_query(data, k)
            search_time = time.time() - start_time

            correct = 0
            for i in range(num_elements):
                for label in labels_hnsw[i]:
                    for correct_label in dsc_bf_results[i]:
                        if label == correct_label:
                            correct += 1
                            break

            recall = float(correct) / (k * num_elements)
            print("recall is :", recall)
            logpath = target_idx_dir / (
                idx.stem.split("_")[0] + f"_{ef}_{thr_num}" + ".log"
            )
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
    parser.add_argument(
        "--rewrite", action="store_true", help="Выполнить BF-поиск заново"
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

    search(
        idx,
        dsc,
        Path(args.output_dir),
        ef,
        thr_num,
        append=args.a,
        rewrite=args.rewrite,
    )


if __name__ == "__main__":
    main()
