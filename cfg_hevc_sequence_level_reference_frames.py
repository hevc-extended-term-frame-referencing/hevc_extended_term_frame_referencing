#Frame1: Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference 
#pictures predict deltaRPS #ref_idcs reference idcs print >> fid, 'Frame1: P 1 5 -6.5 0.2590 0 0 1.0 0 0 0 1 1 -1 0');
from __future__ import division
import numpy as np
import os, sys, subprocess, pdb
import argparse
import ConfigParser
import datetime, math, time


INF = 999

###--------------------------------------------------------------
## Parse configuration Parameters from the configuration file
def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = { "option":"default"}

    if args.conf_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Parametters")))
        #print(dict(config.items("Parametters")))

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)   
    args = parser.parse_args(remaining_argv)
    return(args)

###--------------------------------------------------------------
## read frame numbers from Rank List File
def read_ranklist():
   ## read priority list
   with open(RankListFile) as f:
       FNums = f.readlines()
   f.close()
   iFNums=map(int, FNums)

   ## get total number of frames
   NumFrames=round(len(iFNums))
   NumFrames=int(NumFrames)
   return(iFNums,NumFrames)

###--------------------------------------------------------------
## convert iFNums from vector to matrix such that each row is a separate GOP
def Create_Distributed_GOP_Matrix():
   NotAlloc_Frames=np.arange(0,NumFrames)
   for val in ref_pics_active_Stitching:
      idx=np.where(NotAlloc_Frames==val)
      NotAlloc_Frames=np.delete(NotAlloc_Frames,idx)

   Distributed_GOP_Matrix=np.ones((GOP,0), dtype=int)
   ref_pics_in_Distributed_GOP_Matrix=np.empty(0)
   while len(NotAlloc_Frames)>0:
       Distributed_GOP_Vec=np.empty(0)
       ref_pics_active_Stitching_temp=ref_pics_active_Stitching
       #### To add few frames at the beginning of GOp encoding .. lagging
       ref_pics_active_Stitching_temp=np.append(ref_pics_active_Stitching_temp,(Distributed_GOP_Matrix[(len(Distributed_GOP_Matrix)-num_ref_pics_active_Max+num_ref_pics_active_Stitching):(len(Distributed_GOP_Matrix))]))
       ref_pics_active_Stitching_temp=np.unique(ref_pics_active_Stitching_temp)
       ref_pics_active_Stitching_temp=np.sort(ref_pics_active_Stitching_temp)
       #print(ref_pics_active_Stitching)
       #print(ref_pics_active_Stitching_temp)
       #print(Distributed_GOP_Matrix)
       #pdb.set_trace()  
       ####
       ref_pics_added=0;
       while len(Distributed_GOP_Vec)<GOP:
          if len(NotAlloc_Frames)==0:     #if all frames are allocated to Distributed Matrix
              break
          elif len(ref_pics_active_Stitching_temp)==0: #if all sticthing frames are allocated to Distributed Matrix
              Distributed_GOP_Vec=np.append(Distributed_GOP_Vec,NotAlloc_Frames[0])
              NotAlloc_Frames=np.delete(NotAlloc_Frames,0)
          elif ref_pics_active_Stitching_temp[0]<NotAlloc_Frames[0]: #if the smallest stitch frames is less than the smallest not allocated frame 
              Distributed_GOP_Vec=np.append(Distributed_GOP_Vec,ref_pics_active_Stitching_temp[0])
              if ref_pics_active_Stitching_temp[0] in ref_pics_active_Stitching:   ### added to avoid considering lag frames as stitchers
                 ref_pics_added=ref_pics_added+1
              ref_pics_active_Stitching_temp=np.delete(ref_pics_active_Stitching_temp,0)
          else:
              Distributed_GOP_Vec=np.append(Distributed_GOP_Vec,NotAlloc_Frames[0])
              NotAlloc_Frames=np.delete(NotAlloc_Frames,0)
       if len(Distributed_GOP_Vec)==GOP:
              Distributed_GOP_Matrix=np.append(Distributed_GOP_Matrix,Distributed_GOP_Vec)
       ref_pics_in_Distributed_GOP_Matrix=np.append(ref_pics_in_Distributed_GOP_Matrix,ref_pics_added)
   Distributed_GOP_Matrix=np.reshape(Distributed_GOP_Matrix,(int(len(Distributed_GOP_Matrix)/GOP),GOP))
   return(Distributed_GOP_Matrix,ref_pics_in_Distributed_GOP_Matrix)

