#!/bin/bash

set -x

DAYS="20230615"
qsub -v  DAYSIN=${DAYS},CYCSIN="00",MEMSIN="01" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",MEMSIN="02" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",MEMSIN="03" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",MEMSIN="04" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",MEMSIN="05" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",MEMSIN="01" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",MEMSIN="02" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",MEMSIN="03" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",MEMSIN="04" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",MEMSIN="05" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",MEMSIN="01" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",MEMSIN="02" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",MEMSIN="03" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",MEMSIN="04" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",MEMSIN="05" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",MEMSIN="01" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",MEMSIN="02" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",MEMSIN="03" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",MEMSIN="04" archive_retro_ensfcst_grib.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",MEMSIN="05" archive_retro_ensfcst_grib.ksh

exit 0
