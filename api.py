import math
import os.path
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
from libra import SessionWithHeaderRedirection as redirectionClass
from libra import dearch, check_dir
from monitoring import app as app_rocketry
from datetime import datetime, time
from actual_data import get_actual_info, get_actual_highrate_filepath
import glob
import time
import logging.config





app = FastAPI(
    title="downloading ephemeris",
    version="0.1"
)

session = app_rocketry.session

logger = logging.getLogger("api")


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
    filename = os.path.join("archive/dl_year".replace("/", os.sep), url[url.rfind('/') + 1:])
    local_filename = filename.removesuffix('.gz')

    if os.path.exists(local_filename):
        logger.info(f"sending file '{local_filename[local_filename.rfind(os.sep) + 1:]}' to client")
        return FileResponse(path=local_filename, filename=local_filename)
    else:
        response = session.get(url, stream=True)

        if response.status_code == 200:
            check_dir("dl_year")

            logger.info(f"downloading file '{filename[filename.rfind(os.sep) + 1:]}'")
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fd.write(chunk)

            logger.info(f"unzipping '{filename[filename.rfind(os.sep) + 1:]}' to '{local_filename[local_filename.rfind(os.sep) + 1:]}'")
            dearch(filename, local_filename)
            os.remove(filename)

            logger.info(f"sending file '{local_filename[local_filename.rfind(os.sep) + 1:]}' to client")
            return FileResponse(path=local_filename, filename=local_filename)
        elif response.status_code == 404:
            logger.info(f"there is no file {filename[filename.rfind(os.sep) + 1:]} on CDDIS")
            return f"there is no file {filename[filename.rfind(os.sep) + 1:]} on CDDIS"
        else:
            logger.info(f"there are troubles with getting {filename[filename.rfind(os.sep) + 1:]}, "
                        f"response code {response.status_code}")
            return (f"there are troubles with getting {filename[filename.rfind(os.sep) + 1:]}, "
                    f"response code {response.status_code}")


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
        raise HTTPException(status_code=404, detail="Archive is empty")


@app.get('/actual/{g_n_all}')
def send_actual_info(g_n_all):
    if get_actual_info(g_n_all) is False:
        raise HTTPException(status_code=404)
    else:
        return get_actual_info(g_n_all)


@app.get('/download/last/highrate/{g_n_l_f}')
def send_highrate_file(g_n_l_f):
    gnss_type = {
        "n": "gps",
        "g": "glo",
        "l": "gal",
        "f": "bds",
    }

    if g_n_l_f not in ["n", "g", "l", "f"]:
        raise HTTPException(status_code=404, detail="This GNSS is not supported yet.")
        return

    filepath = get_actual_highrate_filepath(g_n_l_f)
    if filepath:
        name = os.path.basename(filepath)
        if os.path.isfile(filepath):
            return FileResponse(filepath, filename=name)
        else:
            raise HTTPException(status_code=404, detail="Item is not a file")
    else:
        raise HTTPException(status_code=404, detail="Item is not ready or exist")


@app.get('/actual/highrate/{g_n_l_f}')
def send_actual_highrate_info(g_n_l_f):
    if g_n_l_f not in ["n", "g", "l", "f"]:
        raise HTTPException(status_code=404, detail="This GNSS is not supported yet.")

    filepath = get_actual_highrate_filepath(g_n_l_f)
    if filepath:
        name = os.path.basename(filepath)
        size_kb = str(math.ceil(os.path.getsize(filepath) / 1024)) + 'Kb'
        update_time = os.path.getmtime(filepath)
        modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(update_time))
        response = ("Name: " + name + ';' + "Gnss: " + g_n_l_f + ';' + "Size: " + size_kb + ';' +
                    "Last Update DateTime: " + modificationTime + ';')
        return response
    else:
        raise HTTPException(status_code=404, detail="Item not ready or exist")




# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000)
