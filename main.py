from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn



app = FastAPI(
    title = "I AM TRYING"
)

# ЭТО ЧТОБЫ ПРОВЕРИТЬ ФОРМИРОВАНИЕ ДАТЫ ДЛЯ СКАЧИВАНИЯ ФАЙЛА ПО ЗАПРОСУ http://localhost:8000/filename/213-23-n
# (естественно и дату и год и n/g можно менят, это из примера из воровского документа по эфемеридам))
@app.get("/filename/{DDD}-{YY}-{n_or_g}")
def filename(DDD: int, YY: int, n_or_g):
    filename = "brdc"+DDD+"0."+YY+n_or_g
    return {"зесь должно быть скачивание файла": filename}


# СКАЧАТЬ ФАЙЛ КОТОРЫЙ ЛЕЖИТ ГДЕ-ТО В ПАПКЕ ПО ЗАПРОСУ http://localhost:8000/download_file
# у меня катинка лежит в той же папке, что и проект, так что адрес короткий
@app.get("/download_file")
def download_file():
  return FileResponse(path='cute cat.jpg', filename='картинка кота.jpeg')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)