#!/usr/bin/env python3
# Remove bkg from airnow obs file from MONET
# Author: Huiying Luo, last modified Jun 2025

import os

from math import cos, sin, asin, sqrt
import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates


import random

import glob
import matplotlib.pyplot as plt
import numpy as np

from math import radians, cos, sin, asin, sqrt
import pandas as pd
from datetime import datetime

from numpy import mean, sqrt, square, median

from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
import cartopy.crs as ccrs
import cartopy.feature as cf
import calendar


import numpy as np
import sys
import shutil
    
########### Input ############

basepath='PMbaseline/IODA_hourlyPM25baseline_v2final.nc'  
inpath='PMobs_airnow/AIRNOW_20240720_20240731_MONET.nc' # prepared by JS_reformat_airnow.py from Johana
#inpath='PMobs_airnow/test5.airnow.20240724-20240725.nc' # prepared by workflow from Jordan, no masks in PM2.5, possible issues w MONET eva?
outpath=inpath[:-3]+'_PM25blremoved_'+basepath[-10:]
threshold_km=100 # searching max distance for baseline

############# Background removal ################
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c  # Radius of earth in kilometers. Use 3956 for miles
    return km

def find_nearest_within_threshold(reference_lat, reference_lon, lat,lon, threshold_km):

    min_distance = 10000
    
    for s in range(len(lat)):
        distance = haversine(reference_lat, reference_lon, lat[s], lon[s])
        if distance < min_distance:
            min_distance = distance
            nearest_location = s
            # print(min_distance)
    #         print(reference_lat)
    #         print(lat[s])
    # print()
    # print(min_distance)
    
    if min_distance<threshold_km:
        #print('yes')
        return nearest_location
    else:
        print('no')
        print(min_distance)
        return np.nan
        

def copy_group(src_group, dst_group,DS_aqsfinal):
    """
    Recursively copy a group and its contents (dimensions, variables, attributes, and subgroups).
    """
    # Copy global attributes
    for name in src_group.ncattrs():
        dst_group.setncattr(name, src_group.getncattr(name))

    # Copy dimensions
    for name, dimension in src_group.dimensions.items():
        dst_group.createDimension(name, len(dimension) if not dimension.isunlimited() else None)

    # Copy variables
    for name, variable in src_group.variables.items():
        # Check if the source variable has a _FillValue attribute
        fill_value = variable._FillValue if '_FillValue' in variable.ncattrs() else None

        # Create the variable in the destination group with the fill_value
        dst_var = dst_group.createVariable(
            name,
            variable.datatype,
            variable.dimensions,
            fill_value=fill_value  # Set fill_value here
        )

        # Copy variable attributes (excluding _FillValue, as it's already set)
        for attr_name in variable.ncattrs():
            if attr_name != '_FillValue':  # Skip _FillValue, as it's already set
                dst_var.setncattr(attr_name, variable.getncattr(attr_name))

        # Copy variable data
 
        if name=='PM2.5':
            print('Changing value of PM2.5...')

            dst_var[:] = DS_aqsfinal[:]
            
        else:
         
            dst_var[:] = variable[:]
        
    # Recursively copy subgroups
    for name, subgroup in src_group.groups.items():
        dst_subgroup = dst_group.createGroup(name)
        copy_group(subgroup, dst_subgroup)

# read bkg
dss = nc.Dataset(basepath)
site_id_aqs = dss.variables['site_id_aqs'][:]
site_lat_aqs = dss.variables['site_lat'][:]
site_lon_aqs = dss.variables['site_lon'][:]
DS_aqs = dss.variables['PM25baseline'][:]
dss.close()
    

# read obs input
ds = nc.Dataset(inpath)
site_time_aqsioda = ds['time'][:]#(time) int min since 2024-07-20 00:00:00
dst=nc.num2date(site_time_aqsioda, units=ds['time'].units, calendar='standard')
site_id_aqsioda = ds['siteid'][0,:]#longitude(y, x)
site_lat_aqsioda = ds['latitude'][0,:]
site_lon_aqsioda = ds['longitude'][0,:] 
DS_aqsioda = ds['PM2.5'][:,0,:] #(time, y, x), time*site

## checking changed file
dsr = nc.Dataset(outpath)
site_time_aqsioda = dsr['time'][:]#(time) int min since 2024-07-20 00:00:00
DS_aqsf = dsr['PM2.5'][:,0,:] #(time, y, x), time*site

# ## checking with original changed file with Johana's script
# dsrq = nc.Dataset('PMobs_airnow/AIRNOW_20240720_20240731_MONET_PM25bkgremoved_v2.nc')
# site_time_aqsioda = dsrq['time'][:]#(time) int min since 2024-07-20 00:00:00
# DS_aqsfq = dsrq['PM2.5'][:,0,:] #(time, y, x), time*site

# calculate new value
DS_aqsfinal=np.zeros([len(site_time_aqsioda),1,len(site_id_aqsioda)])
DS_aqsfinal[:]=np.nan
DS_aqscali=np.zeros([len(site_id_aqsioda)])

