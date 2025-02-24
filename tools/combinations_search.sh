#!/bin/sh

# Инициализация переменных для аргументов
idx_dir=""
idx_file=""
dsc_dir=""
dsc_file=""
output_dir="./search_results"

# Обработка аргументов командной строки
while [ "$#" -gt 0 ]; do
  case "$1" in
    --idx_dir)
      idx_dir="$2"
      shift 2
      ;;
    --idx_file)
      idx_file="$2"
      shift 2
      ;;
    --dsc_dir)
      dsc_dir="$2"
      shift 2
      ;;
    --dsc_file)
      dsc_file="$2"
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

# Проверка для idx: задать ровно один из параметров --idx_dir или --idx_file
if [ -n "$idx_dir" ] && [ -n "$idx_file" ]; then
    echo "Укажите либо --idx_dir, либо --idx_file, но не оба одновременно."
    exit 1
fi

if [ -z "$idx_dir" ] && [ -z "$idx_file" ]; then
    echo "Укажите один из параметров: --idx_dir или --idx_file."
    exit 1
fi

if [ -n "$dsc_dir" ] && [ -n "$dsc_file" ]; then
    echo "Укажите либо --dsc_dir, либо --dsc_file, но не оба одновременно."
    exit 1
fi

if [ -z "$dsc_dir" ] && [ -z "$dsc_file" ]; then
    echo "Укажите один из параметров: --dsc_dir или --dsc_file."
    exit 1
fi

ef_values="100 200 300"    # Пример диапазона для ef
thr_num_values="1 2 3"     # Пример диапазона для thr_num

for ef in $(seq 10 100 310); do
  for thr in $(seq 4 4 "$(nproc --all)"); do
    echo "Запуск: ef=$ef, thr_num=$thr"
    
    if [ -n "$idx_dir" ]; then
        idx_arg="--idx_dir $idx_dir"
    else
        idx_arg="--idx_file $idx_file"
    fi

    if [ -n "$dsc_dir" ]; then
        dsc_arg="--dsc_dir $dsc_dir"
    else
        dsc_arg="--dsc_file $dsc_file"
    fi

    poetry run python3 ./search.py --ef "$ef" --thr_num "$thr" $idx_arg $dsc_arg --output_dir "$output_dir" -a
  done
done
