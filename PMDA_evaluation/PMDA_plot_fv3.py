import netCDF4 as nc
import xarray as xa
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors
import cartopy.crs as ccrs
import cartopy.feature as cf
import sys
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import dateutil.relativedelta, dateutil.parser
import io
import time,os,sys,multiprocessing
import multiprocessing.pool
from scipy import ndimage
import pyproj
import argparse
import cartopy
from PIL import Image
from matplotlib.gridspec import GridSpec
from matplotlib.colors import CenteredNorm

print('loaded!')

## Input data
homedir = '/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/PMDA2/'
infile_grd = homedir+'stmp/2024073001/FV3JEDI_prod/00/INPUT/fv3_grid_spec'
checkt='2024073001'
corefilelist = ['nwges/2024073000/fcst_fv3lam/RESTART/20240730.010000.fv_core.res.tile1.nc','stmp/2024073001/FV3JEDI_prod/00/INPUT/fv_core.res.tile1.nc','stmp/2024073001/FV3JEDI_prod/00/PM25.fv_core.res.nc','stmp/2024073001/fcst_fv3lam/INPUT/fv_core.res.tile1.nc'] # restart from last hour fcst, after met GSI, aerosol DA output, after aerosol DA and non-var cloud

varlist = ['W','DZ','liq_wat','ice_wat','rainwat','snowwat','graupel','water_nc','rain_nc','o3mr','liq_aero','sgs_tke']
varincorefile = [1,1,0,0,0,0,0,0,0,0,0,0]
#varlist = ['v','va','smoke','dust','coarsepm','sphum','rainwat','u','T','delp','phis','ua']
#varincorefile = [1,1,0,0,0,0,0,1,1,1,1,1]

## Plot control and prep
cartopy.config['data_dir'] = "/mnt/lfs6/BMC/wrfruc/hluo/other_eva/natural_earth_data"
lonlimits = (-129,-105)
latlimits = (23,55)
pos=[[0,0.55,0.3,0.4],[0.31,0.55,0.3,0.4],[0.62,0.55,0.3,0.4],[0,0.05,0.3,0.4],[0.31,0.05,0.3,0.4],[0.62,0.05,0.3,0.4]]
grd = xa.open_dataset(infile_grd)

