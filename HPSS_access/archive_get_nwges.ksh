##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:59:00
#PBS -j oe
#PBS -N output_rrfs_retro_det_nwges

set -x

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval 

module load hpss

version="v0.9.7"
export ARCHIVEDIR="/NCEPDEV/emc-meso/2year/emc.lam/rrfs_retro/${version}"
mkdir -p /lfs/f2/t2o/ptmp/emc/ptmp/emc.lam/rrfs/${version}/nwges
cd /lfs/f2/t2o/ptmp/emc/ptmp/emc.lam/rrfs/${version}/nwges

days=20240518

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

export RUN="rrfs"

  for onecyc in 18; do

    onerun=${RUN}.$year$month$day/${onecyc}
    echo "extract files from ${onerun}"
    hour=${onerun##*/}

    htar -xf $ARCHIVEDIR/$year/$month/$day/lbcs_ctrl_${year}${month}${day}${hour}.tar
    htar -xf $ARCHIVEDIR/$year/$month/$day/nwges_ctrl_${year}${month}${day}${hour}.tar
  done

dateval=`date`

echo "Completed archive at "$dateval 
