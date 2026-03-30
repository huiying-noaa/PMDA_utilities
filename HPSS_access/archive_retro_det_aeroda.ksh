#!/bin/sh
  
#SBATCH -A wrfruc
#SBATCH -t 06:00:00
#SBATCH --ntasks=1
#SBATCH --partition=service

set -x

version=${NAMEIN}
export BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}"
export NWGES_BASEDIR="/mnt/lfs6/BMC/wrfruc/hluo/workflow/AOD_DA/${version}/stmp"
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
# nwges: RESTART/ and INPUT/ and lbcs/
for HH in ${cycs}
do
  hour=${HH}
  OUT=${OUTDIR}/log.archive.det.aeroda.${year}${month}${day}${hour}
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDIAOD_spinup ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/AOD_${version}_spinup_$year$month$day$HH.tar $year$month$day$HH/FV3JEDIAOD_spinup/00/*.nc  $year$month$day$HH/FV3JEDIAOD_spinup/00/LOG/LOG_VAR_AOD_SMOKE >> ${OUT} 2>&1
  fi
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDIAOD_prod ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/AOD_${version}_prod_$year$month$day$HH.tar $year$month$day$HH/FV3JEDIAOD_prod/00/*.nc  $year$month$day$HH/FV3JEDIAOD_prod/00/LOG/LOG_VAR_AOD_SMOKE >> ${OUT} 2>&1                                                                    
  fi
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDIPM25_spinup ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/PM25_${version}_spinup_$year$month$day$HH.tar $year$month$day$HH/FV3JEDIPM25_spinup/00/*.nc  $year$month$day$HH/FV3JEDIPM25_spinup/00/LOG/*3dvar >> ${OUT} 2>&1
  fi
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDI_spinup ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/PM25_${version}_spinup_$year$month$day$HH.tar $year$month$day$HH/FV3JEDI_spinup/00/*.nc $year$month$day$HH/FV3JEDI_spinup/00/LOG/*3dvar >> ${OUT} 2>&1
  fi
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDIPM25_prod ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/PM25_${version}_prod_$year$month$day$HH.tar $year$month$day$HH/FV3JEDIPM25_prod/00/*.nc $year$month$day$HH/FV3JEDIPM25_prod/00/LOG/*3dvar >> ${OUT} 2>&1
  fi
  if [[  -e ${NWGES_BASEDIR}/$year$month$day$HH/FV3JEDI_prod ]]; then
    echo "Initial conditions (spinup) at ${year}${month}${day}${HH}..." >> ${OUT} 2>&1
    cd ${NWGES_BASEDIR}
    htar -chvf $ARCHIVEDIR/$year/$month/$day/PM25_${version}_prod_$year$month$day$HH.tar $year$month$day$HH/FV3JEDI_prod/00/*.nc $year$month$day$HH/FV3JEDI_prod/00/LOG/*3dvar >> ${OUT} 2>&1                                                                      
  fi

done

dateval=`date`

echo "Completed archive at "$dateval >> ${OUT} 2>&1
exit 0

