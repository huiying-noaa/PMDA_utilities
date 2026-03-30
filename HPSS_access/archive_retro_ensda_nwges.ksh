##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:59:00
#PBS -j oe
#PBS -N output_rrfs_retro_ens_nwges

set -x

version="v0.9.7"
export BASEDIR="/lfs/f2/t2o/ptmp/emc/stmp/emc.lam/rrfs/${version}"
export COMOUT_BASEDIR="/lfs/h2/emc/ptmp/emc.lam/rrfs/${version}/prod"
export LOG_DIR="/lfs/h2/emc/ptmp/emc.lam/rrfs/${version}/logs"
export NWGES_BASEDIR="/lfs/f2/t2o/ptmp/emc/ptmp/emc.lam/rrfs/${version}/nwges"
#export BASEDIR="/lfs/h3/emc/rrfstemp/rrfs/${version}"
#export COMOUT_BASEDIR="/lfs/h3/emc/rrfstemp/rrfs/${version}/prod"
#export LOG_DIR="/lfs/h3/emc/rrfstemp/rrfs/${version}/logs"
#export NWGES_BASEDIR="/lfs/h3/emc/rrfstemp/rrfs/${version}/nwges"
export OUTDIR=${BASEDIR}

export ARCHIVEDIR="/NCEPDEV/emc-meso/2year/emc.lam/rrfs_retro/${version}"

days=${DAYSIN}
HH=${CYCSIN}
mems=${MEMSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

export OUT=${OUTDIR}/log.archive.ensda_nwges.${year}${month}${day}${HH}.${SAVETYPE}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval >> ${OUT} 2>&1

echo "Archiving RRFS retro output for ${year}${month}${day}" >> ${OUT}
/usr/local/bin/hsi mkdir -p $ARCHIVEDIR/$year/$month/$day >> ${OUT} 2>&1

for imem in ${mems}
do 
    memchar=mem00${imem}
    if [[ -e ${NWGES_BASEDIR}/$year$month$day$HH/${memchar}/fcst_fv3lam ]] ;then
      echo "Initial conditions at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
      cd ${NWGES_BASEDIR}
      htar -chvf $ARCHIVEDIR/$year/$month/$day/nwges_ens_$year$month$day${HH}_${memchar}_${SAVETYPE}.tar $year$month$day${HH}/${memchar}/fcst_fv3lam >> ${OUT} 2>&1
    fi
done

for imem in ${mems}
do 
    memchar=mem00${imem}
    if [[ -e ${NWGES_BASEDIR}/$year$month$day$HH/${memchar}/lbcs ]] ;then
      echo "Initial conditions at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
      cd ${NWGES_BASEDIR}
      htar -chvf $ARCHIVEDIR/$year/$month/$day/lbcs_ens_$year$month$day${HH}_${memchar}_${SAVETYPE}.tar $year$month$day${HH}/${memchar}/lbcs >> ${OUT} 2>&1
    fi
done

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1

exit 0

