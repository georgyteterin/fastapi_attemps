import requests
import shutil
import gzip


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


def dearch(archive_name, local_filename):
    with gzip.open(archive_name, 'rb') as file_in:
        with open(local_filename, 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)

