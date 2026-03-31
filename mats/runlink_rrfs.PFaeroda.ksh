#!/bin/ksh -v

set -x

#Note: do not use dash in expname

expname=RRFSret_Jul2024_PFaeroda
runpath=/mnt/lfs6/BMC/wrfruc/hluo/mats_eva/PFaeroda


cd $HOME/RR_uaverif/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ruc_madis_surface/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ceiling/retro_data
ln -s ${runpath} ${expname}

cd $HOME/visibility/retro_data
ln -s ${runpath} ${expname}

cd $HOME/surfrad3/retro
ln -s ${runpath} ${expname}

cd $HOME/acars_RR/retro_runs
ln -s ${runpath} ${expname}

ls -l $HOME/RR_uaverif/RR_retro/${expname}
ls -l $HOME/ruc_madis_surface/RR_retro/${expname}
ls -l $HOME/ceiling/retro_data/${expname}
ls -l $HOME/visibility/retro_data/${expname}
ls -l $HOME/surfrad3/retro/${expname}
ls -l $HOME/acars_RR/retro_runs/${expname}
