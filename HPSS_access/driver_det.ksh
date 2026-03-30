#!/bin/bash

set -x

DAYS="20240724"
NAMES="AODDA AeroDA PMDA3 ctrl"
#qsub -v  DAYSIN=${DAYS},CYCSIN="00 01 02 03 04 05" archive_retro_det_nwges.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="06 07 08 09 10 11" archive_retro_det_nwges.ksh 
#qsub -v  DAYSIN=${DAYS},CYCSIN="12 13 14 15 16 17" archive_retro_det_nwges.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="18 19 20 21 22 23" archive_retro_det_nwges.ksh

#qsub -v  DAYSIN=${DAYS},CYCSIN="00" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="01 02 03 04 05" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="06" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="07 08 09 10 11" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="12" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="13 14 15 16 17" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="18" archive_retro_det_grib.ksh
#qsub -v  DAYSIN=${DAYS},CYCSIN="19 20 21 22 23" archive_retro_det_grib.ksh

#qsub -v  DAYSIN=${DAYS},CYCSIN="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23" archive_retro_det_diag.ksh
sbatch --export=ALL, NAMEIN=${NAMES}, DAYSIN=${DAYS} archive_retro_det_logs.ksh
#qsub -v  NAMEIN=${NAMES}, DAYSIN=${DAYS} archive_retro_det_logs.ksh
#qsub -v  DAYSIN=${DAYS} archive_retro_det_raveintp.ksh

exit 0
