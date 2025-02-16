import time
import argparse
from pathlib import Path

import hnswlib

from utils import load_dsc_file, build_index

dsc_bf_results = {}

# def get_BF_result(data, bf_path, query, k=2):
#     global dsc_bf_results

#     method = hnswlib.BFIndex
#     bf_index, _ = build_index(data, index_path=str(bf_path), method=method)
#     labels_bf, distances_bf = bf_index.knn_query(data, k)
#     dsc_bf_results[query] = labels_bf

#     return labels_bf


def search(
    index: list[Path], queries: list[Path], output_dir: Path, ef=None, thr_num=None, k=2
):
    dsc_bf_results = {}

    for q in queries:
        data = load_dsc_file(q)
        print(f"Делается BF индекс для {q.stem}")
        bf_index, _ = build_index(data, method=hnswlib.BFIndex)
        print(f"Вычисляется по BF индекс для {q.stem}")
        labels_bf, distances_bf = bf_index.knn_query(data, k)
        dsc_bf_results[q] = labels_bf

    for idx in index:
        print(f"Используется индекс {idx.stem}")
        target_output_dir = output_dir / idx.stem
        target_output_dir.mkdir(parents=True, exist_ok=True)
        if "0_BF" in str(idx):
            continue
        for query in queries:
            print(f"Поиск в файле {query.stem}")
            data = load_dsc_file(query)
            thr_num, ef_c, M = list(map(int, str(idx.stem).split("_")[-1:-4:-1]))
            hnsw_index, _ = build_index(
                data, M=M, ef_construction=ef_c, threads_num=thr_num
            )
            hnsw_index.set_ef(ef)

            start_time = time.time()
            labels_hnsw, distances_hnsw = hnsw_index.knn_query(data, k)
            build_time = time.time() - start_time

            correct = 0
            for i in range(data.shape[0]):
                for label in labels_hnsw[i]:
                    for correct_label in dsc_bf_results[query][i]:
                        if label == correct_label:
                            correct += 1
                            break

            recall = float(correct) / (k * data.shape[0])
            print("recall is :", recall)
            logpath = target_output_dir / query.stem
            with open(logpath, "w") as log_file:
                log_file.write(f"{recall:.6f} {build_time:.6f}\n")

            print(f"Сохранён лог: {logpath}\n")


def main():
    parser = argparse.ArgumentParser(description="Поиск по hnswlib индексу")
    parser.add_argument(
        "--output_dir",
        default="./search_results",
        help="Папка для сохранения лог файлов",
    )
    parser.add_argument("--ef", type=int, help="Значение ef для поиска")
    parser.add_argument("--thr_num", type=int, help="Количество потоков для поиска")

    idx_group = parser.add_mutually_exclusive_group(required=True)
    idx_group.add_argument("--idx_file", help="Путь к IDX файлу с индексом")
    idx_group.add_argument("--idx_dir", help="Путь к директории с IDX файлами")

    dsc_group = parser.add_mutually_exclusive_group(required=True)
    dsc_group.add_argument("--dsc_file", help="Путь к DSC файлу с запросами")
    dsc_group.add_argument("--dsc_dir", help="Путь к директории с DSC файлами")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if (args.ef or args.thr_num) and not (args.ef and args.thr_num):
        parser.error(
            "Если указан хотя бы один из параметров --ef или --thr_num, то необходимо указать оба."
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

    search(idx, dsc, Path(args.output_dir), ef, thr_num)


if __name__ == "__main__":
    main()
