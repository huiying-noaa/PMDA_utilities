#!/bin/bash

set -x

DAYS="20240526"
qsub -v  DAYSIN=${DAYS},CYCSIN="00",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",SAVETYPE="B",MEMSIN="06 07 08 09 10 11 12 13 14 15 16 17 18" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="00",SAVETYPE="C",MEMSIN="19 20 21 22 23 24 25 26 27 28 29 30" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="06",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_retro_ensda_nwges.ksh

qsub -v  DAYSIN=${DAYS},CYCSIN="12",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",SAVETYPE="B",MEMSIN="06 07 08 09 10 11 12 13 14 15 16 17 18" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="12",SAVETYPE="C",MEMSIN="19 20 21 22 23 24 25 26 27 28 29 30" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="18",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_retro_ensda_nwges.ksh

qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="B",MEMSIN="06 07 08 09 10 11 12 13 14 15 16 17 18" archive_retro_ensda_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="C",MEMSIN="19 20 21 22 23 24 25 26 27 28 29 30" archive_retro_ensda_nwges.ksh

qsub -v  DAYSIN=${DAYS} archive_retro_ensda_diag.ksh

exit 0
