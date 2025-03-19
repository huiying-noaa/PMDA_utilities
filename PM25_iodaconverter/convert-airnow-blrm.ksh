#!/bin/ksh 

#set -ux

export sitefile=True

airnow_in="test" #/scratch2/BMC/amb-verif/hluo/pmobs/airnow
airnow_out="testout" #/scratch2/BMC/amb-verif/hluo/pmobs/airnowioda
IODA_CONVERTER="." #/scratch2/BMC/amb-verif/hluo/pmobs
mkdir -p ${airnow_in}
mkdir -p ${airnow_out}

if [ -z $IODA_CONVERTER ]; then
 echo "IODA_CONVERTER environment is not set "
 exit 1
fi
 
if [ $# -ne 1 ]; then
 echo "need YYYYMMDDHH"
 exit 1
fi 
YYYY=$(echo $1|cut -c1-4)
MM=$(echo $1|cut -c5-6)
DD=$(echo $1|cut -c7-8)

# optional data downloading
#if [ ! -s ${airnow_in}/HourlyData_$1.dat ]; then
# wget https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/$YYYY/$YYYY$MM$DD/HourlyData_$1.dat -O ${airnow_in}/HourlyData_$1.dat
#fi
#if [ ! -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat ]; then
# wget https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/$YYYY/$YYYY$MM$DD/monitoring_site_locations.dat \
# -O ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat
#fi

python3 -u  $IODA_CONVERTER/airnow2ioda-nc-RRFSSD-blrm.py -i ${airnow_in}/HourlyData_$1.dat -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat -b ${airnow_in}/IODA_hourlyPM25baseline_88101_${MM}_25rms.nc -o ${airnow_out}/airnow-$1-blrm-v1.nc
