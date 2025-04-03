#!/usr/bin/env python3


# convert ioda obs into monthly nc file , by Huiying

import numpy as np
import pandas as pd
from math import cos, sin
from netCDF4 import Dataset
from datetime import datetime, timedelta
import os, zipfile
import glob
from calendar import monthrange
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# ###### unzip downloaded files (aqs annual) ######
# dir_name = '.'
# extension = ".zip"
# os.chdir(dir_name)  # change directory from working dir to dir with files
# 
# for item in os.listdir(dir_name):  # loop through items in dir
#     if item.endswith(extension):  # check for ".zip" extension
#         file_name = os.path.abspath(item)  # get full path of files
#         zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
#         zip_ref.extractall(dir_name)  # extract file to dir
#         zip_ref.close()  # close file
# =============================================================================

## settings
mon='07'
path_output = 'PMobs'

## functions
def generate_hourly_datetime_index(year, month):
  start_date = pd.Timestamp(year, month, 1)
  end_date = pd.Timestamp(year, month, 1) + pd.DateOffset(months=1) - pd.Timedelta(hours=1)
  return pd.date_range(start=start_date, end=end_date, freq='H')
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
siteinfo=pd.read_csv('PMbaseline/PMIODA_site_mon'+mon+'.csv')
site_id_aqsioda=siteinfo['siteid'].tolist()

for yrid in range(2015,2025):# not include 2025

    yr=str(yrid)
    print('Processing '+yr+'...')
    tic()
    
    hourlist=generate_hourly_datetime_index(yrid,int(mon))

    #####
    dataall=np.zeros([len(hourlist),len(site_id_aqsioda)])
    dataall[:]=np.nan
    
    dataco=np.zeros([len(hourlist),len(site_id_aqsioda)])
    dataco[:]=np.nan
    
    datapm10=np.zeros([len(hourlist),len(site_id_aqsioda)])
    datapm10[:]=np.nan

    
    for h in range(len(hourlist)):
        inpath='PMIODA/airnowobs/airnow-'+hourlist[h].strftime('%Y%m%d%H')+'-blprep-v1.nc'
        if os.path.isfile(inpath):
            with Dataset(inpath,'r') as ds:
                #ds = Dataset(inpath)
                #print(hourlist[h].strftime('%Y%m%d%H'))
                  
                for s in range(len(ds['MetaData']['stationIdentification'][:])):
                    sindex=site_id_aqsioda.index(ds['MetaData']['stationIdentification'][s])
                    dataall[h,sindex]=ds['ObsValue']['particulatematter2p5Surface'][:][s]
                    dataco[h,sindex]=ds['ObsValue']['CarbonmonoxideSurface'][:][s]
                    datapm10[h,sindex]=ds['ObsValue']['particulatematter10Surface'][:][s]
        else:
            print('Missing '+hourlist[h].strftime('%Y%m%d%H'))
    
    PM25=dataall
    PM10=datapm10
    CO=dataco
    
    #vbs_name=['PM25']
    vbs_sname=['PM25','PM10','CO']
    output = Dataset(path_output + '/AQSIODA_hourlyPM25_' + yr+'_' +mon  + '.nc',
                     'w')

    output.createDimension('time', len(hourlist))
    output.createDimension('site', len(site_id_aqsioda))

    # create and name var w units
    var_time = output.createVariable('time', str, ('time',))
    var_id = output.createVariable('site_id', str, ('site',))
    var_lon = output.createVariable('site_lon', 'float', ('site',))
    var_lat = output.createVariable('site_lat', 'float', ('site',))

    for i in range(len(vbs_sname)):
        exec("var_%s  = output.createVariable('%s', 'float', ('time','site'))" % (str(i), vbs_sname[i]))

    # value

    var_lon[:] = np.array(siteinfo['lon'])
    var_lat[:] = np.array(siteinfo['lat'])


    var_time[:] = np.array(hourlist.strftime('%Y-%m-%d%H:%M'))

    for i in range(len(vbs_sname)):
        exec('var_%s[:] = np.array(%s)' % (str(i), vbs_sname[i]))
    output.close()
    print('Data saved to '+path_output + '/AQSIODA_hourlyPM25_' + yr+'_' +mon  + '.nc')
    toc()
        
    print()

    
        