###--------------------------------------------------------------
def call(cmd):
    # proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
    #proc = subprocess.Popen(cmd, \
    #               stdout=subprocess.PIPE, shell=True)
    #proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen(cmd,shell=True)
    (out, err) = proc.communicate()
    return (out, err)

###--------------------------------------------------------------
def call_bg(cmd):
    #proc = subprocess.Popen(cmd, shell=True)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    return proc


###--------------------------------------------------------------
def Create_Encoder_Config(Distributed_GOP_Matrix,ref_pics_in_Distributed_GOP_Matrix):
    for Pcnt in range(np.shape(Distributed_GOP_Matrix)[0]):
        if Pcnt==0:
            print('GOP#{} [{} - {}]'.format(Pcnt,int(Distributed_GOP_Matrix[Pcnt][0]),int(Distributed_GOP_Matrix[Pcnt][np.shape(Distributed_GOP_Matrix)[1]-1])))
        else:
            print('GOP#{} [{} - {}]'.format(Pcnt,int((Distributed_GOP_Matrix[Pcnt-1][np.shape(Distributed_GOP_Matrix)[1]-1])+1),int(Distributed_GOP_Matrix[Pcnt][np.shape(Distributed_GOP_Matrix)[1]-1])))
    	Abs_ref_pics_Stitching_array_Distributed=ref_pics_active_Stitching[0:int(ref_pics_in_Distributed_GOP_Matrix[Pcnt])]
    	#num_ref_pics_active_Stitching_Distributed=len(Abs_ref_pics_Stitching_array_Distributed)
        num_ref_pics_active_Stitching_Distributed=len(ref_pics_active_Stitching)
    	NumFrames_Distributed=GOP
    	num_ref_pics_active_Max_Distributed=num_ref_pics_active_Max
        
        ref_pics_Stitching_array_Distributed=[];
        relative_ref_value=0
        if Pcnt>0:
           for Abs_ref_value in Abs_ref_pics_Stitching_array_Distributed:
              if Abs_ref_value <= Distributed_GOP_Matrix[Pcnt-1][GOP-1]:
                  ref_pics_Stitching_array_Distributed=np.append(ref_pics_Stitching_array_Distributed,relative_ref_value)
                  relative_ref_value=relative_ref_value+1
              else:
                  ref_pics_Stitching_array_Distributed=np.append(ref_pics_Stitching_array_Distributed,Abs_ref_value)
        else:
           ref_pics_Stitching_array_Distributed=Abs_ref_pics_Stitching_array_Distributed
        
        ref_pics_Stitching_array_Distributed_int=[]
        for cnt_int in range(len(ref_pics_Stitching_array_Distributed)):
	        ref_pics_Stitching_array_Distributed_int=np.append(ref_pics_Stitching_array_Distributed_int,int (ref_pics_Stitching_array_Distributed[cnt_int]))

        ref_pics_Stitching_array_Distributed=ref_pics_Stitching_array_Distributed_int
        print('Stitching Frames in the Ref Picture set: Absolute Frame Numbers = {}').format(Abs_ref_pics_Stitching_array_Distributed)
        #print('Stitching Frames in the Ref Picture set: Frame Numbers Relative to this GOP = {}').format(ref_pics_Stitching_array_Distributed)

    	##write config files header
        fid = open('encoder_HMS_sequence_level_GOP.cfg','w')
    	print >> fid, '#======== Coding Structure ============='
    	print >> fid, 'IntraPeriod                   : -1           # Period of I-Frame ( -1 = only first)'
    	print >> fid, 'DecodingRefreshType           : 2           # Random Accesss 0:none, 1:CRA, 2:IDR, 3:Recovery Point SEI'
    	print >> fid, 'GOPSize                       : '+str(GOP)+'           # GOP Size (number of B slice = GOPSize-1)'
    	print >> fid, 'ReWriteParamSetsFlag          : 1           # Write parameter sets with every IRAP'
    	'#        Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference pictures     predict     deltaRPS' '#ref_idcs reference idcs'
    	print >> fid,''
      
        #fid.write('#Stitching Frames in the Ref Picture set: Global Frame Values = %s\n' % Abs_ref_pics_Stitching_array_Distributed)
        #fid.write('#Stitching Frames in the Ref Picture set: Relative to this GOP = %s\n' % ref_pics_Stitching_array_Distributed)
    	print >> fid,''

    	## Buidling encoding structure for Stitching mode
    	ref_pics_stitch_to_use_Distributed=[]
    	if 0 in ref_pics_Stitching_array_Distributed:
	    if num_ref_pics_active_Stitching_Distributed>0:
	        ref_pics_stitch_to_use_Distributed=np.append(ref_pics_stitch_to_use_Distributed,0)

    	ref_pics_Distributed=[]
    	for cnt in range(1,NumFrames_Distributed+1):
	   ref_pics_notstitch_to_use_Distributed=[]
	   ref_pics_old_Distributed=ref_pics_Distributed
	   ref_pics_Distributed=[]
	   reference_idcs_Distributed=[]
	   cnt2=cnt-1
	   ref_pics_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,ref_pics_stitch_to_use_Distributed)
           #print(ref_pics_Distributed)
	   while len(ref_pics_notstitch_to_use_Distributed)<num_ref_pics_active_Max_Distributed-num_ref_pics_active_Stitching_Distributed:
	      ref_pics_notstitch_to_use_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,cnt2)
	      ref_pics_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,ref_pics_stitch_to_use_Distributed)
	      ref_pics_Distributed=np.unique(ref_pics_Distributed)
	      cnt2=cnt2-1
	   ref_pics_Distributed=np.sort(ref_pics_Distributed)
	   ref_pics_Distributed=ref_pics_Distributed[ref_pics_Distributed>=0]
	   ref_pics_Distributed=ref_pics_Distributed[::-1]
           #print(ref_pics_Distributed)

	   if cnt in ref_pics_Stitching_array_Distributed:
	      if len(ref_pics_stitch_to_use_Distributed) < num_ref_pics_active_Stitching_Distributed: 
	         ref_pics_stitch_to_use_Distributed=np.append(ref_pics_stitch_to_use_Distributed,cnt)
	
	   GOPLine='Frame' + str(cnt) + ': P '+ str(cnt) +' 0 -6.5 0.2590 0 0 1.0 0 0 0 '+ str(len(ref_pics_Distributed)) + ' ' + str(len(ref_pics_Distributed))
	   for cnt1 in range(len(ref_pics_Distributed)):
	      GOPLine=GOPLine+' '+str(int(ref_pics_Distributed[cnt1]-cnt))
	   if cnt == 1:
	      GOPLine=GOPLine+' 0'
	   else:	
	      GOPLine=GOPLine+' 2 0'
			
           print >> fid, GOPLine

	fid.write('\n#Note: The number of frames in the particitioned video is equal to GOP (Frame#0, Frame#1, .... Frame#(GOP-1)) and thus the line Frmae#GOP in this file will not be used to encode any frame, it is added to comply with the required format of HEVC GOP structure')
        fid.close()

