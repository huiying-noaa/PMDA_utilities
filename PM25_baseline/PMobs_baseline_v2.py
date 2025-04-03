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

import warnings
warnings.filterwarnings('ignore')

###########

mon='07'
path_output = 'PMbaseline'
#############


######### Input loading
# Met: asos, buoy, aqs,mesonet

Met_T = []
#########

#############
# AQS
marker=0

for yrid in range(2015,2025):# not include 2025

    yr=str(yrid)

    inpath='PMobs/AQSIODA_hourlyPM25_' +yr+'_'+mon  + '.nc'
    if os.path.isfile(inpath):
        print('Reading '+yr)
        ds = Dataset(inpath)
        if marker==0:
            site_id_aqs = ds.variables['site_id'][:]
   
            site_lat_aqs = ds.variables['site_lat'][:]
            site_lon_aqs = ds.variables['site_lon'][:]
            
            DS_aqs = ds.variables['PM25'][:]
            DS_CO=ds.variables['CO'][:]
            DS_PM10=ds.variables['PM10'][:]

        else:
            DS_aqs = np.concatenate((DS_aqs,ds.variables['PM25'][:]))
            DS_CO=np.concatenate((DS_CO,ds.variables['CO'][:]))
            DS_PM10=np.concatenate((DS_PM10,ds.variables['PM10'][:]))
            
        for i in range(len(ds.variables['time'])):
            Met_T.append(datetime.strptime(ds.variables['time'][i],'%Y-%m-%d%H:%M'))
    marker=1

siteinfo=pd.read_csv('PMbaseline/PMIODA_site_mon'+mon+'.csv')
site_id_aqs=np.array(siteinfo['siteid'])

data_base=np.zeros([len(site_id_aqs),24])
data_base[:]=np.nan

data_rate=np.zeros([len(site_id_aqs),24])
data_rate[:]=np.nan

event_tag=np.zeros([len(Met_T),len(site_id_aqs)])
event_tag[:]=np.nan #0 no, 1 polluted, 2 reclassified no, 3 reclassified yes

# calculate RMS for each hour and mark event
for s in range(len(site_id_aqs)):
    if np.count_nonzero(~np.isnan(DS_aqs[:,s]))<10:
        continue
    else: 
        numobs=np.zeros(24)
        #fig, ax1=plt.subplots(figsize=(5,3))
        for h in range(24):
            data=DS_aqs[h::24,s]
            data=data[~np.isnan(data)]
            numobs[h]=len(data)
            #ax1.boxplot(data,positions=[h],widths=0.7)
   
            
            if np.count_nonzero(~np.isnan(data))<10: # <(0.5*len(data)): # less than 50% obs
                data_base[s,h]=np.nan
            else:
                rms = sqrt(mean(square(data[data<median(data)])))
                data_base[s,h]=2*rms#mean(data[data<3*rms])#3*rms#
                
                
                data_rate[s,h]=sum(np.abs(data) < data_base[s,h]) / float(len(data))
            for d in range(len(DS_aqs[h::24,s])):
                if DS_aqs[h+d*24,s]<data_base[s,h]:
                    event_tag[h+d*24,s]=0
                elif DS_aqs[h+d*24,s]>(data_base[s,h]/2*3):
                    event_tag[h+d*24,s]=1
        for h in range(1,len(DS_aqs[:,s])):
            if np.isnan(event_tag[h,s]) and ~np.isnan(DS_aqs[h,s]):
                event_tag[h,s]=event_tag[h-1,s]+2
                
        
        # ax1.plot(data_base[s,:])
        # ax1.set_xlabel('UTC hour')
        # ax1.set_ylabel('PM$_{2.5}$ (µg/m³)')
        
        # ax2 = ax1.twinx()
        # ax2.plot(numobs, 'r-')
        # ax2.set_ylabel('Obs #')
        # ax2.set_ylim([0, np.max(numobs)+5])
        
        # plt.xticks(np.round(np.linspace(0, 22, 12)).astype(int),np.round(np.linspace(0, 22, 12)).astype(int))
        # #plt.ylim([0,90])
        # plt.title(calendar.month_name[int(mon)]+' PM$_{2.5}$ Background Estimation \n'+ site_id_aqs[s])
        # plt.savefig(path_output+'/num'+calendar.month_name[int(mon)]+site_id_aqs[s]+'nolim_IODA_25rms.png',dpi=300, bbox_inches='tight')
        # plt.close()

## set baseline value

baseline=np.zeros([len(site_id_aqs),24])
baseline[:]=np.nan

