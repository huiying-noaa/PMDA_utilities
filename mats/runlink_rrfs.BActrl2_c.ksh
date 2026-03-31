#!/bin/ksh -v

set -x

#Note: do not use dash in expname

expname=RRFSret_Jul2024_BActrl2_c
runpath=/mnt/lfs6/BMC/wrfruc/hluo/mats_eva/BActrl2_c


cd $HOME/RR_uaverif/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ruc_madis_surface/RR_retro
ln -s ${runpath} ${expname}

cd $HOME/ceiling/beta/retro_data
ln -s ${runpath} ${expname}


ls -l $HOME/RR_uaverif/RR_retro/${expname}
ls -l $HOME/ruc_madis_surface/RR_retro/${expname}
ls -l $HOME/ceiling/beta/retro_data/${expname}

