##!/bin/bash

#PBS -A RRFS-DEV
#PBS -q dev_transfer
#PBS -l select=1:ncpus=1:mem=2G
#PBS -l walltime=5:59:00
#PBS -j oe
#PBS -N output_rrfs_retro_ensfcst_grib2

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
cycs=${CYCSIN}
mems=${MEMSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

#----------------------------------------
dateval=`date`
echo "Started archive at "$dateval
echo "Archiving RRFS retro output for ${year}${month}${day}"

/usr/local/bin/hsi mkdir -p $ARCHIVEDIR/$year/$month/$day

cd ${COMOUT_BASEDIR}

for onecyc in ${cycs} ; do

  for imem in ${mems}
  do
    memchar=mem00${imem}
    onerun=refs.$year$month$day/${onecyc}
    echo "Archive files from ${onerun}"
    hour=${onecyc}
    OUT=${OUTDIR}/log.archive.ensfcst.grib2.${year}${month}${day}${hour}.${memchar}

# grib2 files
    YY=()
    YY=(`ls -d ${COMOUT_BASEDIR}/${onerun}/${memchar}/*grib2*`) >> ${OUT} 2>&1
    postcount=${#YY[@]}
    echo $postcount >> ${OUT} 2>&1
    if [[ $postcount -gt 0 ]];then
      echo "GRIB2 ensemble forecast forecast..." >> ${OUT} 2>&1
      cd ${COMOUT_BASEDIR}
      /usr/local/bin/htar -chvf $ARCHIVEDIR/$year/$month/$day/grib2_enfcst_$year$month$day$hour.${memchar}.tar ${onerun}/${memchar}/*grib2* >> ${OUT} 2>&1
    fi
  done
done

dateval=`date`
echo "Completed archive at "$dateval >> ${OUT} 2>&1
exit 0

