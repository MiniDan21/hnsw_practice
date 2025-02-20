import os
import argparse
from pathlib import Path

import hnswlib

from utils import load_dsc_file, build_index, save_index


def make_index(
    input_file,
    output_dir,
    M=None,
    ef_construction=None,
    threads_num=None,
    brutforce=False,
):
    data = load_dsc_file(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # if brutforce:
    #     print(f"Строим BF-индекс")
    #     index, build_time = build_index(data, method=hnswlib.BFIndex)
    #     target_bf_output = os.path.join(
    #         output_dir, f"{base_name.split('-')[0]}_0_BF.idx"
    #     )
    #     target_log_output = os.path.join(
    #         output_dir, f"{base_name.split('-')[0]}_0_BF.log"
    #     )
    #     save_index(index, target_bf_output)
    #     with open(target_log_output, "w") as log_file:
    #         log_file.write(f"{build_time:.6f}\n")

    #     print(f"Сохранён лог: {target_log_output}\n")

    M_values = [2**i for i in range(2, 6)]
    ef_construction_values = list(range(50, 301, 50))
    threads_values = [os.cpu_count() // 2, os.cpu_count()]

    if M is not None:
        M_values = [M]
    if ef_construction is not None:
        ef_construction_values = [ef_construction]
    if threads_num is not None:
        threads_values = [threads_num]

    for M in M_values:
        for ef in ef_construction_values:
            for threads in threads_values:
                print(f"Строим индекс: M={M}, ef_construction={ef}, threads={threads}")
                index, build_time = build_index(
                    data, M=M, ef_construction=ef, threads_num=threads
                )

                idx_filename = f"{base_name.split('-')[0]}_{M}_{ef}_{threads}.idx"
                log_filename = f"{base_name.split('-')[0]}_{M}_{ef}_{threads}.log"
                idx_filepath = os.path.join(output_dir, idx_filename)
                log_filepath = os.path.join(output_dir, log_filename)

                save_index(index, idx_filepath)

                with open(log_filepath, "w") as log_file:
                    log_file.write(f"{build_time:.6f}\n")

                print(f"Сохранён лог: {log_filepath}\n")


def make_indexes(
    input_dir,
    output_dir,
    M=None,
    ef_construction=None,
    threads_num=None,
    brutforce=False,
):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".dsc"):
            file_path = os.path.join(input_dir, filename)
            target_output_dir = os.path.join(output_dir, filename)
            os.makedirs(target_output_dir, exist_ok=True)

            if os.path.isfile(file_path):
                make_index(
                    file_path,
                    target_output_dir,
                    M=M,
                    ef_construction=ef_construction,
                    threads_num=threads_num,
                    brutforce=brutforce,
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
        )
    elif args.input_dir:
        make_indexes(
            args.input_dir,
            args.output_dir,
            M=M,
            ef_construction=ef,
            threads_num=thr_num,
        )


if __name__ == "__main__":
    main()
