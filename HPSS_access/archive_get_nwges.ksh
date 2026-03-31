#!/bin/sh
  
#SBATCH -A wrfruc
#SBATCH -t 06:00:00
#SBATCH --ntasks=1
#SBATCH --partition=u1-service
set -x

#----------------------------------------
dateval=`date`
echo "Started archive retrieval at "$dateval 

#module load hpss

version=${NAMEIN}
export ARCHIVEDIR="/5year/BMC/wrfruc/hluo/PF_FV3_Jet/${version}"
mkdir -p /scratch4/BMC/wrfruc/hluo/PF_FV3/${version}/monet
cd /scratch4/BMC/wrfruc/hluo/PF_FV3/${version}/monet

days=${DAYSIN}
cycs=${CYCSIN}

export day=${days:6:2}
export year=${days:0:4}
export month=${days:4:2}

export RUN="rrfs"

  for onecyc in ${cycs}; do

    onerun=${RUN}.$year$month$day/${onecyc}
    echo "extract files from ${onerun}"
    hour=${onerun##*/}

    htar -xf $ARCHIVEDIR/$year/$month/$day/monet_${version}_${year}${month}${day}${hour}.tar
  done

dateval=`date`

echo "Completed at "$dateval 
