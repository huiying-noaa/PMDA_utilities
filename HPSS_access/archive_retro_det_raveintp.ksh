#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 06:00:00
#SBATCH --ntasks=1
#SBATCH --partition=service

set -x

version=${NAMEIN}
export BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}"
export NWGES_BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}/nwges"
export OUTDIR=${BASEDIR}

export ARCHIVEDIR="/5year/BMC/wrfruc/hluo/PF_FV3_Jet/${version}"

days=${DAYSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval
echo "Archiving RRFS retro output for ${year}${month}${day}"

hsi mkdir -p $ARCHIVEDIR/$year/$month/$day
OUT=${OUTDIR}/log.archive.det.rave.${year}${month}${day}

    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/nwges_${version}_raveintp_$year$month$day.tar ${NWGES_BASEDIR}/RAVE_INTP/SMOKE_RRFS_data_$year$month$day??00.nc  >> ${OUT} 2>&1

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1
exit 0

