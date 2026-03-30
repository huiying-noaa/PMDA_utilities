##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:30:00
#PBS -j oe -o archive_retro_ensda_diag.out
#PBS -N hrrrak_smoke_transfer

set -x

export expname="rrfs"
export version="v0.9.7"
export retroname=""

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

days=20230612

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

export RUN="enkfrrfs"
export OUT=${OUTDIR}/log.archive.${expname}.ensda_diag.${year}${month}${day}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval >> ${OUT} 2>&1

echo "Archiving RRFS retro output for ${year}${month}${day}" >> ${OUT}

cd ${COMOUT_BASEDIR}
set -A XX `ls -d ${RUN}.$year$month$day/* | sort -r` >> ${OUT} 2>&1
runcount=${#XX[*]}

if [[ $runcount -gt 0 ]];then

  /usr/local/bin/hsi mkdir -p $ARCHIVEDIR/$year/$month/$day >> ${OUT} 2>&1

  for onerun in ${XX[*]};do

    echo "Archive files from ${onerun}" >> ${OUT} 2>&1
    hour=${onerun##*/}

# diag files
    set -A YY `ls -d ${COMOUT_BASEDIR}/${onerun}/mem00*/diag_conv*nc4.gz` >> ${OUT} 2>&1
    postcount=${#YY[*]}
    echo $postcount >> ${OUT} 2>&1
    if [[ $postcount -gt 0 ]];then
      echo "GSI diag files..." >> ${OUT} 2>&1
      cd ${COMOUT_BASEDIR}
      /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/diag_ens_$year$month$day$hour.tar  ${onerun}/*/diag*nc4* ${onerun}/*/*fits* ${onerun}/*/stdout*  >> ${OUT} 2>&1
    fi

# grib2 files
    set -A YY `ls -d ${COMOUT_BASEDIR}/${onerun}/mem00*/*grib2*` >> ${OUT} 2>&1
    postcount=${#YY[*]}
    echo $postcount >> ${OUT} 2>&1
    if [[ $postcount -gt 0 ]];then
      echo "GRIB2 ensemble forecast..." >> ${OUT} 2>&1
      cd ${COMOUT_BASEDIR}
      /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/grib2_ens_$year$month$day$hour.tar ${onerun}/mem00*/*grib2* >> ${OUT} 2>&1
    fi

  done
fi

# log files
if [[ -e ${LOG_DIR}/${RUN}.$year$month$day ]];then
  echo "Log files..." >> ${OUT} 2>&1
  /usr/local/bin/hsi mkdir -p $ARCHIVEDIR/$year/$month/$day >> ${OUT} 2>&1
  cd ${LOG_DIR}
  /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/logs_ens_$year$month$day.tar ${RUN}.$year$month$day >> ${OUT} 2>&1
fi

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1

exit 0

