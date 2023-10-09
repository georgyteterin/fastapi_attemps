from datetime import datetime
from bs4 import BeautifulSoup
from libra import SessionWithHeaderRedirection as redirectionClass
from libra import dearch
from rocketry import Rocketry
from rocketry.conds import every

app = Rocketry()


USERNAME = "rokja"
PASSWORD = "Par0lephemers!"
PREV_GLO = ''
PREV_NAV = ''


g_name = 'brdc' + f"{datetime.today().date():%j}" + '0.23g.gz'
n_name = 'brdc' + f"{datetime.today().date():%j}" + '0.23n.gz'



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

    try:
        response = session.get(url, stream=True)

        print(response.status_code)
        response.raise_for_status()
        with open(filename, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                fd.write(chunk)

        local_filename = r"archive\\" + filename.removesuffix('.gz')

        dearch(filename, local_filename)
        return response.status_code
    # except requests.exceptions.HTTPError as e:
    #     print(e)
    except:
        # print('url does not exist')
        return 404


@app.task(every('300 seconds'))
def do_things():

    check = get_data()

    def compare(prev, filename):
        if get_file(filename) == 200:
            if prev == check.get(filename):
                print("no changes")
            else:
                get_file(filename)
                with open('log.txt', 'a') as f:
                    f.write(datetime.now().strftime("%H:%M:%S") + "    " + filename + "   " + check.get(filename) + "\n")
                    f.close()
                # print('logged')
                prev = check.get(filename)
            return prev

    prev_nav = compare(PREV_NAV, n_name)
    prev_glo = compare(PREV_GLO, g_name)

# time.sleep(20)

#
if __name__ == '__main__':
    app.run()