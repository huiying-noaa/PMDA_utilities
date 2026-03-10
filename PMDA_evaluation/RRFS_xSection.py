from matplotlib import pyplot as plt
from matplotlib import colormaps as cmaps 
import pandas as pd
import netCDF4
import sys
import numpy as np
import xarray as xr

from matplotlib import ticker, cm
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.colors as colors
import matplotlib as mpl

from netCDF4 import Dataset, MFDataset

from datetime import date, datetime, timedelta, timezone

import time
import numpy.matlib
import numpy.ma as ma

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import warnings
import os
import fnmatch
import glob
import gc
import csv
import pickle

from math import radians, sin, cos, acos, exp

#make colormap whitebluegreenyellowred for smoke
def Rip_of_whitebluegreenyellowred():
    ''' Rip off NCL's WhiteBlueGreenYellowRed '''
    cpool = ['#cfedfb', '#cdecfb', '#caebfb', '#c7eafa', '#c5e9fa', '#c2e8fa',
             '#bfe7fa', '#bde6fa', '#bae5f9', '#b7e4f9', '#b5e3f9', '#b2e2f9',
             '#b0e1f9', '#ade0f8', '#aadff8', '#a8def8', '#a5ddf8', '#a2dcf7',
             '#9ddaf7', '#9bd8f6', '#98d6f5', '#96d4f3', '#94d2f2', '#92d0f1',
             '#8fcef0', '#8dccee', '#8bcaed', '#88c8ec', '#86c5eb', '#84c3ea',
             '#81c1e8', '#7fbfe7', '#7dbde6', '#7bbbe5', '#78b9e4', '#76b7e2',
             '#74b5e1', '#71b3e0', '#6fb1df', '#6dafdd', '#6aaddc', '#68abdb',
             '#66a9da', '#64a7d9', '#61a5d7', '#5fa3d6', '#5da0d5', '#5a9ed4',
             '#589cd3', '#569ad1', '#5398d0', '#5196cf', '#4f94ce', '#4d92cc',
             '#488eca', '#488fc6', '#4890c3', '#4891bf', '#4892bc', '#4893b8',
             '#4894b5', '#4895b1', '#4896ad', '#4897aa', '#4899a6', '#489aa3',
             '#489b9f', '#489c9c', '#489d98', '#489e94', '#489f91', '#48a08d',
             '#48a18a', '#49a286', '#49a383', '#49a47f', '#49a57c', '#49a678',
             '#49a774', '#49a871', '#49a96d', '#49aa6a', '#49ac66', '#49ad63',
             '#49ae5f', '#49af5b', '#49b058', '#49b154', '#49b251', '#49b34d',
             '#49b546', '#4eb647', '#53b847', '#57b948', '#5cbb48', '#61bc49',
             '#66bd4a', '#6abf4a', '#6fc04b', '#74c14b', '#79c34c', '#7ec44d',
             '#82c64d', '#87c74e', '#8cc84e', '#91ca4f', '#96cb50', '#9acc50',
             '#9fce51', '#a4cf51', '#a9d152', '#add252', '#b2d353', '#b7d554',
             '#bcd654', '#c1d755', '#c5d955', '#cada56', '#cfdc57', '#d4dd57',
             '#d9de58', '#dde058', '#e2e159', '#e7e25a', '#ece45a', '#f0e55b',
             '#f5e75b', '#fae85c', '#fae55b', '#fae159', '#fade58', '#f9da56',
             '#f9d755', '#f9d454', '#f9d052', '#f9cd51', '#f9c950', '#f9c64e',
             '#f9c34d', '#f8bf4b', '#f8bc4a', '#f8b849', '#f8b547', '#f8b246',
             '#f8ae45', '#f8ab43', '#f7a742', '#f7a440', '#f7a03f', '#f79d3e',
             '#f79a3c', '#f7963b', '#f7933a', '#f68f38', '#f68c37', '#f68935',
             '#f68534', '#f68233', '#f67e31', '#f67b30', '#f6782f', '#f5742d',
             '#f5712c', '#f56a29', '#f46829', '#f36629', '#f26429', '#f16229',
             '#f06029', '#ef5e29', '#ef5c29', '#ee5a29', '#ed5829', '#ec5629',
             '#eb5429', '#ea5229', '#e95029', '#e84e29', '#e74c29', '#e64a29',
             '#e54829', '#e44629', '#e44328', '#e34128', '#e23f28', '#e13d28',
             '#e03b28', '#df3928', '#de3728', '#dd3528', '#dc3328', '#db3128',
             '#da2f28', '#d92d28', '#d92b28', '#d82928', '#d72728', '#d62528',
             '#d52328', '#d31f28', '#d11f28', '#cf1e27', '#ce1e27', '#cc1e26',
             '#ca1e26', '#c81d26', '#c71d25', '#c51d25', '#c31d24', '#c11c24',
             '#c01c24', '#be1c23', '#bc1b23', '#ba1b22', '#b91b22', '#b71b22',
             '#b51a21', '#b31a21', '#b21a20', '#b01a20', '#ae191f', '#ac191f',
             '#ab191f', '#a9191e', '#a7181e', '#a5181d', '#a4181d', '#a2171d',
             '#a0171c', '#9e171c', '#9d171b', '#9b161b', '#99161b', '#97161a',
             '#96161a', '#921519']
    cmap_smoke = mpl.colors.ListedColormap(cpool, 'Rip_of_whitebluegreenyellowred')
    cmap_smoke.set_over("#000000")
    cmap_smoke.set_under("#FFFFFF")
    cmap_smoke.set_bad("#FFFFFF")
    cmaps.register(cmap_smoke)
    return cmap_smoke

