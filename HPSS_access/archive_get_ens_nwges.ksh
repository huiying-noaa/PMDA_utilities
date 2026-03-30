##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:59:00
#PBS -j oe
#PBS -N output_rrfs_retro_ens_nwges

set -x

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval 

module load hpss

version="v0.9.7"
export ARCHIVEDIR="/NCEPDEV/emc-meso/2year/emc.lam/rrfs_retro/${version}"
mkdir -p /lfs/f2/t2o/ptmp/emc/ptmp/emc.lam/rrfs/${version}/nwges
cd /lfs/f2/t2o/ptmp/emc/ptmp/emc.lam/rrfs/${version}/nwges

days=${DAYSIN}
HH=${CYCSIN}
mems=${MEMSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

for imem in ${mems}
do
    memchar=mem00${imem}
    htar -xf $ARCHIVEDIR/$year/$month/$day/nwges_ens_$year$month$day${HH}_${memchar}_${SAVETYPE}.tar
    htar -xf $ARCHIVEDIR/$year/$month/$day/lbcs_ens_$year$month$day${HH}_${memchar}_${SAVETYPE}.tar
done

echo "Completed archive at "$dateval 
