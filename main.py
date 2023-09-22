from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import uvicorn
import gzip
import shutil


app = FastAPI(
    title="I AM TRYING"
)


# ЭТО ЧТОБЫ ПРОВЕРИТЬ ФОРМИРОВАНИЕ ДАТЫ ДЛЯ СКАЧИВАНИЯ ФАЙЛА ПО ЗАПРОСУ http://localhost:8000/filename/213-23-n
# (естественно и дату и год и n/g можно менят, это из примера из воровского документа по эфемеридам))
@app.get("/filename/{DDD}-{YY}-{n_or_g}")
def filename(DDD, YY, n_or_g):
    filename = "brdc" + DDD + "0." + YY + n_or_g + ".txt"
    return {"зесь должно быть скачивание файла": filename}


# СКАЧАТЬ ФАЙЛ КОТОРЫЙ ЛЕЖИТ ГДЕ-ТО В ПАПКЕ ПО ЗАПРОСУ http://localhost:8000/download_file
# у меня катинка лежит в той же папке, что и проект, так что адрес короткий
@app.get("/download_file")
def download_file():
    return FileResponse(path='cute cat.jpg', filename='картинка кота.jpeg')


@app.get("/download_file/{DDD}-{YY}-{n_or_g}")
def download_file_by_name(DDD, YY, n_or_g):
    filename = "brdc" + DDD + "0." + YY + n_or_g + ".jpg"
    return FileResponse(path=filename, filename=filename)


@app.get("/link/{num}")
def download_by_link(num: int):
    if num == 1:
        url = 'https://rockweek.ru/wp-content/uploads/2016/09/kiss_44.jpg'
    elif num == 2:
        url = 'https://wallpapers.com/images/hd/cute-cats-pictures-ofp9qyt72qck6jqg.jpg'
    elif num == 3:
        url = 'https://schoharierecovery.org/wp-content/uploads/2020/09/2-2.jpg'
    # elif num == 4:
    #     url = 'https://cddis.nasa.gov/archive/gnss/data/daily/2023/brdc/brdc2120.23n.gz'
    else:
        return {"ссылка пока не добавлена"}
    # url = ['https://rockweek.ru/wp-content/uploads/2016/09/kiss_44.jpg',
    #        'https://wallpapers.com/images/hd/cute-cats-pictures-ofp9qyt72qck6jqg.jpg',
    #        'https://schoharierecovery.org/wp-content/uploads/2020/09/2-2.jpg'
    #        ]
    # r = requests.get(url[num - 1])
    r = requests.get(url)
    # with open(r'C:\Users\гоша\Documents\my_photos\picture.jpg', 'wb') as f:
    with open(r'picture.jpg', 'wb') as f:
        f.write(r.content)
    # path = r'C:\Users\гоша\Documents\my_photos\picture.jpg'
    path = r'picture.jpg'
    filename = 'picture.jpg'
    return FileResponse(path=path, filename=filename)


@app.get('/download_ephemers')
def get_file():
    class SessionWithHeaderRedirection(requests.Session):

        AUTH_HOST = 'urs.earthdata.nasa.gov'

        def __init__(self, username, password):

            super().__init__()

            self.auth = (username, password)

        def rebuild_auth(self, prepared_request, response):
            headers = prepared_request.headers
            url = prepared_request.url

            if 'Authorization' in headers:

                original_parsed = requests.utils.urlparse(response.request.url)

                redirect_parsed = requests.utils.urlparse(url)

                if ((original_parsed.hostname != redirect_parsed.hostname) and
                        redirect_parsed.hostname != self.AUTH_HOST and
                        original_parsed.hostname != self.AUTH_HOST):
                    del headers['Authorization']
            return

    username = "rokja"
    password = "Par0lephemers!"

    session = SessionWithHeaderRedirection(username, password)

    url = "https://cddis.nasa.gov/archive/gnss/data/daily/2023/brdc/brdc2050.23n.gz"

    filename = url[url.rfind('/') + 1:]

    try:

        response = session.get(url, stream=True)
        print(response.status_code)
        response.raise_for_status()
        with open(filename, 'wb') as fd:

            for chunk in response.iter_content(chunk_size=1024 * 1024):
                fd.write(chunk)

    except requests.exceptions.HTTPError as e:
        print(e)

    def rasarch(archive_name):
        local_filename = archive_name.removesuffix('.gz')
        with gzip.open(archive_name, 'rb') as file_in:
            with open(local_filename, 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
                return(local_filename)

    our_filename = rasarch(filename)
    return FileResponse(path=our_filename, filename=our_filename)



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
