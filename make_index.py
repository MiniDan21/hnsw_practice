import os
import time
import argparse
from pathlib import Path

import hnswlib

from utils import load_dsc_file, save_index


def make_index(
    input_file,
    output_dir,
    M=None,
    ef_construction=None,
    threads_num=None,
    brutforce=False,
    append=False,
):
    data = load_dsc_file(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    output_dir = os.path.join(output_dir, input_file.split("/")[-1])
    os.makedirs(output_dir, exist_ok=True)

    M_values = [2**i for i in range(2, 6)]
    ef_construction_values = list(range(50, 301, 50))
    threads_values = [os.cpu_count() // 2, os.cpu_count()]

    if M is not None:
        M_values = [M]
    if ef_construction is not None:
        ef_construction_values = [ef_construction]
    if threads_num is not None:
        threads_values = [threads_num]

    num_elements, dim = data.shape
    for M in M_values:
        for ef in ef_construction_values:
            for threads in threads_values:
                print(f"Строим индекс: M={M}, ef_construction={ef}, threads={threads}")
                hnsw_index = hnswlib.Index(space="l2", dim=dim)
                hnsw_index.init_index(
                    max_elements=num_elements, ef_construction=ef, M=M
                )
                hnsw_index.set_num_threads(threads)

                start_time = time.time()
                hnsw_index.add_items(data)
                build_time = time.time() - start_time

                idx_filename = f"{base_name.split('-')[0]}_{M}_{ef}_{threads}.idx"
                bf_idx_filename = f"BF.idx"
                log_filename = f"{base_name.split('-')[0]}_{M}_{ef}_{threads}.log"
                idx_filepath = os.path.join(output_dir, idx_filename)
                bf_idx_filepath = os.path.join(output_dir, bf_idx_filename)
                log_filepath = os.path.join(output_dir, log_filename)

                hnsw_index.save_index(idx_filepath)

                if not os.path.exists(bf_idx_filepath):
                    bf_index = hnswlib.BFIndex(space="l2", dim=dim)
                    bf_index.init_index(max_elements=num_elements)
                    bf_index.add_items(data)
                    bf_index.save_index(bf_idx_filepath)

                log_info = f"{input_file},{M},{ef},{threads},{build_time:.6f}\n"
                if append:
                    with open(log_filepath, "a") as log_file:
                        log_file.write(log_info)
                else:
                    with open(log_filepath, "w") as log_file:
                        log_file.write(log_info)

                print(f"Сохранён лог: {log_filepath}\n")


def make_indexes(
    input_dir,
    output_dir,
    M=None,
    ef_construction=None,
    threads_num=None,
    brutforce=False,
    append=False,
):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".dsc"):
            file_path = os.path.join(input_dir, filename)

            if os.path.isfile(file_path):
                make_index(
                    file_path,
                    output_dir,
                    M=M,
                    ef_construction=ef_construction,
                    threads_num=threads_num,
                    brutforce=brutforce,
                    append=append,
                )


def main():
    parser = argparse.ArgumentParser(
        description="Построение индексов для DSC файлов с использованием hnswlib"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_file", help="Путь к DSC файлу")
    group.add_argument("--input_dir", help="Путь к директории с DSC файлами")
    parser.add_argument(
        "--output_dir",
        default="./work-dir",
        help="Директория для сохранения выходных файлов",
    )
    parser.add_argument("--M", type=int, help="Параметр M")
    parser.add_argument("--ef", type=int, help="Параметр ef")
    parser.add_argument(
        "--thr_num", type=int, help="Количество потоков для построения индекса"
    )
    parser.add_argument(
        "-a", action="store_true", help="Добавить в логи результат, оставляя предыдущий"
    )
    # parser.add_argument("--analize_dir", help="Анализ папки с логами")
    # parser.add_argument(
    #     "--bf", action="store_true", help="Включение построения индекса по брутфорсингу"
    # )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if (args.M or args.ef or args.thr_num) and not (
        args.M and args.ef and args.thr_num
    ):
        parser.error(
            "Если указан хотя бы один из параметров --M, --ef или --thr_num, то необходимо указать все три."
        )

    M = args.M
    ef = args.ef
    thr_num = args.thr_num

    if args.input_file:
        make_index(
            args.input_file,
            args.output_dir,
            M=M,
            ef_construction=ef,
            threads_num=thr_num,
            append=args.a,
        )
    elif args.input_dir:
        make_indexes(
            args.input_dir,
            args.output_dir,
            M=M,
            ef_construction=ef,
            threads_num=thr_num,
            append=args.a,
        )


if __name__ == "__main__":
    main()
