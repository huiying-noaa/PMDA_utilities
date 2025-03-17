#!/bin/ksh
#source /scratch2/BMC/wrfruc/hwang/fire2/DA_C775/T1/fv3-jedi/test/ioda_pm2p5/modulefile.skylab6.rocky8
export PYTHONPATH="${PYTHONPATH}://scratch2/BMC/wrfruc/rli/JEDI/ioda-bundle/iodaconv/src:/scratch2/BMC/wrfruc/rli/JEDI/ioda-bundle/build/lib/python3.10"
export sitefile=True


yy=2024
mm=07
dd=20
hh=00
/usr/bin/ksh convert-airnow-blrm.ksh ${yy}${mm}${dd}${hh}


