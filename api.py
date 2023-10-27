import os.path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
from libra import SessionWithHeaderRedirection as redirectionClass
from libra import dearch, check_dir
from monitoring import app as app_rocketry
from monitoring import do_things as download
from datetime import datetime, timedelta
from actual_data import get_actual_info


app = FastAPI(
    title="downloading ephemeris",
    version="0.1"
)

session = app_rocketry.session


USERNAME = "rokja"
PASSWORD = "Par0lephemers!"
PREV_GLO = ''
PREV_NAV = ''


g_name = 'brdc' + f"{datetime.today().date():%j}" + '0.23g.gz'
n_name = 'brdc' + f"{datetime.today().date():%j}" + '0.23n.gz'


@app.on_event("startup")
def first_download():
    download()



@app.get('/startMech')
async def mechanism():
    return session.tasks


@app.get('/download/{year}/{DDD}-{n_or_g}')
def get_file(year, DDD, n_or_g):
    url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + year + "/brdc/brdc"
           + DDD + "0." + year[2:] + n_or_g + ".gz")

    session = redirectionClass(USERNAME, PASSWORD)
    filename = os.path.join("archive/dl_year", url[url.rfind('/') + 1:])


    try:

        response = session.get(url, stream=True)
        # print(response.status_code)
        response.raise_for_status()
        check_dir("dl_year")

        with open(filename, 'wb') as fd:

            for chunk in response.iter_content(chunk_size=1024 * 1024):
                fd.write(chunk)

    except requests.exceptions.HTTPError as e:
        print(e)

    local_filename = filename.removesuffix('.gz')
    dearch(filename, local_filename)
    os.remove(filename)

    return FileResponse(path=local_filename, filename=local_filename)


@app.get('/download/last/{n_or_g}')
def send_file(n_or_g: str):

    path = os.path.join("archive", "dl_daily", 'brdc' + f"{datetime.today().date():%j}" + '0.23'+n_or_g)
    yesterday = datetime.today() - timedelta(days=1)
    yesterday_path = os.path.join("archive", "dl_daily", 'brdc' + f"{yesterday.date():%j}" + '0.23'+n_or_g)
    if os.path.isfile(path):
        return FileResponse(path, filename='brdc' + f"{datetime.today().date():%j}" + '0.23'+n_or_g)
    elif os.path.isfile(yesterday_path):
        return FileResponse(yesterday_path, filename='brdc' + f"{yesterday.date():%j}" + '0.23' + n_or_g)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get('/actual/{g_n_all}')
def send_actual_info(g_n_all):
    if get_actual_info(g_n_all) is False:
        raise HTTPException(status_code=404)
    else:
        return get_actual_info(g_n_all)

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000)
