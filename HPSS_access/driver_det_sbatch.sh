#!/bin/bash
#SBATCH --job-name=archive_logs
#SBATCH --output=archive_%j.log
#SBATCH --ntasks=1
#SBATCH --time=01:00:00

#DAYS="20240723"
#NAMES="ctrl"

#DAYS="20240724 20240725 20240726 20240727 20240728 20240729 20240730"
DAYS="20240728 20240729 20240730"
#NAMES="AeroDA PMDA3"                                                                                                                                                                               
#CYCS="00 01"

NAMES="AODDA AeroDA PMDA3 ctrl"
CYCS="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"


for DAY in $DAYS; do
    # Loop through each name
    for NAME in $NAMES; do
        echo "Submitting jobs for NAME=$NAME and DAY=$DAY"
        # Launch sbatch and pass the single values to the environment
        for CYC in $CYCS; do
          echo "Submitting jobs for HOUR=$CYC"
          sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}",CYCSIN="${CYC}" archive_retro_det_monet.ksh
          #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}",CYCSIN="${CYC}" archive_retro_det_aeroda.ksh 
          #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}",CYCSIN="${CYC}" archive_retro_det_nwges.ksh     
          #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}",CYCSIN="${CYC}" archive_retro_det_diag.ksh
          #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}",CYCSIN="${CYC}" archive_retro_det_grib.ksh
        done
        #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}" archive_retro_det_raveintp.ksh
        #sbatch --export=ALL,NAMEIN="${NAME}",DAYSIN="${DAY}" archive_retro_det_logs.ksh
    done
done