#VERTINCALLY INTEGRATED SMOKE
title_v_smoke='Vertically-Integrated Smoke (experimental)'
clevs_con_smoke=[0.1,0.2,0.4,0.6,0.8,1,2,4,10,16,24,32,40,50]
clevs_sfc_smoke=[1,2,4,6,8,12,16,20,25,30,40,60,100,200]
clevs_v_smoke =[1,4,7,11,15,20,25,30,40,50,75,150,250,500]

cmap_sfc_smoke=Rip_of_whitebluegreenyellowred()
norm_v_smoke = mpl.colors.BoundaryNorm(clevs_v_smoke,cmap_sfc_smoke.N)
norm_sfc_smoke = mpl.colors.BoundaryNorm(clevs_sfc_smoke,cmap_sfc_smoke.N)
norm_con_smoke = mpl.colors.BoundaryNorm(clevs_con_smoke,cmap_sfc_smoke.N)


# Useful functions

# Check if dir. exists; create one if it doesn't at the branch level
def checkDir(plot_dir):
    if os.path.isdir(plot_dir):
        print('Plot dir already exists!')
    else:
        print('Plot dir does not exist, creating it!')
        os.mkdir(plot_dir);

# Get the model grid indices or a given lat,lon pair
def get_XY_latlon(lat_model,lon_model,lat_user,lon_user):
    abslat = np.abs(lat_model-lat_user)
    abslon = np.abs(lon_model-lon_user)
    c      = np.maximum(abslon, abslat)
    x, y   = np.where(c == np.min(c))     
    return x[0],y[0]

# Find closest indices for a given lat, lon pairs
# Method 1: Use cKDTree
def find_closest_indices(lat_grid, lon_grid, target_lats, target_lons):
    """Return list of grid indices along the list of lat lons using cKDTree."""
    # Flatten the 2D lat/lon grid
    lat_flat = lat_grid.ravel()
    lon_flat = lon_grid.ravel()

    # Create KDTree on (lat, lon) points
    tree = cKDTree(np.c_[lat_flat, lon_flat])

    # Query nearest neighbors
    distances, flat_indices = tree.query(np.c_[target_lats, target_lons])

    # Convert flat indices back to 2D indices
    iy, ix = np.unravel_index(flat_indices, lat_grid.shape)

    return iy, ix

