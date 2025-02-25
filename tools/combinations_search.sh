#!/bin/sh

# Инициализация переменных для аргументов
idx_dir=""
idx_file=""
dsc_dir=""
dsc_file=""
output_dir="./search_results"
ef_arg=""
thr_arg=""

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
    --ef)
      ef_arg="$2"
      shift 2
      ;;
    --thr_num)
      thr_arg="$2"
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

# Проверка для dsc: задать ровно один из параметров --dsc_dir или --dsc_file
if [ -n "$dsc_dir" ] && [ -n "$dsc_file" ]; then
    echo "Укажите либо --dsc_dir, либо --dsc_file, но не оба одновременно."
    exit 1
fi

if [ -z "$dsc_dir" ] && [ -z "$dsc_file" ]; then
    echo "Укажите один из параметров: --dsc_dir или --dsc_file."
    exit 1
fi

# Формирование аргументов для вызова search.py
if [ -n "$idx_dir" ]; then
    idx_cmd="--idx_dir $idx_dir"
else
    idx_cmd="--idx_file $idx_file"
fi

if [ -n "$dsc_dir" ]; then
    dsc_cmd="--dsc_dir $dsc_dir"
else
    dsc_cmd="--dsc_file $dsc_file"
fi

# Если ef или thr_num не заданы, используем цикл по диапазонам.
# Пример диапазона для ef: от 10 до 210 с шагом 100
for ef in $(seq 10 100 210); do
  # Вычисляем диапазон для thr_num: от nproc/2 до nproc
  nproc_all=$(nproc --all)
  start=$(echo "$nproc_all / 2" | bc)
  step=$(echo "$nproc_all / 2" | bc)
  for thr in $(seq "$start" "$step" "$nproc_all"); do
    echo "Запуск: ef=$ef, thr_num=$thr"
    poetry run python3 ./search.py --ef "$ef" --thr_num "$thr" $idx_cmd $dsc_cmd --output_dir "$output_dir"
  done
done
