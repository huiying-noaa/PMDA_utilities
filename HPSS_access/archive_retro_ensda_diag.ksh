##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:59:00
#PBS -j oe
#PBS -N output_rrfs_retro_ens_diag

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

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

export RUN="enkfrrfs"
export OUT=${OUTDIR}/log.archive.ensda_diag.${year}${month}${day}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval >> ${OUT} 2>&1
echo "Archiving RRFS retro output for ${year}${month}${day}" >> ${OUT}

/usr/local/bin/hsi mkdir -p $ARCHIVEDIR/$year/$month/$day >> ${OUT} 2>&1

cd ${COMOUT_BASEDIR}
for onecyc in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23; do

    onerun=enkfrrfs.$year$month$day/${onecyc}
    echo "Archive files from ${onerun}" >> ${OUT} 2>&1
    hour=${onecyc}

# diag files
    if [[ -e ${COMOUT_BASEDIR}/${onerun} ]];then
      echo "GSI diag files..." >> ${OUT} 2>&1
      cd ${COMOUT_BASEDIR}
      /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/diag_ens_$year$month$day$hour.tar  ${onerun}/*/diag*nc4* ${onerun}/*/*fits* ${onerun}/*/stdout*  >> ${OUT} 2>&1
    fi

# grib2 files
#    set -A YY `ls -d ${COMOUT_BASEDIR}/${onerun}/mem00*/*grib2*` >> ${OUT} 2>&1
#    postcount=${#YY[*]}
#    echo $postcount >> ${OUT} 2>&1
#    if [[ $postcount -gt 0 ]];then
#      echo "GRIB2 ensemble forecast..." >> ${OUT} 2>&1
#      cd ${COMOUT_BASEDIR}
#      /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/grib2_ens_$year$month$day$hour.tar ${onerun}/mem00*/*grib2* >> ${OUT} 2>&1
#    fi
#
  done

# log files
if [[ -e ${LOG_DIR}/enkfrrfs.$year$month$day ]];then
  echo "Log files..." >> ${OUT} 2>&1
  cd ${LOG_DIR}
  /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/logs_ens_$year$month$day.tar enkfrrfs.$year$month$day >> ${OUT} 2>&1
fi

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1

exit 0