# Method 2: Use Bresenham line method
def bresenham_line(a1, b1, a2, b2):
    """Return list of grid indices along the line from (a1, b1) to (a2, b2) using Bresenham's algorithm."""
    x0, y0 = b1, a1  # note: b is x-axis (grid_xt), a is y-axis (grid_yt)
    x1, y1 = b2, a2

    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        points.append((y0, x0))  # back to (a, b) ordering
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

    return points

levels_int_smoke = [1, 4, 7, 11, 15, 20, 25, 30, 40, 50, 75, 150, 250, 500]
levels_sfc_smoke = [1, 2, 4, 6,  8,  12, 16, 20, 25, 30, 40, 60,  100, 200]

def smoke_colors() -> np.ndarray:
        white = plt.get_cmap('Greys', 2)([0])
        blues = plt.get_cmap('Blues', 6)(range(1, 5))
        green_yellow_red = plt.get_cmap('RdYlGn_r', 18)([1, 3, 5, 9, 12, 13, 14, 16, 18])
        purple = np.array([colors.to_rgba('xkcd:vivid purple')])
        return np.concatenate((white, blues, green_yellow_red, purple))


# Load a sample netcdf file
netcdf_dir = '/scratch3/BMC/acomp/Sudheer/Fire-nest/Retros/SheepFire_Data/2019072400/fcst_fv3lam/'
dyn_nc = netCDF4.Dataset(netcdf_dir+'dynf023.nc')
print(list(dyn_nc.variables.keys()))


n_lev = 65; # Number of vertical levels

nx=np.shape(np.squeeze(dyn_nc['lon']))[0]
ny=np.shape(np.squeeze(dyn_nc['lon']))[1]

# Initialize variables
# Vars that dont change with time
lat_rrfs = np.empty((nx,ny)) * np.nan
lon_rrfs = np.empty((nx,ny)) * np.nan
hgtsfc   = np.empty((nx,ny)) * np.nan

# Enough to read once as these wont change with time
lat_rrfs = dyn_nc['lat'][:,:] 
lon_rrfs = dyn_nc['lon'][:,:]
lon_rrfs = lon_rrfs-360 # convert Longitude from 0 to 360 to -180 to 180

hgtsfc = dyn_nc['hgtsfc'][0,:,:]

currdir = os.getcwd()
plot_dir  = currdir + '/xSectionPlots/'
checkDir(plot_dir)

# Plot the terrain
states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lakes',
        scale='50m',
        facecolor='none')

levels=np.arange(-200,3200,200)

fig = plt.figure(figsize=(7,5))
ax = plt.axes(projection=cartopy.crs.PlateCarree())

CS=plt.contour(lon_rrfs,lat_rrfs,hgtsfc,
               transform=cartopy.crs.PlateCarree(),
               levels=np.arange(-100,3200,200),colors='k',linewidths=0.4,zorder=1)

graph=plt.contourf(lon_rrfs,lat_rrfs,hgtsfc,
                   transform=cartopy.crs.PlateCarree(),
                   cmap='terrain',levels=levels,zorder=0,extend='both')

plt.colorbar(graph,label='Elevation MSL [m]',orientation='horizontal',pad=0.1,shrink=0.75)

ax.set_extent([-113,-108, 43, 46])

ax1 = plt.gca()
ax1.add_feature(states_provinces, edgecolor='k', linewidth=0.3)

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, rotate_labels=False,
              linewidth=1, color='none', alpha=0.1, linestyle='--', x_inline=False, y_inline=False)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 10}
gl.ylabel_style = {'size': 10}
gl.top_labels = False
gl.right_labels = False

