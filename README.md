# fastapi_attemps

запросы и что они делают:
main.py:
  1) http://localhost:8000/download/{year}/{DDD}-{n_or_g} - генеирует ссылку для скачивания, скачивает архив, распаковывает и посылает содержимое как ответ
  2) http://localhost:8000/download/last/{n_or_g} - из директории archive качает актуальный файл, если сегодняшнего файла еще нет, ачает последний вчерашний, если такового тоже нет возвращает false

в файле monitoring.py описан механизм мониторинга сайта на предмет новых файлов, обновления архива
в файле api.py описаны запросы