## Plot per var
for varid in range(2,len(varlist)):#range(len(varlist)):
    var=varlist[varid]
    plot_fn = homedir+'DAcheckk_'+var+'_'+checkt+'.png'     
    if varincorefile[varid]==0:
        filelist=[item.replace('core','tracer') for item in corefilelist]
    else:
        filelist=corefilelist
    filelist=[homedir + item for item in filelist]

    Base = xa.open_dataset(filelist[0])
    MetDA = xa.open_dataset(filelist[1])
    AeroDA = xa.open_dataset(filelist[2]) 
    Final = xa.open_dataset(filelist[3])
    
    ## Layers and grid
    vard=Base[var].values.shape
    if len(vard)==3:
        print('Plotting 2D variable '+var+'...')
    else:
        print('Plotting layer 65 (surface) and layer 55 of variable '+var+'...')
    if 1092 in vard:
        X = grd.grid_lont
        Y = grd.grid_latt
    elif 1093 in vard:
        X = grd.grid_lon
        Y = grd.grid_lat
    else:
        print('Error: Wrong variable dimension! Skipping...')
        continue
    
    fig, [[ax1, ax2, ax3], [ax4, ax5, ax6]] = plt.subplots(nrows=2, ncols=3, subplot_kw={'projection': ccrs.PlateCarree()},sharex=True,sharey=True,figsize=(25/2*0.8,10*0.8))

    ## Bottom layer for 3D/2D
    if 1==1:
        if len(vard)==3:
            layerid=0
            plotvar=MetDA[var][0,:,:].values-Base[var][0,:,:].values
        else:
            layerid=64
            plotvar=MetDA[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
        ax1.add_feature(cf.BORDERS,zorder=10) 
        ax1.add_feature(cf.COASTLINE,zorder=10)
        ax1.add_feature(cf.STATES,zorder=10)
        p1=ax1.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm')
        ax1.set_title(f'\n{var} L{layerid+1}, MetDA-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
        ax1.set_xlim(lonlimits)
        ax1.set_ylim(latlimits)
        ax1.set_position(pos[0])
        cbar_ax=fig.add_axes([0.28,0.55,0.01,0.4])
        cbar=plt.colorbar(p1,cax=cbar_ax,extend='both')
    else:
        print(var+' is not in MetDA!')
    
    
    
    #print(AeroDA[var].values.shape)
    #print(Base[var].values.shape)
    #print(AeroDA[var])
    #print(Base[var]) 
    try:
        if len(vard)==3:
            layerid=0
            plotvar=AeroDA[var][0,:,:].values-Base[var][0,:,:].values
        else:
            layerid=64
            plotvar=AeroDA[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
        ax2.add_feature(cf.BORDERS,zorder=10) 
        ax2.add_feature(cf.COASTLINE,zorder=10)
        ax2.add_feature(cf.STATES,zorder=10)
        p2=ax2.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm', shading='nearest')
        ax2.set_title(f'\n{var} L{layerid+1}, AeroDA-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
        ax2.set_xlim(lonlimits)
        ax2.set_ylim(latlimits)
        ax2.set_position(pos[1])
        cbar_ax=fig.add_axes([0.59,0.55,0.01,0.4])
        cbar=plt.colorbar(p2,cax=cbar_ax,extend='both')
    except:
        print(var+' is not in AeroDA!')
        


    try:
        if len(vard)==3:
            layerid=0
            plotvar=Final[var][0,:,:].values-Base[var][0,:,:].values
        else:
            layerid=64
            plotvar=Final[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
        ax3.add_feature(cf.BORDERS,zorder=10) 
        ax3.add_feature(cf.COASTLINE,zorder=10)
        ax3.add_feature(cf.STATES,zorder=10)
        p3=ax3.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm', shading='nearest')
        ax3.set_title(f'\n{var} L{layerid+1}, Final-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
        ax3.set_xlim(lonlimits)
        ax3.set_ylim(latlimits)
        ax3.set_position(pos[2])
        cbar_ax=fig.add_axes([0.9,0.55,0.01,0.4])
        cbar=plt.colorbar(p3,cax=cbar_ax,extend='both')
    except:
        print(var+' is not in Final!')
    
    ## Layer 55 (python layer 54) for 3D
    
    if len(vard)==4:
        try:
            layerid=54
            plotvar=MetDA[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
            ax4.add_feature(cf.BORDERS,zorder=10)
            ax4.add_feature(cf.COASTLINE,zorder=10)
            ax4.add_feature(cf.STATES,zorder=10)
            p4=ax4.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm', shading='nearest')
            ax4.set_title(f'\n{var} L{layerid+1}, MetDA-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
            ax4.set_xlim(lonlimits)
            ax4.set_ylim(latlimits)
            ax4.set_position(pos[3])
            cbar_ax=fig.add_axes([0.28,0.05,0.01,0.4])
            cbar=plt.colorbar(p4,cax=cbar_ax,extend='both')
        except:
            print(var+' is not in MetDA!')


        try:
            layerid=54
            plotvar=AeroDA[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
            ax5.add_feature(cf.BORDERS,zorder=10) 
            ax5.add_feature(cf.COASTLINE,zorder=10)
            ax5.add_feature(cf.STATES,zorder=10)
            p5=ax5.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm', shading='nearest')
            ax5.set_title(f'\n{var} L{layerid+1}, AeroDA-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
            ax5.set_xlim(lonlimits)
            ax5.set_ylim(latlimits)
            ax5.set_position(pos[4])
            cbar_ax=fig.add_axes([0.59,0.05,0.01,0.4])
            cbar=plt.colorbar(p5,cax=cbar_ax,extend='both')
        except:
            print(var+' is not in AeroDA!')
        
        
        
        try:
            layerid=54
            plotvar=Final[var][0,layerid,:,:].values-Base[var][0,layerid,:,:].values
            ax6.add_feature(cf.BORDERS,zorder=10) 
            ax6.add_feature(cf.COASTLINE,zorder=10)
            ax6.add_feature(cf.STATES,zorder=10)
            p6=ax6.pcolormesh(X[:1090,:1820],Y[:1090,:1820],plotvar[:1090,:1820],norm=CenteredNorm(),cmap='coolwarm', shading='nearest')
            ax6.set_title(f'\n{var} L{layerid+1}, Final-Base\n mn,mx,mean={np.min(plotvar):.2}, {np.max(plotvar):.2}, {np.mean(plotvar):.2}\n',fontsize=10)
            ax6.set_xlim(lonlimits)
            ax6.set_ylim(latlimits)
            ax6.set_position(pos[5])
            cbar_ax=fig.add_axes([0.9,0.05,0.01,0.4])
            cbar=plt.colorbar(p6,cax=cbar_ax,extend='both')
        except:                                                                                                                                                                                                         
            print(var+' is not in Final!')
        
    
    
    plt.savefig(plot_fn,dpi=300, bbox_inches='tight')
    print(f'Output plot saved as {plot_fn}')
    
    