fname = plot_dir+'/RRFS_Terrain.png'
plt.savefig(fname, bbox_inches='tight', dpi=300)
plt.close()

# Get the indices between two lat lon points

a1, b1 = get_XY_latlon(lat_rrfs,lon_rrfs,44.3,-112.0)
a2, b2 = get_XY_latlon(lat_rrfs,lon_rrfs,44.3,-109.0)

indices = bresenham_line(a1, b1, a2, b2)

# Build index list for using in xarray
xidx=np.arange(0,len(indices),1)
j=0
i_idx,j_idx=[],[]

# Plot the terrain to check
fig = plt.figure(figsize=(8,3))
ax=plt.axes()
for idx in indices:
    plt.plot(lon_rrfs[idx[0],idx[1]],hgtsfc[idx[0],idx[1]],'ko')
    i_idx.append(idx[0])
    j_idx.append(idx[1])    
    j=j+1    
plt.show()

track_coord = np.arange(len(indices))

# Load the netcdf via xarray for aster filtering
ds_dyn = xr.open_mfdataset(netcdf_dir+'dynf023.nc',combine="by_coords",chunks={"time":1})

xt_da   = xr.DataArray(j_idx,dims=("track"),coords={"track":track_coord})
yt_da   = xr.DataArray(i_idx,dims=("track"),coords={"track":track_coord})

j_idx,i_idx = xt_da,yt_da

R = 287.058 # J/kg/K
P0 = 100000 #mbar

time_da = 0

# Estimate Vertically Integrated smoke
smoke  = dyn_nc['smoke'][0,:,:,:]
delz   = dyn_nc['delz'][0,:,:,:]*-1
alt_rev = delz[::-1]

dpres  = dyn_nc['dpres'][0,:,:,:]
slp    = dyn_nc['pressfc'][0,:,:]
tmp    = dyn_nc['tmp'][0,:,:,:]
dpres_rev=dpres[::-1]
cumsum_dpres_rev = dpres_rev.cumsum(axis=0)
pression_inv = np.array(slp)-cumsum_dpres_rev
tmp_rev = tmp[::-1]
air_density_rev = pression_inv/(tmp_rev*R)
smoke_rev = smoke[::-1]
column    = smoke_rev*air_density_rev*alt_rev

sfc_Smoke = column[0,:,:]
vInt_Smoke = column.sum(axis=0)/1000

# Build RRFS title from time info in the file
cycTime = datetime.strptime(str(dyn_nc['time'].units)[12:],'%Y-%m-%d %H:%M:%S')
fhrTime = str(int(dyn_nc['time'][0]))
nctime     = dyn_nc['time']
fcyc       = cycTime.strftime("%Y%m%d %H")
fhr        = fhrTime.zfill(3)
time_valid = (cycTime+timedelta(hours=float(fhrTime))).strftime("%Y%m%d %H")
rrfs_title_ln1='RRFS CONUS 3km: '+fcyc+' '+' UTC'
rrfs_title_ln2='Fcst Hr: '+fhr+', Valid '+str(time_valid)+' UTC'
rrfs_title = rrfs_title_ln1 + '\n'+rrfs_title_ln2
validTime_str=(cycTime+timedelta(hours=float(fhrTime))).strftime("%Y%m%d%H")

# Plot the vertically integrated smoke 
cbar_colors = smoke_colors()
clevs       = levels_int_smoke

fig  = plt.figure(figsize=(7,5))
ax   = plt.axes(projection=ccrs.PlateCarree())
graph= plt.contourf(lon_rrfs,lat_rrfs,vInt_Smoke,
             transform=ccrs.PlateCarree(), 
             colors=cbar_colors,levels=clevs,extend='both',
             zorder=0)

plt.colorbar(orientation='horizontal',label="Vertically Integrated Smoke [mg m$^{-2}$]",
             cmap=cbar_colors,pad=0.1,shrink=1,ticks=clevs,extend='both')

