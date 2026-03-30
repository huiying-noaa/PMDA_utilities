#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 06:00:00
#SBATCH --ntasks=1
#SBATCH --partition=service

set -x

version=${NAMEIN}
export BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}"
export COMOUT_BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}/ptmp/prod"
export OUTDIR=${BASEDIR}

export ARCHIVEDIR="/5year/BMC/wrfruc/hluo/PF_FV3_Jet/${version}" 

days=${DAYSIN}
cycs=${CYCSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval

echo "Archiving RRFS retro output for ${year}${month}${day}"

hsi mkdir -p $ARCHIVEDIR/$year/$month/$day

cd ${COMOUT_BASEDIR}

for onecyc in ${cycs}; do

    onerun=rrfs.$year$month$day/${onecyc}
    echo "Archive files from ${onerun}"
    hour=${onecyc}
    OUT=${OUTDIR}/log.archive.det.diag.${year}${month}${day}${hour}
    # deterministic diag files
    if [[ -e ${COMOUT_BASEDIR}/${onerun}/diag_conv_t_ges.$year$month$day$hour.nc4.gz ]];then
      echo "GSI diag files..." >> ${OUT} 2>&1
      cd ${COMOUT_BASEDIR}
      htar -chvf $ARCHIVEDIR/$year/$month/$day/diag_${version}_$year$month$day$hour.tar ${onerun}/diag*nc4*  ${onerun}/stdout*   ${onerun}/*fits* ${onerun}/*txt ${onerun}/OUTPUT* ${onerun}/*satbias* >> ${OUT} 2>&1
    fi

done

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1
exit 0

