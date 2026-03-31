#!/bin/ksh -v

set -x

expname=RRFSret_Jul2024_PFpmda2
start_hour=1721779200  #00 24 07 2024
end_hour=1722384000    #00 31 07 2024

# 1: reprocess each fcst
# 0: not reprocess if current fcst is processed, it search database, if fcst is processed, then go to next fcst hour
# for(my $valid_time=$startSecs;$valid_time<=$endSecs;$valid_time+=1*3600) 
# foreach my $fcst_len (@fcst_lens) 


#cd $HOME/ruc_madis_surface
#./retro2.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/hluo/infs_${expname} 2>&1 &  # 1: reprocess, 0: do not reprocess

cd $HOME/RR_uaverif
./process_retro4.pl ${expname} ${start_hour} ${end_hour} FW-to-Wobus 1  > /lfs5/BMC/amb-verif/hluo/infu_${expname} 2>&1 &

cd $HOME/ceiling
ceil_driver_retro.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/hluo/infc_${expname} 2>&1 &


# use /misc/whome/role.amb-verif/utilities/time70.pl
# to find the experiment period.



