#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# By Huiying Luo, huiying.luo@noaa.gov, Aug 2024, published v0

import netCDF4 as nc
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
import cartopy.crs as ccrs
import cartopy.feature as cf
import sys
import shutil

## Readdata. Pending change: read file names from yaml file 

fn_obsin = '/scratch2/BMC/wrfruc/hwang/fire2/DA_C775/T1/fv3-jedi/test/ioda_pm2p5/airnow-ave2grid-out/airnow-v2-2020091212.nc'
fn_obsout = '/scratch2/BMC/wrfruc/hluo/PM3dvar/3dvar_c84/Data/hofx/3dvar_rrfs-sd_vader_pm25_2020091212.nc'
fn_plot = 'test.png'


obsin = nc.Dataset(fn_obsin,'r')
obsout = nc.Dataset(fn_obsout,'r')

lats_pm = obsin.groups['MetaData'].variables['latitude'][:]
lons_pm = obsin.groups['MetaData'].variables['longitude'][:]
pm_noqc  = obsin.groups['ObsValue'].variables['particulatematter2p5Surface'][:]
pre_qc = obsin.groups['PreQC'].variables['particulatematter2p5Surface'][:]

lats_da_noqc = obsout.groups['MetaData'].variables['latitude'][:]
lons_da_noqc = obsout.groups['MetaData'].variables['longitude'][:]
oman_noqc = obsout.groups['oman'].variables['particulatematter2p5Surface'][:]
ombg_noqc = obsout.groups['ombg'].variables['particulatematter2p5Surface'][:]
hofx0_noqc = obsout.groups['hofx0'].variables['particulatematter2p5Surface'][:]
hofx1_noqc = obsout.groups['hofx1'].variables['particulatematter2p5Surface'][:]
ob_err_vals_noqc = obsout.groups['ObsError'].variables['particulatematter2p5Surface'][:]
ob_vals_noqc = obsout.groups['ObsValue'].variables['particulatematter2p5Surface'][:]


msize = 8 #plot marker size
lonlimits = (-135,-75)
latlimits = (20,55)
cmap1='viridis'
cmap2='Spectral_r'
fig, [[ax1, ax2, ax3], [ax4, ax5, ax6]] = plt.subplots(nrows=2, ncols=3, subplot_kw={'projection': ccrs.PlateCarree()},sharex=True,sharey=True,figsize=(21,7))
fig.suptitle('Observation Space diagnostics')



# PM in
ax1.add_feature(cf.BORDERS,zorder=0) 
ax1.add_feature(cf.COASTLINE,zorder=0)
ax1.add_feature(cf.STATES,zorder=0)
varplot=pm_noqc
p1 = ax1.scatter(lons_pm,lats_pm,c=pm_noqc,s=msize,cmap='jet',zorder=2,edgecolors='k',linewidths=0.1,vmin=0,vmax=100)
ax1.set_title(f'Observed PM2.5',fontsize=10)
fig.colorbar(p1)
ax1.set_xlim(lonlimits)
ax1.set_ylim(latlimits)


#hofx
ax2.add_feature(cf.BORDERS,zorder=0) 
ax2.add_feature(cf.COASTLINE,zorder=0)
ax2.add_feature(cf.STATES,zorder=0)
varplot=hofx0_noqc
p2 = ax2.scatter(lons_da_noqc,lats_da_noqc,c=hofx0_noqc,s=msize,cmap='jet',edgecolors='k',linewidths=0.1,zorder=2,vmin=0,vmax=100)
ax2.set_title(f'HofX0\nmn,mx,mean={np.min(varplot):.3}, {np.max(varplot):.3}, {np.mean(varplot):.3}',fontsize=10)
fig.colorbar(p2)


#hofx
ax3.add_feature(cf.BORDERS,zorder=0)
ax3.add_feature(cf.COASTLINE,zorder=0)
ax3.add_feature(cf.STATES,zorder=0)
varplot=hofx1_noqc
p3 = ax3.scatter(lons_da_noqc,lats_da_noqc,c=hofx1_noqc,s=msize,cmap='jet',edgecolors='k',linewidths=0.1,zorder=2,vmin=0,vmax=100)
ax3.set_title(f'HofX1\nmn,mx,mean={np.min(varplot):.3}, {np.max(varplot):.3}, {np.mean(varplot):.3}',fontsize=10)
fig.colorbar(p3)


#increments
increment= ombg_noqc - oman_noqc #reversed from hofx_an - hofx_bg because hofx is subtracted in each of ombg and oman
print('increment check',np.size(increment))
print(np.ma.median(increment))
ax4.add_feature(cf.BORDERS,zorder=0)
ax4.add_feature(cf.COASTLINE,zorder=0)
ax4.add_feature(cf.STATES,zorder=0)
varplot=increment
p4 = ax4.scatter(lons_da_noqc,lats_da_noqc,c=varplot,s=msize,cmap='jet',edgecolors='k',linewidths=0.1,zorder=2,vmin=-5,vmax=5)
ax4.set_title(f'Analysis - Background\nmn,mx,mean={np.min(varplot):.3}, {np.max(varplot):.3}, {np.mean(varplot):.3}',fontsize=10)
fig.colorbar(p4)


#ombg
ax5.add_feature(cf.BORDERS,zorder=0)
ax5.add_feature(cf.COASTLINE,zorder=0)
ax5.add_feature(cf.STATES,zorder=0)
varplot=ombg_noqc
p5 = ax5.scatter(lons_da_noqc,lats_da_noqc,c=varplot,s=msize,cmap='jet',edgecolors='k',linewidths=0.1,zorder=2,vmin=-20,vmax=20)
ax5.set_title(f'OMBG\nmn,mx,mean={np.min(varplot):.3}, {np.max(varplot):.3}, {np.mean(varplot):.3}',fontsize=10)
fig.colorbar(p5)



#oman
ax6.add_feature(cf.BORDERS,zorder=0)
ax6.add_feature(cf.COASTLINE,zorder=0)
ax6.add_feature(cf.STATES,zorder=0)
varplot=oman_noqc
p6 = ax6.scatter(lons_da_noqc,lats_da_noqc,c=varplot,s=msize,cmap='jet',edgecolors='k',linewidths=0.1,zorder=2,vmin=-20,vmax=20)
ax6.set_title(f'OMAN\nmn,mx,mean={np.min(varplot):.3}, {np.max(varplot):.3}, {np.mean(varplot):.3}',fontsize=10)
fig.colorbar(p6)

plt.savefig(fn_plot,dpi=600, bbox_inches='tight')