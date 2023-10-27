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
        response = ("Name: " + proper_name + '\n' + "Gnss: " + proper_name[-1] + '\n' + "Size: " + size_kb + '\n' +
                    "Last Update DateTime: " + modificationTime)
        # print(response)
        return response
    else:
        return False