for s in range(len(site_id_aqs)):
    if np.count_nonzero(~np.isnan(DS_aqs[:,s]))<10:
        continue
    else: 
      
        for h in range(24):
            data=DS_aqs[h::24,s]
            tag=event_tag[h::24,s]
            #ax1.boxplot(data,positions=[h],widths=0.7)
   
            
            if np.count_nonzero(~np.isnan(data))<10: # <(0.5*len(data)): # less than 50% obs
                baseline[s,h]=np.nan
            else:
                baseline[s,h]=np.mean(data[tag% 2 == 0])
                # check pct
                data=data[~np.isnan(data)]
                data_rate[s,h]=sum(np.abs(data) < baseline[s,h]) / float(len(data))
                
            

PM25baseline=baseline

## eva with few days and PM10/CO
# indt=24*7
# for s in range(len(site_id_aqs)):
#     fig, ax1=plt.subplots(figsize=(10,3))
#     t=Met_T[-indt:]
#     data=DS_aqs[-indt:,s]
#     ax1.plot(t,data,label='PM2.5')
    
#     data=DS_CO[-indt:,s]
#     ax1.plot(t,data*50,label='CO*50')
    
#     data=DS_PM10[-indt:,s]
#     ax1.plot(t,data/5,label='PM10/5')

#     plt.legend(loc="best")
    
#     data=event_tag[-indt:,s]
#     ax2 = ax1.twinx()
#     for i in range(len(data)):
#         if data[i] % 2 == 0:
#             ax2.plot(t[i],data[i], 'b^')
#         else:
#             ax2.plot(t[i],data[i], 'r^')
#     ax2.set_ylabel('Event tag')
#     plt.grid(axis='x')
#     plt.savefig('10yr_'+site_id_aqs[s]+'.png',dpi=300, bbox_inches='tight')


## eva w PM10/CO violin

for s in range(len(site_id_aqs)):
    for h in range(24):
        data=DS_aqs[h::24,s]
        dataCO=DS_CO[-indt:,s]
        
        event_tag[h::24,s]
        
        fig, ax1=plt.subplots(figsize=(7,5))

        ax1.violinplot(data,positions=[h],widths=0.7,showmedians=True)
        
        
        ax1.plot(t,data,label='PM2.5')
        
        data=DS_CO[-indt:,s]
        ax1.plot(t,data*50,label='CO*50')
        
        data=DS_PM10[-indt:,s]
        ax1.plot(t,data/5,label='PM10/5')
    
        plt.legend(loc="best")
        
        data=event_tag[-indt:,s]
        ax2 = ax1.twinx()
        for i in range(len(data)):
            if data[i] % 2 == 0:
                ax2.plot(t[i],data[i], 'b^')
            else:
                ax2.plot(t[i],data[i], 'r^')
        ax2.set_ylabel('Event tag')
        plt.grid(axis='x')
        plt.savefig('10yr_'+site_id_aqs[s]+'_'+str(h)+'.png',dpi=300, bbox_inches='tight')

'''Write netCDF file'''

# output = Dataset(path_output + '/IODA_hourlyPM25baseline_' +mon  + '_v2.nc',
#                   'w')
# output.createDimension('time', 24)
# output.createDimension('site', len(site_id_aqs))




# # create and name var w units
# var_time = output.createVariable('time', str, ('time',))
# var_id = output.createVariable('site_id_aqs', str, ('site',))
# var_lon = output.createVariable('site_lon', 'float', ('site',))
# var_lat = output.createVariable('site_lat', 'float', ('site',))
# var_county = output.createVariable('site_county', str, ('site',))
# var_state = output.createVariable('site_state', str, ('site',))
# var_alt = output.createVariable('site_alt', 'float', ('site',))
# var_met = output.createVariable('site_met', str, ('site',))
# var_LU = output.createVariable('site_LU', str, ('site',))
# var_LS = output.createVariable('site_LS', str, ('site',))
# var_datum = output.createVariable('site_datum', str, ('site',))
    
# vbs_sname = ['PM25baseline','data_rate']  # v name
# vb_unit = ['Micrograms/cubic meter','percentile']  # INPUT and OUTPUT unit

# # vbs_sname = ['PM25baseline']  # v name
# # vb_unit = ['Micrograms/cubic meter']  # INPUT and OUTPUT unit

# for i in range(len(vbs_sname)):
#     exec("var_%s  = output.createVariable('%s', 'float', ('site','time'))" % (str(i), vbs_sname[i]))
#     exec('var_%s.units  = vb_unit[%s]' % (str(i), str(i)))

# # value
# var_id[:] = site_id_aqs
# var_lon[:] = site_lon_aqs
# var_lat[:] = site_lat_aqs

# var_time[:] = np.array(np.arange(24).astype(str))

# for i in range(len(vbs_sname)):
#     exec('var_%s[:] = np.array(%s)' % (str(i), vbs_sname[i]))
# output.close()

