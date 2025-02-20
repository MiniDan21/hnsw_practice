#!/bin/bash
# Использование:
#   ./script.sh [output_prefix] [work_dir] [search_dir]
#
#   output_prefix  - префикс для создаваемых CSV файлов (по умолчанию "total")
#   work_dir        - директория с логами для первого файла (по умолчанию "work-dir")
#   search_dir     - директория с логами для второго файла (по умолчанию "search_results")

# rm *.csv

output_prefix="${1:-total}"
work_dir="${2:-work-dir}"
search_dir="${3:-search_results}"

echo "Используем рабочую директорию: $work_dir"
echo "Используем директорию поиска: $search_dir"

echo "input.dsc,M,ef_constr,num_threads,time" > "${output_prefix}_index.csv"
cat ${work_dir}/**/*.log >> "${output_prefix}_index.csv"

echo "input.dsc,test.dsc,M,ef_constr,ef,num_threads,recall,time" > "${output_prefix}_search.csv"
# почему то не работает, но вручную работает
cat ${search_dir}*/**/*.log >> "${output_prefix}_search.csv"
