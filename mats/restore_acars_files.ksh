#!/bin/ksh --login

#SBATCH -J acars_retro_restore
##SBATCH --mail-user=eric.james@noaa.gov
#SBATCH --mail-type=FAIL
#SBATCH -A amb-verif
#SBATCH -n 1
#SBATCH -t 04:00:00
#SBATCH -p service
#SBATCH -D /home/role.amb-verif/acars_RR/ACARS_RETRO_DIR
##SBATCH -oe /home/role.amb-verif/acars_RR/ACARS_RETRO_DIR/restore_acars.log
#SBATCH -o /home/role.amb-verif/acars_RR/ACARS_RETRO_DIR/restore_acars.log

  module load hpss

  # Set dates of interest

  startDate=2024-07-20
  endDate=2024-07-31

  # Set destination directories
  export DEST_DIR=/home/role.amb-verif/acars_RR/ACARS_RETRO_DIR
  cd ${DEST_DIR}

  while [[ ${startDate} != ${endDate} ]] ;
  do
    echo "Grabbing acars for ${startDate}"
    year=$(date --date=$startDate '+%Y')
    month=$(date --date=$startDate '+%m')
    day=$(date --date=$startDate '+%d')
    hsi get /BMC/fdr/Permanent/${year}/${month}/${day}/data/acars/qc/netcdf/${year}${month}${day}0000.zip
    /bin/unzip ${year}${month}${day}0000.zip
    rm ${year}${month}${day}0000.zip
    startDate=$(date -I -d "$startDate + 1 day")
  done

exit 0
