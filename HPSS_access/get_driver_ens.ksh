#!/bin/bash

set -x

DAYS="20240518"

qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="A",MEMSIN="01 02 03 04 05" archive_get_ens_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="B",MEMSIN="06 07 08 09 10 11 12 13 14 15 16 17 18" archive_get_ens_nwges.ksh
qsub -v  DAYSIN=${DAYS},CYCSIN="23",SAVETYPE="C",MEMSIN="19 20 21 22 23 24 25 26 27 28 29 30" archive_get_ens_nwges.ksh

exit 0
