#!/bin/sh

# Очистка предыдущих результатов


rm -f *.csv

#!/bin/sh

# Функция для вывода справки
print_help() {
  echo "Использование: $0 [OPTIONS]"
  echo ""
  echo "Обязательные параметры:"
  echo "  --dsc_file FILE         Путь к файлу дескрипторов (обязательный параметр)."
  echo ""
  echo "Параметры для этапа создания индекса:"
  echo "  --M VALUE               Параметр M для создания индекса."
  echo "  --ef_constr VALUE       Параметр ef_construction для создания индекса."
  echo "  --idx_thr_num VALUE     Параметр thr_num для создания индекса."
  echo ""
  echo "Параметры для этапа поиска:"
  echo "  --ef VALUE              Параметр ef для поиска."
  echo "  --search_thr_num VALUE         Параметр search_thr_num для поиска."
  echo ""
  echo "Флаги для пропуска этапов:"
  echo "  --skip_index            Пропустить этап создания индекса."
  echo "  --skip_search           Пропустить этап поиска."
  echo ""
  echo "Примечание:"
  echo "  Если заданы все параметры для индексации (--M, --ef_constr, --idx_thr_num),"
  echo "    запускается make_index.py с указанными значениями."
  echo "  Если параметры для индексации не заданы, используется combinations_make_index.sh."
  echo ""
  echo "  Если заданы оба параметра для поиска (--ef и --search_thr_num),"
  echo "    запускается search.py с указанными значениями."
  echo "  Если параметры для поиска не заданы, используется combinations_search.sh."
  echo ""
  echo "  Если ни один из параметров для поиска не указан, то выполняется комбинация по умолчанию."
  echo ""
  exit 0
}

# Обработка параметра помощи
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  print_help
fi

# Инициализация переменных
dsc_file=""
M=""
ef_constr=""
idx_thr_num=""
ef=""
search_thr=""
skip_index=0
skip_search=0

# Обработка аргументов командной строки
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dsc_file)
      dsc_file="$2"
      shift 2
      ;;
    --M)
      M="$2"
      shift 2
      ;;
    --ef_constr)
      ef_constr="$2"
      shift 2
      ;;
    --idx_thr_num)
      idx_thr_num="$2"
      shift 2
      ;;
    --ef)
      ef="$2"
      shift 2
      ;;
    --search_thr_num)
      search_thr="$2"
      shift 2
      ;;
    --skip_index)
      skip_index=1
      shift 1
      ;;
    --skip_search)
      skip_search=1
      shift 1
      ;;
    *)
      echo "Неизвестный параметр: $1"
      exit 1
      ;;
  esac
done

# Проверка обязательного параметра dsc_file
if [ "$skip_index" -ne 1 ] || [ "$skip_search" -ne 1 ]; then
  if [ -z "$dsc_file" ]; then
    echo "Ошибка: необходимо указать --dsc_file"
    exit 1
  fi
fi


# Извлечение базового имени файла и его директории
dsc_base=$(basename "$dsc_file")
dsc_dir=$(dirname "$dsc_file")

# Определение суффикса для idx-файла: если заданы M, ef_constr и idx_thr_num, используем их,
# иначе применяем значения по умолчанию: 12, 110, 12.
if [ -n "$M" ] && [ -n "$ef_constr" ] && [ -n "$idx_thr_num" ]; then
  suffix="${M}_${ef_constr}_${idx_thr_num}"
else
  suffix="12_110_12"
fi

idx_file_path="work-dir/${dsc_base}/*_${suffix}.idx"

# Если параметры не будут заданы, то пройдется по циклу, фиксируя в логах время и параметры
# Указание параметров укажет лишь на точечное создание и тестирование индекса. 
# После циклов будет выбран фиксированный индекс, для тестирования поиска
if [ "$skip_index" -eq 0 ]; then
  if [ -n "$M" ] && [ -n "$ef_constr" ] && [ -n "$idx_thr_num" ]; then
    echo "Выполнение make_index.py с параметрами: M=$M, ef_construction=$ef_constr, thr_num=$idx_thr_num"
    poetry run python3 make_index.py --M "$M" --ef_construction "$ef_constr" --thr_num "$idx_thr_num" --input_file "$dsc_file"
  else
    # rm -rf work-dir/*
    echo "Выполнение combinations_make_index.sh с --input_file $dsc_file"
    ./tools/combinations_make_index.sh --input_file "$dsc_file"
  fi
else
  echo "Пропуск этапа создания индекса (--skip_index)"
fi

# Если параметры не будут заданы, то пройдется по циклу, фиксируя в логах recall, время и параметры

if [ "$skip_search" -eq 0 ]; then
  rm -r search_results/* 
  # Если заданы оба параметра для поиска, запускаем search.py
  if [ -n "$ef" ] && [ -n "$search_thr" ]; then
    echo "Выполнение search.py с параметрами: ef=$ef, thr_num=$search_thr"
    poetry run python3 search.py --idx_file $idx_file_path --dsc_dir $dsc_dir --ef "$ef" --thr_num "$search_thr"
  else
    # rm -rf search_results/*
    # Иначе формируем команду для combinations_search.sh
    ./tools/combinations_search.sh --idx_file $idx_file_path --dsc_dir $dsc_dir
  fi
else
  echo "Пропуск этапа поиска (--skip_search)"
fi

./tools/prepare_csv.sh
poetry run python3 analize.py --csv ./total_search.csv -x ef -y num_threads --smooth
