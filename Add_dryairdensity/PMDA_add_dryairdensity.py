#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# By Huiying Luo, huiying.luo@noaa.gov, Sept 2025, published v1

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

delp = datacore.variables['delp'][:] #air pressure thickness (Pa), from top to surface; Ptop 20mb to 2000 Pa
T = datacore.variables['T'][:] 
delp = np.ma.masked_where(delp == 9.969209968386869e+36, delp)
T = np.ma.masked_where(T == 9.969209968386869e+36, T)
print(delp[0,:,0,0])

## calculation
# v0: rough estimate P=np.cumsum(delp, axis=1)
P=np.cumsum(delp, axis=1)
#print(P[0,:,0,0])

# v1: use ptop to get a more precise estimate. P at center ~ average of top and bottom, validated using Pcenter.py
ptop=2000 #Pa
P=np.zeros(delp.shape)
Pcum=np.cumsum(delp, axis=1)
P[0,0,:,:]=ptop+delp[0,0,:,:]/2
for layer in range(1,delp.shape[1]):
    P[0,layer,:,:]=ptop+Pcum[0,layer-1,:,:]+delp[0,layer,:,:]/2
print(P[0,:,0,0])


Rconst = 287.05 #J/(kg·K), dens (1.225 kg/m3) = P (101325 Pa)/(Rconst * T (k)) 
denstest = P / (T * Rconst)

# print(P[0,:,0,0])
print(np.max(denstest[0,0,:,:]))
print(np.min(denstest[0,0,:,:]))
print(np.max(denstest[0,-1,:,:]))
print(np.min(denstest[0,-1,:,:]))

# Validation A: standard atm https://www.eoas.ubc.ca/courses/atsc113/flying/met_concepts/02-met_concepts/02a-std_atmos-P/index.html#:~:text=The%20table%20above%20shows%20that,bottom%20quarter%20of%20the%20photo).
# density 0.0395 kg/m3, P 2.511 kPa, T -51.5C, H 25 km
# V1 similar to std atm, not the v0/ref from Hongli

# Validation B: monet first layer dense in /mnt/lfs6/BMC/wrfruc/hluo/workflow/cleanrun/PMDA_c/stmp/monet/dynf_2024072721_001.nc to validate

## add variable to core
if 'dry_air_density' in datacore.variables.keys():

    #datacore['dry_air_density'][:] = denstest.astype('float32') # doesn't work for the inital test density w wrong dim
    
    
    for i in range(100): 
        try:
            datacore.renameVariable('dry_air_density','dry_air_density_'+str(i)) # rename original to _i if exist 
            print('Previous estimate saved to V '+ str(i))
            break
        except:
            print('keep searching for a name for previous estimate...')
    print('Updating dry_air_density...')
else:
    print('Adding dry_air_density...')


fed_out = datacore.createVariable('dry_air_density',np.float32,('Time','zaxis_1','yaxis_2','xaxis_1'),chunksizes=np.shape(delp))
fed_out[:] = denstest.astype('float64')

datacore.close()

print('Done')
