import os
from datetime import datetime
from bs4 import BeautifulSoup
from libra import SessionWithHeaderRedirection as redirectionClass
from libra import dearch, check_dir, check_file
from rocketry import Rocketry
from rocketry.conds import every
import logging.config
from urllib.parse import urljoin
from rinex_merger import RinexMerger

logger = logging.getLogger("monitoring")

app = Rocketry()

USERNAME = "rokja"
PASSWORD = "Par0lephemers!"
prev_glo = ''
prev_nav = ''

current = datetime.now()
current_day = f"{datetime.today().date():%j}"

g_name = 'brdc' + current_day + '0.23g.gz'
n_name = 'brdc' + current_day + '0.23n.gz'
log_name = os.path.join("archive", "rinex_logs", "rinex_log.txt")


def get_data():
    url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + str(datetime.today().year) + "/brdc/")

    session = redirectionClass(USERNAME, PASSWORD)

    response = session.get(url, stream=True)

    soup = BeautifulSoup(response.text, "html.parser")

    fileinfos = list(soup.find_all("span", "fileInfo"))
    del fileinfos[0:len(fileinfos) - 2]
    data = []
    for fileinfo in fileinfos:
        data.append(fileinfo.string)

    filenames = list(soup.find_all("a", "archiveItemText"))
    del filenames[0:len(filenames) - 2]
    name = []
    for filename in filenames:
        name.append(filename.string)

    if n_name and g_name in name:
        nav_ind = name.index(n_name)
        glo_ind = name.index(g_name)

        accord = {
            name[nav_ind]: data[nav_ind],
            name[glo_ind]: data[glo_ind]
        }
    else:
        accord = {}
        # print('oops')

    return accord


