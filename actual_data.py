import glob
import os
import time
import math


def get_actual_info(g_n_all):
    if g_n_all == "n" or g_n_all == "g":
        list_of_files = glob.glob(('archive/dl_daily/*.23'+g_n_all).replace("/", os.sep))
        latest_file = max(list_of_files, key=os.path.getctime)
        proper_name = latest_file.split(os.sep)[2]
        size_kb = str(math.ceil(os.path.getsize(latest_file)/1024)) + 'Kb'
        update_time = os.path.getmtime(latest_file)
        modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(update_time))
        response = ("Name: " + proper_name + ';' + "Gnss: " + proper_name[-1] + ';' + "Size: " + size_kb + ';' +
                    "Last Update DateTime: " + modificationTime + ';')
        # print(response)
        return response
    else:
        return False


def get_actual_highrate_filepath(gnss):
    gnss_type = {
        "n": "gps",
        "g": "glo",
        "l": "gal",
        "f": "bds",
    }
    filepath = ""
    files_folder = os.path.join("archive", "dl_highrate", gnss_type[gnss])
    if os.path.exists(files_folder):
        # find the last file
        list_of_files = [os.path.join(files_folder, f) for f in os.listdir(files_folder) if os.path.isfile(os.path.join(files_folder, f))]
        latest_file = max(list_of_files, key=os.path.getctime)
        name = os.path.basename(latest_file)
        filepath = os.path.join(files_folder, name)
        return filepath
    else:
        return False



