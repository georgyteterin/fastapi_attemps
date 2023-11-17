# fastapi_attemps

запросы и что они делают:
main.py:
  1) http://localhost:8000/download/{year}/{DDD}-{n_or_g} - генеирует ссылку для скачивания, скачивает архив, распаковывает и посылает содержимое как ответ
  2) http://localhost:8000/download/last/{n_or_g} - из директории archive качает актуальный файл, если сегодняшнего файла еще нет, качает последний скаченный, если такового тоже нет возвращает false
  3) http://localhost:8000/actual/{g_n_all} - возвращает данные о последнем файле на сервере (пока только для n и g, для остальных запросов выдаст 404)
  4) http://localhost:8000/download/last/highrate/{g_n_l_f} - из директории '_archive/dl_highrate_' качает актуальный highrate файл на сервере (n - GPS, g - GLONASS, l - Galileo, f - Beidou)
  5) http://localhost:8000/actual/highrate/{g_n_l_f} - возвращает данные о последнем highrate файле на сервере  (n - GPS, g - GLONASS, l - Galileo, f - Beidou)

в файле monitoring.py описан механизм мониторинга сайта на предмет новых файлов, обновления архива
в файле api.py описаны запросы

