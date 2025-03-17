#!/bin/ksh 

#set -ux

airnow_in=/scratch2/BMC/amb-verif/hluo/pmobs/airnow
airnow_out=/scratch2/BMC/amb-verif/hluo/pmobs/airnowioda
IODA_CONVERTER=/scratch2/BMC/amb-verif/hluo/pmobs
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
export sitefile=True

#if [ ! -s ${airnow_in}/HourlyData_$1.dat ]; then
# wget https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/$YYYY/$YYYY$MM$DD/HourlyData_$1.dat -O ${airnow_in}/HourlyData_$1.dat
#fi
#if [ ! -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat ]; then
# wget https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/$YYYY/$YYYY$MM$DD/monitoring_site_locations.dat \
# -O ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat
#fi
if [ ! -s ${airnow_in}/HourlyData_$1.dat ]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! missing file HourlyData_$1.dat !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
else
if [ ! -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat ]; then
  #python3 -u  $IODA_CONVERTER/airnow2ioda-nc-RRFSSD-blrm.py -i ${airnow_in}/HourlyData_$1.dat -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat -b IODA_hourlyPM25baseline_88101_07_25rms.nc -o airnow-$1-blrm-v1.nc
  echo "$1 used default site file" 
  python3 -u  $IODA_CONVERTER/airnow2ioda-nc-RRFSSD-blprep.py -i ${airnow_in}/HourlyData_$1.dat -s ${airnow_in}/monitoring_site_locations_20240930.dat -o ${airnow_out}/airnow-$1-blprep-v1.nc
else
  python3 -u  $IODA_CONVERTER/airnow2ioda-nc-RRFSSD-blprep.py -i ${airnow_in}/HourlyData_$1.dat -s ${airnow_in}/monitoring_site_locations_$YYYY$MM$DD.dat -o ${airnow_out}/airnow-$1-blprep-v1.nc
fi
fi