# for yearn in ['2021','2022','2023']:  # ['2010', '2011', '2012', '2013', '2014']:  #'2018','2015',
#     # time
#     date_start = yearn + '0901'
#     date_end = yearn + '0930'
#     date = pd.date_range(start=date_start, end=date_end, freq='D')
#     time = pd.date_range(start=date[0], end=date[-1] + pd.Timedelta('1D'), freq='1H')[:-1]  # OUTPUT EST

#     '''Reading and Sorting Data'''
#     vb_name = ['88101']#['88502']  # input AQS file name 88101-FEM 88502-non FEM
#     vbs_name = ['PM25']  # v name
#     vbs_sname = ['PM25']  # v name
#     vb_unit = ['Micrograms/cubic meter']  # INPUT and OUTPUT unit

#     SS = len(site_id)
#     TT = len(time)
#     PM25 = np.zeros((TT, SS))
#     PM25[:] = np.nan


#     for vv in range(len(vb_name)):
#         print('Processing ' + vb_name[vv] + ' file for ' + yearn + '...')
#         readin = pd.read_csv(path_input + '/hourly_' + vb_name[vv] + '_' + yearn + '.csv')

#         station = []
#         site_name1 = np.array(readin['State Code']).astype('str')
#         site_name2 = np.array(readin['County Code']).astype('str')
#         site_name3 = np.array(readin['Site Num']).astype('str')
#         for s in range(int(len(site_name1))):
#             station.append(str(site_name1[s].zfill(2)) + str(site_name2[s].zfill(3)) + str(site_name3[s].zfill(4)))
#         station = np.array(station)

#         timein1 = np.array(readin['Date GMT']).astype('str')  # INPUT GMT
#         timein2 = np.array(readin['Time GMT']).astype('str')

#         VAR = np.array(readin['Sample Measurement'])
#         Punit = np.array(readin['Units of Measure'])  # INPUT ppm
#         Pname = np.array(readin['Parameter Name'])
#         del readin

#         ####### check variables
#         PnameU = np.unique(Pname)
#         print(PnameU)
#         print(np.unique(Punit))

#         if len(PnameU)==1:

#             for s in np.arange(SS):
#                 index = np.squeeze(np.argwhere(station == site_id[s]))

#                 for i in index:
#                     tempt = datetime.strptime(str(timein1[i]) + str(timein2[i]), '%Y-%m-%d%H:%M')#- timedelta(hours=5)

#                     if np.argwhere(time == tempt):
#                         exec('%s[np.argwhere(time == tempt),s] = np.array(VAR[i])' % vbs_name[vv])
#         else:
#             print('Please split variables: ')
#             print(PnameU)

#     '''Write netCDF file'''

#     output = Dataset(path_output + '/AQS_hourlyPM25_' +vb_name[0]+ '_' +date_start + '_' + date_end  + '.nc',
#                      'w')

#     output.createDimension('time', TT)
#     output.createDimension('site', SS)

#     # create and name var w units
#     var_time = output.createVariable('time', str, ('time',))
#     var_id = output.createVariable('site_id', str, ('site',))
#     var_lon = output.createVariable('site_lon', 'float', ('site',))
#     var_lat = output.createVariable('site_lat', 'float', ('site',))
#     var_county = output.createVariable('site_county', str, ('site',))
#     var_state = output.createVariable('site_state', str, ('site',))
#     var_alt = output.createVariable('site_alt', 'float', ('site',))
#     var_met = output.createVariable('site_met', str, ('site',))
#     var_LU = output.createVariable('site_LU', str, ('site',))
#     var_LS = output.createVariable('site_LS', str, ('site',))
#     var_datum = output.createVariable('site_datum', str, ('site',))

#     for i in range(len(vbs_name)):
#         exec("var_%s  = output.createVariable('%s', 'float', ('time','site'))" % (str(i), vbs_sname[i]))
#         exec('var_%s.units  = vb_unit[%s]' % (str(i), str(i)))

#     # value
#     var_id[:] = site_id
#     var_lon[:] = site_lon
#     var_lat[:] = site_lat
#     var_county[:] = site_countyname
#     var_state[:] = site_statename
#     var_alt[:] = site_alt
#     var_met[:] = site_met
#     var_LU[:] = site_LU
#     var_LS[:] = site_LS
#     var_datum[:] = site_datum

#     var_time[:] = np.array(time.strftime('%Y-%m-%d%H:%M'))

#     for i in range(len(vb_name)):
#         exec('var_%s[:] = np.array(%s)' % (str(i), vbs_sname[i]))
#     output.close()

#     print(yearn + ' Done!!!')


