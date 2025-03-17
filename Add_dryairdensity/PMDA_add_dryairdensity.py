#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# By Huiying Luo, huiying.luo@noaa.gov, Sept 2024, published v0

## Script to add/update dry air density variable to background core file for PM2.5 DA 
## How to: 
    # python/run (depends on where the script will be run) script_name background_core_file save_original_copy_switch(optional, 0/1. default value: 1, save copy; 0, not save copy) 
    # e.g.: python PMDA_add_dryairdensity.py '/scratch2/BMC/wrfruc/hluo/PM3dvar/3dvar_c84/Data/inputs/lam_rrfs/bkg/sd_20200912.120000.fv_core.res.tile1test.nc'
## IMPORTANT NOTE: Script will change background core file directly! Please copy example data before testing!
    
import netCDF4 as nc
import numpy as np
import sys
import shutil

## Input. Pending change: option to read core file name from yaml file 
filecore = sys.argv[1] 

if len(sys.argv)==3 and sys.argv[2]==0:
    print('NOTE: Core file will be modified!')
else:
    shutil.copyfile(filecore, filecore+'.copy')
    print('Core file copy saved.')

print('Changing core file...')

## read and prepare data
datacore =nc.Dataset(filecore,'r+')

delp = datacore.variables['delp'][:] #air pressure thickness (Pa), from top to surface
T = datacore.variables['T'][:] 
delp = np.ma.masked_where(delp == 9.969209968386869e+36, delp)
T = np.ma.masked_where(T == 9.969209968386869e+36, T)

## calculation
P=np.cumsum(delp, axis=1)
Rconst = 287.05 #J/(kg·K), dens (1.225 kg/m3) = P (101325 Pa)/(Rconst * T (k)) 
denstest = P / (T * Rconst)
    
## add variable to core
if 'dry_air_density' in datacore.variables.keys():

    #datacore['dry_air_density'][:] = denstest.astype('float32') # doesn't work for the inital test density w wrong dim
    
    print('Updating dry_air_density...')
    datacore.renameVariable(u'dry_air_density',u'dry_air_density_delete') # rename original to _delete if exist 
else:
    print('Adding dry_air_density...')

fed_out = datacore.createVariable('dry_air_density',np.float32,('Time','zaxis_1','yaxis_2','xaxis_1'),chunksizes=np.shape(delp))
fed_out[:] = denstest.astype('float64')

datacore.close()

print('Done')