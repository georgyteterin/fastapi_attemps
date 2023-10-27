import requests
import shutil
import gzip
import os
import glob


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
            file_out.close()
        file_in.close()


def check_dir(dir_name):
    if os.path.isdir(r"archive"):
        if os.path.isdir(r"archive/" + dir_name):
            pass
        else:
            os.mkdir(r"archive/" + dir_name)
    else:
        os.mkdir(r"archive")
        os.mkdir(r"archive/" + dir_name)


def check_file(file_name):
    if os.path.isdir(r"archive"):
        if os.path.isfile(file_name):
            pass
        else:
            with open(file_name, 'w') as f:
                f.close()
    else:
        os.mkdir(r"archive")
        with open(file_name, 'w') as f:
            f.close()


def last_modified_file(folder):
    result = None
    date = None
    for name in glob.iglob(folder + "/*"):
        if os.path.isfile(name):
            if not result:
                result = name
                date = os.path.getmtime(name)
            else:
                date2 = os.path.getmtime(name)
                if date2 > date:
                    result = name
                    date = date2

    result = result[result.rfind(os.sep) + 1:]
    return result
