#!/bin/ksh -v

set -x


#expname=RRFSret_July2023_v091                       # CONUS 3km
#expname=RRFSret_IOP1_orgErr
#expname=RRFSret_IOP1_tunedErr

#expname=RRFS_NA_3kmret_July2023_v091                 # NA 3km
#expname=RRFS_NA_3kmret_July2023_v094                 # NA 3km


# 202405 0109--0823
#expname=RRFS_NA_3kmret_May2024_v114                 # NA 3km
#start_hour=1714521600   # 050100
#end_hour=1715554800     # 051223

# 202401 0809-1523
expname=RRFSret_July2024_PF_ctrl
start_hour=1721433600   # 010800
end_hour=1722470400     # 011923


# 202307 0113-0823
#expname=RRFS_NA_3kmret_July2023_v112                 # NA 3km
#start_hour=1688212800    # 070112
#end_hour=1689202800      # 071223


# 1: reprocess each fcst
# 0: not reprocess if current fcst is processed, it search database, if fcst is processed, then go to next fcst hour
# for(my $valid_time=$startSecs;$valid_time<=$endSecs;$valid_time+=1*3600) 
# foreach my $fcst_len (@fcst_lens) 


cd $HOME/ruc_madis_surface
./retro2.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/bjallen/infs_${expname} 2>&1 &  # 1: reprocess, 0: do not reprocess

cd $HOME/RR_uaverif
./process_retro4.pl ${expname} ${start_hour} ${end_hour} FW-to-Wobus 1  > /lfs5/BMC/amb-verif/bjallen/infu_${expname} 2>&1 &

cd $HOME/ceiling
ceil_driver_retro.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/bjallen/infc_${expname} 2>&1 &
#ceil_driver_retro_exp_diag.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs4/BMC/amb-verif/Ruifang.Li/infc_diag_${expname} 2>&1 &
#ceil_driver_retro_exp_diag2.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs4/BMC/amb-verif/Ruifang.Li/infc_diag2_${expname} 2>&1 &




# use /misc/whome/role.amb-verif/utilities/time70.pl
# to find the experiment period.