##################################################################
## Main Body
if __name__ == "__main__":
    args=main()

    ##Inputs
    RankListFile=args.ranklistfile;
    num_ref_pics_active_Max=int(args.num_ref_pics_active_max);
    num_ref_pics_active_Stitching=int(args.num_ref_pics_active_stitching);
    vid=args.vid;

    mode=args.mode;
    fps=int(args.fps);
    GOP=int(args.gop);
    Width=int(args.w);
    Hight=int(args.h);
    QP=int(args.qp);
    MaxCUSize=int(args.maxcusize);
    MaxPartitionDepth=int(args.maxpartitiondepth);
    RateControl=int(args.ratecontrol);
    rate=int(args.rate);
    NProcesses=int(args.nprocesses);
    Combined_encoder_log=args.combined_encoder_log
    Split_video_path=args.split_video_path;


    
    fsr=fps

    if GOP%2!=0:
        GOP=int(GOP/2) * 2

    if num_ref_pics_active_Stitching>num_ref_pics_active_Max:
        num_ref_pics_active_Stitching=num_ref_pics_active_Max
    
    if GOP<(2*num_ref_pics_active_Max):
        GOP=2*num_ref_pics_active_Max

    (iFNums,NumFrames)=read_ranklist();
    iFNums=np.array(iFNums)
    ref_pics_active_Stitching=iFNums[0:(num_ref_pics_active_Stitching)]
    ref_pics_active_Stitching=np.sort(ref_pics_active_Stitching)
    
    (Distributed_GOP_Matrix,ref_pics_in_Distributed_GOP_Matrix)=Create_Distributed_GOP_Matrix();

    Create_Encoder_Config(Distributed_GOP_Matrix,ref_pics_in_Distributed_GOP_Matrix)
