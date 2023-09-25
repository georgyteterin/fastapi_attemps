from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import uvicorn
import gzip
import shutil


app = FastAPI(
    title="downloading ephemeris",
    version="1"
)

USERNAME = "rokja"
PASSWORD = "Par0lephemers!"

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


@app.get('/download/{year}/{DDD}-{n_or_g}')
def get_file(year: int, DDD, n_or_g):
    url = ("https://cddis.nasa.gov/archive/gnss/data/daily/" + str(year) + "/brdc/brdc"
           + DDD + "0." + str(year % 100) + n_or_g + ".gz")

    session = SessionWithHeaderRedirection(USERNAME, PASSWORD)
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
        local_filename = filename.removesuffix('.gz')
        with gzip.open(archive_name, 'rb') as file_in:
            with open(local_filename, 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
                return local_filename

    our_filename = rasarch(filename)

    return FileResponse(path=our_filename, filename=our_filename)



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
