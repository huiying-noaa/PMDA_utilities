#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# By Huiying Luo, huiying.luo@noaa.gov, Sept 2025, published v1.2

## Script to add/update dry air density variable to RRFS FV3 background core file for PM2.5 DA
## How to:
    # python/run script_name background_core_file optional_save_original_core_switch (Default value: 1, save copy. Option 0, not save copy)
    # e.g.: python PMDA_add_dryairdensity.py '/scratch2/BMC/wrfruc/hluo/PM3dvar/3dvar_c84/Data/inputs/lam_rrfs/bkg/sd_20200912.120000.fv_core.res.tile1test.nc'
## IMPORTANT NOTE: Script will change background core file directly if switch set to 0! Please copy example data before testing that option!

import netCDF4 as nc
import numpy as np
import sys
import shutil

## Input
filecore = sys.argv[1]
print()
print('Calculating dry air density for '+ filecore)
if len(sys.argv)==3 and sys.argv[2]==0:
    print('NOTE: No original copy will be saved!')
else:
    shutil.copyfile(filecore, filecore+'.copy')
    print('Core file copy saved to '+filecore+'.copy')

## Read and prepare data
datacore =nc.Dataset(filecore,'r+')

delp = datacore.variables['delp'][:] #air pressure thickness (Pa), from top to surface; Ptop 20mb to 2000 Pa
T = datacore.variables['T'][:]
delp = np.ma.masked_where(delp == 9.969209968386869e+36, delp)
T = np.ma.masked_where(T == 9.969209968386869e+36, T)
# print(delp[0,:,0,0])

## Calculation
# v0: rough estimate P=np.cumsum(delp, axis=1)
# P=np.cumsum(delp, axis=1)
# print(P[0,:,0,0])

# v1: use ptop to get a more precise estimate. P at center ~ average of top and bottom, validated using Pcenter.py
ptop=212.637 #Pa for fv3
print('NOTE: Used Ptop at 212.637 Pa for RRFS FV3!')
P=np.zeros(delp.shape)
Pcum=np.cumsum(delp, axis=1)
P[0,0,:,:]=ptop+delp[0,0,:,:]/2
for layer in range(1,delp.shape[1]):
    P[0,layer,:,:]=ptop+Pcum[0,layer-1,:,:]+delp[0,layer,:,:]/2
# print(P[0,:,0,0])


Rconst = 287.05 #J/(kg·K), dens (1.225 kg/m3) = P (101325 Pa)/(Rconst * T (k))
denstest = P / (T * Rconst)

## Validations
# print(np.max(denstest[0,0,:,:]))
# print(np.min(denstest[0,0,:,:]))
# print(np.max(denstest[0,-1,:,:]))
# print(np.min(denstest[0,-1,:,:]))

# Ref: standard atm Table 1-5 from https://www.eoas.ubc.ca/courses/atsc113/flying/met_concepts/02-met_concepts/02a-std_atmos-P/index.html#:~:text=The%20table%20above%20shows%20that,bottom%20quarter%20of%20the%20photo).

## Add variable to core
if 'dry_air_density' in datacore.variables.keys():
    print('dry_air_density already in file, updating value...')
    datacore.variables['dry_air_density'][:] = denstest.astype('float32')
else:
    print('Adding dry_air_density...')
    fed_out = datacore.createVariable('dry_air_density',np.float32,('Time','zaxis_1','yaxis_2','xaxis_1'),chunksizes=np.shape(delp))
    fed_out[:] = denstest.astype('float32')

datacore.close()

print('Done')
