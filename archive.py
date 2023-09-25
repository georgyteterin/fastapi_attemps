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



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
