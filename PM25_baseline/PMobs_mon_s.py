# from PM ioda to month site file

import os

from math import cos, sin, asin, sqrt
import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from netCDF4 import Dataset

import random
import calendar
import glob
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, asin, sqrt
import pandas as pd
from datetime import datetime
from netCDF4 import Dataset
import netCDF4 as nc
from numpy import mean, sqrt, square, median

import glob
import warnings
warnings.filterwarnings('ignore')

###########
mon='07'
path_output = 'PMbaseline'
print('Scanning Month '+mon+'...')
#############
def tic():
    #Homemade version of matlab tic and toc functions
    import time
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    import time
    if 'startTime_for_tictoc' in globals():
        print ("Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds.")
    else:
        print ("Toc: start time not set")

######### Input loading
# sum all sites from all files for the month
tic()

# read all in and construct a station list, 1705 sites in total from 2021-2024, Jul and Sept
marker=0

filelistall=glob.glob('PMIODA/airnowobs/airnow-20??'+mon+'*')
filelistall.sort()


for f in filelistall:
    ds = Dataset(f)
    #print(len(ds['MetaData']['stationIdentification']))
    if marker==0:
        site_id_aqsioda = ds['MetaData']['stationIdentification'][:].tolist()
        site_lat_aqsioda = ds['MetaData']['latitude'][:].tolist()
        site_lon_aqsioda = ds['MetaData']['longitude'][:].tolist()
        
    else:
        site=ds['MetaData']['stationIdentification'][:].tolist()
        for s in range(len(site)):
            if site[s] not in site_id_aqsioda:
                site_id_aqsioda.append(site[s])
                site_lat_aqsioda.append(ds['MetaData']['latitude'][s])
                site_lon_aqsioda.append(ds['MetaData']['longitude'][s])
    ds.close()
    marker=1
    #print(len(site_id_aqsioda))
toc() # about 30s
print('Total sites: ' +str(len(site_lon_aqsioda)))
print('Total files scanned: ' +str(len(filelistall)))

# save
site=pd.DataFrame(columns=['siteid','lat','lon'],index=range(0,len(site_lon_aqsioda)))
site.siteid=site_id_aqsioda
site.lat=site_lat_aqsioda
site.lon=site_lon_aqsioda
site.to_csv(path_output+'/PMIODA_site_mon'+mon+'.csv')

print('Saved to '+path_output+'/PMIODA_site_mon'+mon+'.csv')
print()