def get_file(name_of_file):
    url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + str(datetime.today().year) + "/brdc/"
           + name_of_file)
    # print(url)

    session = redirectionClass(USERNAME, PASSWORD)
    filename = url[url.rfind('/') + 1:]

    check_dir("dl_daily")

    try:
        response = session.get(url, stream=True)
        # print(response.status_code)
        response.raise_for_status()
        filename = os.path.join("archive", "dl_daily", filename)
        with open(filename, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                fd.write(chunk)
            fd.close()

        local_filename = filename.removesuffix('.gz')
        dearch(filename, local_filename)
        os.remove(filename)
        return response.status_code
    # except requests.exceptions.HTTPError as e:
    #     print(e)
    except:
        return 404




@app.task(every('300 seconds'))
def do_things():
    check = get_data()

    def compare(filename):
        if get_file(filename) == 200:
            check_dir("rinex_logs")
            check_file(log_name)
            with open(log_name) as f:
                if check.get(filename) in f.read():
                    f.close()
                    # print("no changes")
                    logger.info("no changes")
                else:
                    get_file(filename)
                    with open(log_name, 'a') as r:
                        r.write(datetime.today().strftime("%d-%m-%Y") + "    " + datetime.now().strftime("%H:%M:%S") +
                                "    " + filename + "   " + check.get(filename) + "\n")
                        r.close()
                    # print("got new data")
                    logger.info("got new data: " + filename.removesuffix('.gz'))
        else:
            # return 500
            # print('someting went wrong while downloading')
            logger.info("something went wrong while downloading")

    if os.path.isfile(r"rinex_log.txt"):
        compare(n_name)
        compare(g_name)
    else:
        with open(r"rinex_log.txt", "w") as p:
            p.close()
        compare(n_name)
        compare(g_name)


@app.task(every('600 seconds'))
def do_custom():
    # get_and_merge_highrate_files
    gnss_postfix = {"gps": "n", "glo": "g", "gal": "l", "bds": "f"}
    gnss_abbrev  = {"gps": "GN", "glo": "RN", "gal": "EN", "bds": "CN"}

    # Создаем папку для сохранения файлов, если её нет
    download_folder = os.path.join("archive", "tmp_files")
    os.makedirs(download_folder, exist_ok=True)

    # Создаем объект RinexMerger
    res_rinex_folder = os.path.join("archive", "dl_highrate")
    os.makedirs(res_rinex_folder, exist_ok=True)
    rinex_merger = RinexMerger(download_folder, res_rinex_folder)

    url = ""

    # Цикл по ГНСС
    for gnss in ["gps", "glo"]:    # ["gps", "glo", "gal", "bds"]
        # До обработки по всем системам почистить папку с кучей файлов
        all_files = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]
        gnss_files = [f for f in all_files if gnss_abbrev[gnss].lower() + ".rnx" in f.lower()]

        for file_path in gnss_files:
            try:
                os.remove(os.path.join(download_folder, file_path))
                # print(f"Файл {file_path} удален успешно.")
            except Exception as e:
                # print(f"Ошибка при удалении файла {file_path}: {e}")
                logger.error(f"Ошибка при удалении файла {file_path}: {e}")
        logger.info(f"Downloaded {gnss.upper()} folder is ready (files are cleaned).")

        # Формирование ссылки на скачивание файлов
        url = f"https://cddis.nasa.gov/archive/gnss/data/highrate/{datetime.now().year:>04d}/{datetime.now().timetuple().tm_yday:>03d}/{(datetime.now().year-2000):>02d}{gnss_postfix[gnss]:s}/"
        # url = f"https://cddis.nasa.gov/archive/gnss/data/highrate/{datetime.now().year:>04d}/{datetime.now().timetuple().tm_yday - 1:>03d}/{(datetime.now().year-2000):>02d}{gnss_postfix[gnss]:s}/"

        # Получить ссылку на самую последнюю папку (час) за сегодняшний день
        session = redirectionClass(USERNAME, PASSWORD)
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"})

        response = session.get(url, stream=True)
        soup = BeautifulSoup(response.text, "html.parser")
        hour_folders = list(soup.find_all("a", "archiveDirText"))
        url += hour_folders[-1].string + "/"

        file_mask_to_download = f"{gnss_abbrev[gnss]}.rnx.gz"

        # Получаем HTML-страницу
        response = session.get(url, stream=True)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем все ссылки на файлы с заданным расширением
        links = soup.find_all("a", "archiveItemText", href=True)
        links = [link for link in links if file_mask_to_download in link.string]

        # Если в папке недостаточно файлов, то пойти в папку за предыдущий час
        if len(links) < 10:
            if hour_folders[-2].string == "00":
                # Папка предыдущий день и 23 час
                url = f"https://cddis.nasa.gov/archive/gnss/data/highrate/{datetime.now().year:>04d}/{(datetime.now().timetuple().tm_yday - 1):>03d}/{(datetime.now().year - 2000):>02d}{gnss_postfix[gnss]:s}/23"
            else:
                url = f"https://cddis.nasa.gov/archive/gnss/data/highrate/{datetime.now().year:>04d}/{datetime.now().timetuple().tm_yday:>03d}/{(datetime.now().year - 2000):>02d}{gnss_postfix[gnss]:s}/"
                url += hour_folders[-2].string + "/"

        number_of_files_limit = 0
        # Скачиваем файлы из папки cddis
        logger.info(f"Downloading {gnss.upper()} files from {url}.")
        for link in links:
            # Формируется ссылка на скачивание отдельного файла
            file_url = urljoin(url, link['href']).strip()
            file_name = os.path.join(download_folder, os.path.basename(file_url))
            # print(f"Скачиваем: {file_url}")
            response = session.get(file_url, stream=True)
            with open(file_name, 'wb') as file:
                file.write(response.content)
            # Разархивация файла
            dearh_file_name = file_name.removesuffix(".gz")
            dearch(file_name, dearh_file_name)
            os.remove(file_name)

            # Скачивание number_of_files_limit файлов на систему
            # TODO: удалить, это для дебага
            number_of_files_limit += 1
            if number_of_files_limit == 50:
                break
        logger.info(f"Downloading {gnss.upper()} files has finished.")
        session.close()

        # Обработка ринекс файлов для gnss
        logger.info(f"Merging files has started")
        rinex_merger.merge_files(gnss)
        logger.info(f"Merging files has finished")

        # # После обработки по всем системам почистить папку с кучей файлов
        # all_files = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]
        # gnss_files = [f for f in all_files if gnss_abbrev[gnss].lower() + ".rnx" in f.lower()]
        #
        # for file_path in gnss_files:
        #     try:
        #         os.remove(os.path.join(download_folder, file_path))
        #         # print(f"Файл {file_path} удален успешно.")
        #     except Exception as e:
        #         # print(f"Ошибка при удалении файла {file_path}: {e}")
        #         logger.error(f"Ошибка при удалении файла {file_path}: {e}")
        # logger.info(f"Downloaded {gnss.upper()} files are cleaned.")

    # <---Окончание цикла по ГНСС




if __name__ == '__main__':
    app.run()
