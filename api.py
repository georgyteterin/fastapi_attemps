import os.path
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
from libra import SessionWithHeaderRedirection as redirectionClass
from libra import dearch, check_dir
from monitoring import app as app_rocketry
from datetime import datetime
from actual_data import get_actual_info
import glob





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


@app.get('/startMech')
async def mechanism():
    return session.tasks


@app.get('/download/{year}/{DDD}-{n_or_g}')
def get_file(year, DDD: str, n_or_g):
    if len(DDD) < 3:
        if len(DDD) < 2:
            url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + year + "/brdc/brdc"
                   + "00"+DDD + "0." + year[2:] + n_or_g + ".gz")
        else:
            url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + year + "/brdc/brdc"
                   + "0"+DDD + "0." + year[2:] + n_or_g + ".gz")
    else:
        url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + year + "/brdc/brdc"
                + DDD + "0." + year[2:] + n_or_g + ".gz")


    session = redirectionClass(USERNAME, PASSWORD)
    filename = os.path.join("archive/dl_year", url[url.rfind('/') + 1:])
    local_filename = filename.removesuffix('.gz')

    if os.path.exists(local_filename):
        return FileResponse(path=local_filename, filename=local_filename)
    else:
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

        dearch(filename, local_filename)
        os.remove(filename)

        return FileResponse(path=local_filename, filename=local_filename)


@app.get('/download/last/{n_or_g}')
def send_file(n_or_g: str):
    if len(os.listdir('archive/dl_daily/'.replace("/", os.sep))) != 0:
        list_of_files = glob.glob(('archive/dl_daily/*.23' + n_or_g).replace("/", os.sep))
        latest_file = max(list_of_files, key=os.path.getctime)
        name = latest_file.split(os.sep)[2]
        path = os.path.join("archive", "dl_daily", name)
        if os.path.isfile(path):
            return FileResponse(path, filename=name)
        else:
            raise HTTPException(status_code=404, detail="Item not found")
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
