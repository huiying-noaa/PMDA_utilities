#!/bin/ksh -v

set -x

expname=RRFSret_Jul2024_PFaeroda
start_hour=1721779200  #00 24 07 2024
end_hour=1722384000    #00 31 07 2024

# 1: reprocess each fcst
# 0: not reprocess if current fcst is processed, it search database, if fcst is processed, then go to next fcst hour
# for(my $valid_time=$startSecs;$valid_time<=$endSecs;$valid_time+=1*3600) 
# foreach my $fcst_len (@fcst_lens) 


#cd $HOME/ruc_madis_surface
#./retro2.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/hluo/inf2s_${expname} 2>&1 &  # 1: reprocess, 0: do not reprocess

#cd $HOME/RR_uaverif
#./process_retro4.pl ${expname} ${start_hour} ${end_hour} FW-to-Wobus 1  > /lfs5/BMC/amb-verif/hluo/infu_${expname} 2>&1 &

#cd $HOME/ceiling
#./ceil_driver_retro.pl ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/hluo/infc_${expname} 2>&1 &

#cd $HOME/visibility
#./retro_driver.tcsh ${expname} ${start_hour} ${end_hour} 1  > /lfs5/BMC/amb-verif/hluo/infvis_${expname} 2>&1 &

cd $HOME/surfrad3
./gen_surfrad.sh  ${start_hour} ${end_hour} 1 24  ${expname}  > /lfs5/BMC/amb-verif/hluo/Finfsol_${expname} 2>&1 &

#cd $HOME/acars_RR
#cp /home/role.amb-verif/acars_RR/RRFSret_July2024_v084_fcst_lens ${expname}_fcst_lens
#./gen_retro_acars_stats3.pl  ${expname} ${start_hour} ${end_hour} 37 1 > /lfs5/BMC/amb-verif/hluo/inf2airc_${expname} 2>&1 &

# use /misc/whome/role.amb-verif/utilities/time70.pl
# to find the experiment period.



