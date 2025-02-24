#!/bin/sh

# Инициализация переменных для аргументов
input_file=""
input_dir=""
output_dir="./work-dir"

# Обработка аргументов командной строки
while [ "$#" -gt 0 ]; do
  case "$1" in
    --input_file)
      input_file="$2"
      shift 2
      ;;
    --input_dir)
      input_dir="$2"
      shift 2
      ;;
    --output_dir)
      output_dir="$2"
      shift 2
      ;;
    *)
      echo "Неизвестный параметр: $1"
      exit 1
      ;;
  esac
done

if [ -n "$input_file" ] && [ -n "$input_dir" ]; then
  echo "Укажите либо --input_file, либо --input_dir."
  exit 1
fi

if [ -z "$input_file" ] && [ -z "$input_dir" ]; then
  echo "Укажите --input_file или --input_dir."
  exit 1
fi

# Заданные диапазоны параметров
M_values="4 8 16"                     # Пример диапазона для M
ef_construction_values="100 200 300"    # Пример диапазона для ef_construction
thr_num_values="1 2 3"                  # Пример диапазона для thr_num

# Запуск цикла по всем комбинациям
for M in $(seq 2 25 52); do
  for ef in $(seq 10 100 310); do
    for thr in $(seq 4 4 $(nproc --all)); do
      echo "Запуск: M=$M, ef_construction=$ef, thr_num=$thr"
      
      # Формирование команды с обязательным аргументом --output_dir
      # Выбор: если задан input_file, то используем его, иначе input_dir
      if [ -n "$input_file" ]; then
        poetry run python3 make_index.py --M "$M" --ef_construction "$ef" --thr_num "$thr" --input_file "$input_file" --output_dir "$output_dir" -a
      else
        poetry run python3 make_index.py --M "$M" --ef_construction "$ef" --thr_num "$thr" --input_dir "$input_dir" --output_dir "$output_dir" -a
      fi
    done
  done
done
