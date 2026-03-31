#!/bin/ksh -v

set -x

#Note: do not use dash in expname


#expname=RRFSret_IOP1_orgErr
#runpath=/lfs4/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/RTMA_IOP1_orgErr
#expname=RRFSret_IOP1_tunedErr
#runpath=/lfs4/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/RTMA_IOP1_tunedErr

#expname=RRFSret_July2023_v091              # CONUS 3km
#expname=RRFS_NA_3kmret_July2023_v091        # NA 3km
#runpath=/mnt/lfs4/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/July2023_v091
#expname=RRFS_NA_3kmret_July2023_v094        # NA 3km
#runpath=/mnt/lfs4/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/July2023_v094

#expname=RRFS_NA_3kmret_May2024_v114        # NA 3km
#runpath=/mnt/lfs5/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/May2024_v114

#expname=RRFS_NA_3kmret_Jan2024_v113        # NA 3km
#runpath=/mnt/lfs5/BMC/wrfruc/Ruifang.Li/NCO_dirs_save/Jan2024_v113

expname=RRFSret_July2024_PF_ctrl
runpath=/lfs5/BMC/wrfruc/bjallen/JEDI-AOD/RRFS_ParkFire_ctrl_1day/v0.7.7/ptmp/prod/${expname}


cd $HOME/RR_uaverif/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ruc_madis_surface/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ceiling/beta/retro_data
ln -s ${runpath} ${expname}


ls -l $HOME/RR_uaverif/RR_retro/${expname}
ls -l $HOME/ruc_madis_surface/RR_retro/${expname}
ls -l $HOME/ceiling/beta/retro_data/${expname}