plt.plot(lon_rrfs[i_idx,j_idx],lat_rrfs[i_idx,j_idx],color='k',linestyle='-', linewidth=2,transform=ccrs.PlateCarree())

ax.set_title(rrfs_title,fontsize=10,loc='left') 

ax.add_feature(states_provinces, edgecolor='k', linewidth=0.3)

ax.set_extent([-113,-108, 43, 46])

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, rotate_labels=False,
              linewidth=0, color='gray', alpha=0.2, linestyle='--', x_inline=False, y_inline=False)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 10}
gl.ylabel_style = {'size': 10}
gl.top_labels = False
gl.right_labels = False

fname = plot_dir+'/'+'Vertically_integrated_Smoke_'+validTime_str+'_UTC.png'
plt.savefig(fname, bbox_inches='tight', dpi=300)
plt.close()

# Calculate the Smoke concentrations
shp_A_lat=np.array(ds_dyn['lat'].isel(grid_xt = j_idx, grid_yt = i_idx))
shp_A_lon=np.array(ds_dyn['lon'].isel(grid_xt = j_idx, grid_yt = i_idx))-360

shp_A_t = ds_dyn['tmp'].isel(time = time_da, grid_xt = j_idx, grid_yt = i_idx)
smoke_curtain = ds_dyn['smoke'].isel(time = time_da, grid_xt = j_idx, grid_yt = i_idx)

dpres  = ds_dyn['dpres'].isel(time = time_da, grid_xt = j_idx, grid_yt = i_idx)
slp    = ds_dyn['pressfc'].isel(time = time_da, grid_xt = j_idx, grid_yt = i_idx)
dpres_rev=dpres[::-1,:]
cumsum_dpres_rev = dpres_rev.cumsum(axis=0)
pression_inv = np.array(slp)-cumsum_dpres_rev
Pconv = (P0/pression_inv)**(2/7)

shp_A_t = shp_A_t[::-1,:]
air_density_rev = pression_inv/(shp_A_t*R)
smoke_curtain = smoke_curtain[::-1,:] * air_density_rev

model_hgtsfc = ds_dyn['hgtsfc'][0].isel(grid_xt = j_idx, grid_yt = i_idx)
dz           = ds_dyn['delz'][0].isel(grid_xt = j_idx, grid_yt = i_idx)
dz           = dz*-1
alt_rev      = dz[::-1]

model_z_hgt  = alt_rev.cumsum(axis=0)+model_hgtsfc
model_z_hgt  = model_z_hgt.transpose()

# Plot the cross-section
levels_smoke = clevs_con_smoke
norm_smoke   = norm_con_smoke

x2d = np.matlib.repmat(shp_A_lon,65,1)
y2d = model_z_hgt/1000
y2d = y2d.transpose()

fig = plt.figure(figsize=(8,3))
ax=plt.axes()

im = ax.contourf(x2d,y2d,smoke_curtain,cmap=cmap_sfc_smoke,
                  levels=levels_smoke,norm=norm_smoke,zorder=0,extend='max')

ax.fill_between(shp_A_lon,model_hgtsfc/1000, color='black', alpha=1)
ax.set_ylabel('Height MLS [km]', fontsize=12)
ax.set_ylim([0.,10.])
ax.set_xlim([np.min(x2d),np.max(x2d)])

ax.set_title(rrfs_title, loc='left',fontsize=10)
ax.set_xlabel('Lon', fontsize=12)

im.cmap.set_over('purple')
cbar=plt.colorbar(im,ax=ax)
im.set_clim([min(levels_smoke),max(levels_smoke)])
cbar.set_label(r'Smoke [$\mu$g m$^{-3}$]', fontsize=12)

fname = plot_dir+'/'+'Smoke_xSection_'+'_'+validTime_str+'_UTC.png'
plt.savefig(fname, bbox_inches='tight', dpi=300)
plt.close()