counter=0
for s in range(len(site_id_aqsioda)):
    if len(np.where(site_id_aqs==site_id_aqsioda[s])[0])==0:
        #print('Searching for nearby location for site: '+site_id_aqsioda[s])
        #nearest = find_nearest_within_threshold(reference_lat, reference_lon, locations, threshold_km)
        nearest = find_nearest_within_threshold(site_lat_aqsioda[s], site_lon_aqsioda[s], site_lat_aqs,site_lon_aqs, threshold_km)
        if np.isnan(nearest):
            DS_aqsfinal[:,0,s]=np.nan
            counter=counter+1
        else:
            
            for i in range(len(DS_aqsfinal[:,0,s])):
                DS_aqsfinal[i,0,s]=DS_aqsioda[i,s]-DS_aqs[nearest,dst[i].month-1,dst[i].hour]
            DS_aqscali[s]=1
    else:
        #print(site_id_aqsioda[s])
        #DS_aqsfinal[:,s]=DS_aqsioda[:,s]-DS_aqs[np.where(site_id_aqs==site_id_aqsioda[s])[0],np.array(np.floor(site_time_aqsioda/60)%24,dtype=int)]
        for i in range(len(DS_aqsfinal[:,0,s])):
            DS_aqsfinal[i,0,s]=DS_aqsioda[i,s]-DS_aqs[np.where(site_id_aqs==site_id_aqsioda[s])[0],dst[i].month-1,dst[i].hour]
        DS_aqscali[s]=1
DS_aqsfinal[DS_aqsfinal<0]=0.0
print('Number of Sites Discarded: '+str(counter))


## save new file w bkg removed     


# Paths to the source and destination files
source_file = inpath
destination_file = outpath

# Open the source file in read mode
with nc.Dataset(source_file, 'r') as src:
    # Create the destination file in write mode
    with nc.Dataset(destination_file, 'w') as dst:
        # Copy the root group and all its contents
        copy_group(src, dst,DS_aqsfinal)

           

# ################### Figure #############

# # figure control, figure show before, bkg and after
# idlist=['abcdefghijklmnopq']
# msize=8
# widththin=0.2
# lonlimits = (-129,-60)
# latlimits = (23,55)
# basegrey=[0.1,0.1,0.1]
# hax1=[0.04,0.04,0.4,0.88]
# hax2=[0.54,0.04,0.4,0.88]


# ######### 
# fig, axes = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': ccrs.PlateCarree()},sharex=True,sharey=True,figsize=(11,3))
# axes=axes.flat
# #fig.suptitle('Background Removal+', '+timein,fontsize=12)

# dtest=nc.Dataset(outpath)
# aft_site_id_aqsioda = dtest['MetaData']['stationIdentification'][:]
# aft_site_lat_aqsioda = dtest['MetaData']['latitude'][:]
# aft_site_lon_aqsioda = dtest['MetaData']['longitude'][:]
# aft_DS_aqsioda = dtest['ObsValue']['particulatematter2p5Surface'][:]
# dtest.close()

# ax=axes[0]#[hh]

# ax.add_feature(cf.BORDERS,zorder=0, linewidth=widththin*3) 
# ax.add_feature(cf.COASTLINE,zorder=0, linewidth=widththin*3)
# ax.add_feature(cf.STATES,zorder=0, linewidth=widththin)

# varplot=DS_aqsioda-aft_DS_aqsioda
# p1 = ax.scatter(site_lon_aqsioda,site_lat_aqsioda,c=varplot,s=msize,cmap='jet',linewidths=0.1,vmin=0,vmax=40)

# # varplot=DS_aqsfinal
# # # calibrated non-SD sites, gray
# # ax.scatter(site_lon_aqsioda[(DS_aqscali==1)&(DS_aqsfinal==0)],site_lat_aqsioda[(DS_aqscali==1)&(DS_aqsfinal==0)],c=[np.add(basegrey,0.7)],edgecolor='none',s=msize,linewidths=0.4)

# # # not calibrated sites
# # p1 = ax.scatter(site_lon_aqsioda[DS_aqscali==0],site_lat_aqsioda[DS_aqscali==0],c=varplot[DS_aqscali==0],s=msize/2,cmap='jet',linewidths=0.1,vmin=0,vmax=40)
# # # calibrated sites
# # p1 = ax.scatter(site_lon_aqsioda[(DS_aqscali==1)&(DS_aqsfinal!=0)],site_lat_aqsioda[(DS_aqscali==1)&(DS_aqsfinal!=0)],c=varplot[(DS_aqscali==1)&(DS_aqsfinal!=0)],s=msize,cmap='jet',linewidths=0.1,vmin=0,vmax=40)



# ax.set_title('Background PM$_{2.5}$ at '+timein)
# cbar_ax=fig.add_axes([0.45,0.04,0.01,0.88])
# clb=fig.colorbar(p1,cax=cbar_ax)
# # hax1=[0.04,0.04,0.4,0.88]
# # hax2=[0.54,0.04,0.4,0.88]

# clb.ax.set_title('(µg/m³)')
# ax.set_xlim(lonlimits)
# ax.set_ylim(latlimits)
# ax.set_position(hax1)

# ax=axes[1]
# ax.add_feature(cf.BORDERS,zorder=5, linewidth=widththin*3) 
# ax.add_feature(cf.COASTLINE,zorder=5, linewidth=widththin*3)
# ax.add_feature(cf.STATES,zorder=5, linewidth=widththin)

# # AOD

# varplot=aft_DS_aqsioda
# p1 = ax.scatter(site_lon_aqsioda,site_lat_aqsioda,c=varplot,s=msize,cmap='jet',linewidths=0.1,vmin=0,vmax=40)



# ax.set_title('SD PM$_{2.5}$ at '+timein)
# cbar_ax=fig.add_axes([0.95,0.04,0.01,0.88])
# clb=fig.colorbar(p1,cax=cbar_ax)
# clb.ax.set_title('')
# ax.set_xlim(lonlimits)
# ax.set_ylim(latlimits)
# ax.set_position(hax2)

   
   
# plt.savefig('PMSD'+timein+'.jpg',dpi=600, bbox_inches='tight')



