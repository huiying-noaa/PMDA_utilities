#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 06:00:00
#SBATCH --ntasks=1
#SBATCH --partition=service



set -x

version=${NAMEIN}
export BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}"
export LOG_DIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}/ptmp/logs"
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
OUT=${OUTDIR}/log.archive.det.logs.${year}${month}${day}
# log files
if [[ -e ${LOG_DIR}/rrfs.$year$month$day ]]; then
  echo "Log files..." >> ${OUT} 2>&1
  cd ${LOG_DIR}
  echo "begin to htar logs"
  htar -chvf $ARCHIVEDIR/$year/$month/$day/logs_${version}_$year$month$day.tar rrfs.$year$month$day >> ${OUT} 2>&1
fi

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1
exit 0

