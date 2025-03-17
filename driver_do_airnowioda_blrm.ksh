#!/bin/ksh
#source /scratch2/BMC/wrfruc/hwang/fire2/DA_C775/T1/fv3-jedi/test/ioda_pm2p5/modulefile.skylab6.rocky8
export PYTHONPATH="${PYTHONPATH}://scratch2/BMC/wrfruc/rli/JEDI/ioda-bundle/iodaconv/src:/scratch2/BMC/wrfruc/rli/JEDI/ioda-bundle/build/lib/python3.10"
export sitefile=True


for yy in 2021 2024; do
mm=09

for dd in $(seq -w 01 31); do
for hh in $(seq -w 00 23); do
/usr/bin/ksh /scratch2/BMC/amb-verif/hluo/pmobs/convert-airnow-blrm.ksh ${yy}${mm}${dd}${hh}


done
done
done
