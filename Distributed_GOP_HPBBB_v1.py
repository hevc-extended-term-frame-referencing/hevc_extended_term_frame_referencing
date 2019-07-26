#Frame1: Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference pictures     predict deltaRPS #ref_idcs reference idcs
#print >> fid, 'Frame1:  P    1   5       -6.5                      0.2590         0          0          1.0   0            0               0           1                1         -1      0');
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
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

###--------------------------------------------------------------
def call_bg(cmd):
    #proc = subprocess.Popen(cmd, shell=True)
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    return proc

###--------------------------------------------------------------
def call_bg_file(cmd,fidProcess):
    proc = subprocess.Popen(cmd,stdout=fidProcess, shell=True)
    fidProcess.close
    return proc

###--------------------------------------------------------------
def export_frames(fn):
    osout = call('rm -rf rec.yuv')
    osout = call('rm -rf {}'.format(Split_video_path))
    osout = call('mkdir {}'.format(Split_video_path))
    osout = call('mkdir {}/pngparallel'.format(Split_video_path))
    osout = call('ffmpeg -r 1 -i {} -r 1 {}/pngparallel/%d.png'.format(fn,Split_video_path))
    return 

###--------------------------------------------------------------
def Split_Video_GOP(Distributed_GOP_Matrix):
    for cnt_row in range(np.shape(Distributed_GOP_Matrix)[0]):
        osout = call('rm -rf {}/Part{}'.format(Split_video_path,cnt_row))
        osout = call('mkdir {}/Part{}'.format(Split_video_path,cnt_row))
        for cnt_col in range(np.shape(Distributed_GOP_Matrix)[1]):
            osout = call('cp -rf {}/pngparallel/{}.png {}/Part{}/{}.png'.format(Split_video_path,int(Distributed_GOP_Matrix[cnt_row,cnt_col]+1),Split_video_path,cnt_row,int(cnt_col+1)))
        osout = call('ffmpeg -start_number 0 -i {}/Part{}/%d.png -c:v libx264 -qp 0 -vf "fps=25,format=yuv420p" {}/Part{}/Part{}.mp4'.format(Split_video_path,cnt_row,Split_video_path,cnt_row,cnt_row))
        osout = call('ffmpeg -y -i {}/Part{}/Part{}.mp4 -vcodec rawvideo -pix_fmt yuv420p {}/Part{}/Part{}.yuv'.format(Split_video_path,cnt_row,cnt_row,Split_video_path,cnt_row,cnt_row))
    return

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
    	fid = open('{}/Part{}/encoder_HMS_GOP_{}.cfg'.format(Split_video_path,Pcnt,Pcnt),'w')
    	print >> fid, '#======== Coding Structure ============='
    	print >> fid, 'IntraPeriod                   : -1           # Period of I-Frame ( -1 = only first)'
    	print >> fid, 'DecodingRefreshType           : 2           # Random Accesss 0:none, 1:CRA, 2:IDR, 3:Recovery Point SEI'
    	print >> fid, 'GOPSize                       : '+str(GOP-NoBFrames)+'           # GOP Size (number of B slice = GOPSize-1)'
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
        cnt_enc=1
    	for cnt in range(NoBFrames,NumFrames_Distributed+1,NoBFrames):
           #pdb.set_trace() 
	   ref_pics_notstitch_to_use_Distributed=[]
	   ref_pics_old_Distributed=ref_pics_Distributed
	   ref_pics_Distributed=[]
	   reference_idcs_Distributed=[]
	   cnt2=cnt-NoBFrames
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
	
	   GOPLine='Frame' + str(cnt_enc) + ': P '+ str(cnt) +' 0 -6.5 0.2590 0 0 1.0 0 0 0 '+ str(len(ref_pics_Distributed)) + ' ' + str(len(ref_pics_Distributed))
           cnt_enc=cnt_enc+1;
	   for cnt1 in range(len(ref_pics_Distributed)):
	      GOPLine=GOPLine+' '+str(int(ref_pics_Distributed[cnt1]-cnt))
	   if cnt == NoBFrames:
	      GOPLine=GOPLine+' 0'
	   else:	
	      GOPLine=GOPLine+' 2 0'
			
           print >> fid, GOPLine

   
           ### added to incorporate B frames (PBBB...BPBBB...B)
           if cnt>0:
	      for cntB in range(cnt-NoBFrames+1,cnt):
	         ref_pics_notstitch_to_use_Distributed=[]
	         ref_pics_old_Distributed=ref_pics_Distributed
	         ref_pics_Distributed=[]
	         reference_idcs_Distributed=[]
	         cnt2=cntB-1
	         ref_pics_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,ref_pics_stitch_to_use_Distributed)
                 ref_pics_L1list=cnt
                 #print(ref_pics_Distributed)
	         while len(ref_pics_notstitch_to_use_Distributed)<num_ref_pics_active_Max_Distributed-num_ref_pics_active_Stitching_Distributed:
	            ref_pics_notstitch_to_use_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,cnt2)
	            ref_pics_Distributed=np.append(ref_pics_notstitch_to_use_Distributed,ref_pics_stitch_to_use_Distributed)
	            ref_pics_Distributed=np.unique(ref_pics_Distributed)
	            cnt2=cnt2-1
	         ref_pics_Distributed=np.sort(ref_pics_Distributed)
	         ref_pics_Distributed=ref_pics_Distributed[ref_pics_Distributed>=0]
	         ref_pics_Distributed=ref_pics_Distributed[::-1]
              
                 ref_pics_Distributed=np.append(ref_pics_Distributed,ref_pics_L1list)
                 #print(ref_pics_Distributed)

	         if cntB in ref_pics_Stitching_array_Distributed:
	            if len(ref_pics_stitch_to_use_Distributed) < num_ref_pics_active_Stitching_Distributed: 
	               ref_pics_stitch_to_use_Distributed=np.append(ref_pics_stitch_to_use_Distributed,cntB)
	
      	         GOPLine='Frame' + str(cnt_enc) + ': B '+ str(cntB) +' 0 -6.5 0.2590 0 0 1.0 0 0 0 '+ str(len(ref_pics_Distributed)) + ' ' + str(len(ref_pics_Distributed))
                 cnt_enc=cnt_enc+1;
	         for cnt1 in range(len(ref_pics_Distributed)):
	            GOPLine=GOPLine+' '+str(int(ref_pics_Distributed[cnt1]-cntB))	
	         GOPLine=GOPLine+' 2 0'
			
                 print >> fid, GOPLine

	##### end of adding B frames

	fid.write('\n#Note: The number of frames in the particitioned video is equal to GOP (Frame#0, Frame#1, .... Frame#(GOP-1)) and thus the line Frmae#GOP in this file will not be used to encode any frame, it is added to comply with the required format of HEVC GOP structure')
        fid.close()
 

###--------------------------------------------------------------
def Encode_decode_video(Distributed_GOP_Matrix):
    encoderlog=[]
    decoderlog=[]
    decoderVMAFlog=[]
    PcntCompleted=[]
    Pcnt2=0
    now_start=[]
    now_end=[]
    for Pcnt in range(np.shape(Distributed_GOP_Matrix)[0]):
         now_start.append(datetime.datetime.now())
         print('Encoding GOP#{} of {} ... {}'.format(Pcnt,(np.shape(Distributed_GOP_Matrix)[0]-1),now_start[Pcnt].strftime("%Y-%m-%d %H:%M:%S")))
         InputYUV='{}/Part{}/Part{}.yuv'.format(Split_video_path,Pcnt,Pcnt)
         BitstreamFile='{}/Part{}/HMEncodedVideo.bin'.format(Split_video_path,Pcnt)
         osout = call('rm -rf {}'.format(BitstreamFile))
         osout = call('cp -f ./encoder_HMS.cfg {}/Part{}/encoder_HMS.cfg'.format(Split_video_path,Pcnt))
   
         encoderlogfile='{}/Part{}/encoderlog.dat'.format(Split_video_path,Pcnt)
         fid = open(encoderlogfile,'w')
         osout=call_bg_file('./HMS/bin/TAppEncoderStatic -c {}/Part{}/encoder_HMS.cfg -c {}/Part{}/encoder_HMS_GOP_{}.cfg --InputFile={} --SourceWidth={} --SourceHeight={} --SAO=0 --QP={} --FrameRate={} --FramesToBeEncoded={} --MaxCUSize={} --MaxPartitionDepth={} --QuadtreeTULog2MaxSize=4 --BitstreamFile="{}" --RateControl={} --TargetBitrate={}'.format(Split_video_path,Pcnt,Split_video_path,Pcnt,Pcnt,InputYUV,Width,Hight,QP,fps,GOP,MaxCUSize,MaxPartitionDepth,BitstreamFile,RateControl,rate),fid)
         encoderlog.append(osout)
         PcntCompleted.append(Pcnt)

         if (int(len(PcntCompleted) % NProcesses) == 0):
             encoderlog[Pcnt2].wait()
             PcntCompleted.remove(Pcnt2)
             now_end.append(datetime.datetime.now())
             print('Encoding of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)-now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
             Pcnt2=Pcnt2+1

         if (Pcnt==(np.shape(Distributed_GOP_Matrix)[0]-1)):
            for Pcnt2 in PcntCompleted:
                encoderlog[Pcnt2].wait()
                now_end.append(datetime.datetime.now())
                print('Encoding of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)- now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
            PcntCompleted=[]

   ### decoding ---------------

    PcntCompleted=[]
    Pcnt2=0
    now_start=[]
    now_end=[]
    for Pcnt in range(np.shape(Distributed_GOP_Matrix)[0]):
         now_start.append(datetime.datetime.now())
         print('Decoding GOP#{} of {} ... {}'.format(Pcnt,(np.shape(Distributed_GOP_Matrix)[0]-1),now_start[Pcnt].strftime("%Y-%m-%d %H:%M:%S")))
         InputYUV='{}/Part{}/Part{}.yuv'.format(Split_video_path,Pcnt,Pcnt)
         ReconFile='{}/Part{}/ReconPart{}.yuv'.format(Split_video_path,Pcnt,Pcnt)
         BitstreamFile='{}/Part{}/HMEncodedVideo.bin'.format(Split_video_path,Pcnt)
         osout = call('rm -rf {}'.format(ReconFile))
         
         decoderlogfile='{}/Part{}/decoderlog.dat'.format(Split_video_path,Pcnt)
         fid = open(decoderlogfile,'w')
         osout=call_bg_file('./HMS/bin/TAppDecoderStatic --BitstreamFile="{}" --ReconFile="{}"'.format(BitstreamFile,ReconFile),fid)
         decoderlog.append(osout)
         PcntCompleted.append(Pcnt)

         if (int(len(PcntCompleted) % NProcesses) == 0):
             decoderlog[Pcnt2].wait()
             PcntCompleted.remove(Pcnt2)
             now_end.append(datetime.datetime.now())
             print('Decoding of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)-now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
             Pcnt2=Pcnt2+1

         if (Pcnt==(np.shape(Distributed_GOP_Matrix)[0]-1)):
            for Pcnt2 in PcntCompleted:
                decoderlog[Pcnt2].wait()
                now_end.append(datetime.datetime.now())
                print('Decoding of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)- now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
            PcntCompleted=[]

   ### VMAF ---------------

    PcntCompleted=[]
    Pcnt2=0
    now_start=[]
    now_end=[]
    for Pcnt in range(np.shape(Distributed_GOP_Matrix)[0]):
         now_start.append(datetime.datetime.now())
         print('Computing VMAF GOP#{} of {} ... {}'.format(Pcnt,(np.shape(Distributed_GOP_Matrix)[0]-1),now_start[Pcnt].strftime("%Y-%m-%d %H:%M:%S")))
         InputYUV='{}/Part{}/Part{}.yuv'.format(Split_video_path,Pcnt,Pcnt)
         ReconFile='{}/Part{}/ReconPart{}.yuv'.format(Split_video_path,Pcnt,Pcnt)
         
         decoderVMAFlogfile='{}/Part{}/decoderVMAFlog.dat'.format(Split_video_path,Pcnt)
         fidVMAF = open(decoderVMAFlogfile,'w')
         osout=call_bg_file('../vmaf/run_vmaf yuv420p {} {} {} {}'.format(Width,Hight,ReconFile,InputYUV),fidVMAF)
	 decoderVMAFlog.append(osout)
         
         PcntCompleted.append(Pcnt)

         if (int(len(PcntCompleted) % NProcesses) == 0):
             decoderVMAFlog[Pcnt2].wait()
             PcntCompleted.remove(Pcnt2)
             now_end.append(datetime.datetime.now())
             print('Computing VMAF of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)-now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
             Pcnt2=Pcnt2+1

         if (Pcnt==(np.shape(Distributed_GOP_Matrix)[0]-1)):
            for Pcnt2 in PcntCompleted:
                decoderVMAFlog[Pcnt2].wait()
                now_end.append(datetime.datetime.now())
                print('Computing VMAF of GOP#{} is completed ... {}   ({}) .. ({})'.format(Pcnt2,now_end[Pcnt2].strftime("%Y-%m-%d %H:%M:%S"),now_end[Pcnt2].replace(microsecond=0)- now_start[Pcnt2].replace(microsecond=0),now_end[Pcnt2].replace(microsecond=0)-now_start[0].replace(microsecond=0)))
            PcntCompleted=[]

    return

###--------------------------------------------------------------
def Combine_encoder_log(Distributed_GOP_Matrix):
    CombinedLines=[]
    CombinedLinesAll=[]
    for cnt_row in range(np.shape(Distributed_GOP_Matrix)[0]):
        cnt_col=0
        encoderlogfile='{}/Part{}/encoderlog.dat'.format(Split_video_path,cnt_row)
        with open(encoderlogfile) as f:
             Lines = f.readlines()
        f.close()
        for cnt in range(len(Lines)):
            if Lines[cnt][:].split(' ')[0] == 'POC':
               CombinedLinesAll.append(Lines[cnt][:])
               if (Distributed_GOP_Matrix[cnt_row][cnt_col] > Distributed_GOP_Matrix[cnt_row-1][GOP-1]) or (cnt_row==0):
                    CombinedLines.append(Lines[cnt][:])
                    cnt_col=cnt_col+1
               else:
                    cnt_col=cnt_col+1

    CombinedLinesVMAF=[]
    CombinedLinesAllVMAF=[]
    for cnt_row in range(np.shape(Distributed_GOP_Matrix)[0]):
        cnt_col=0
        decoderlogfile='{}/Part{}/decoderVMAFlog.dat'.format(Split_video_path,cnt_row)
        with open(decoderlogfile) as f:
             LinesDec = f.readlines()
        f.close()
        #pdb.set_trace()
        for cnt in range(len(LinesDec)):
            if LinesDec[cnt][:].split(' ')[0] == 'Frame':
               CombinedLinesAllVMAF.append(LinesDec[cnt][:])
	       #print('{}..{}..{}..{}\n'.format(cnt_row,cnt_col,cnt,LinesDec[cnt][:]))
               #print(len(CombinedLinesVMAF))
               #pdb.set_trace()
               if (Distributed_GOP_Matrix[cnt_row][cnt_col] > Distributed_GOP_Matrix[cnt_row-1][GOP-1]) or (cnt_row==0):
                    CombinedLinesVMAF.append(LinesDec[cnt][:])
                    #print(CombinedLinesVMAF)
                    cnt_col=cnt_col+1
                    #print(len(CombinedLinesVMAF))
               else:
                    cnt_col=cnt_col+1

    #pdb.set_trace()
    fid = open(Combined_encoder_log,'w')
    fid.write('Input File (MP4) = {}\n'.format(vid))
    fid.write('RankListFile = {}\n'.format(RankListFile))
    fid.write('Ref_active = {}\n'.format(num_ref_pics_active_Max))
    fid.write('Ref_stitch = {}\n'.format(num_ref_pics_active_Stitching))
    fid.write('QP = {}\n'.format(QP))
    fid.write('MaxCUSize = {}\n'.format(MaxCUSize))
    fid.write('MaxPartitionDepth = {}\n'.format(MaxPartitionDepth))
    fid.write('fps = {}\n'.format(fps))
    fid.write('RateControl = {}\n'.format(RateControl))
    fid.write('rate = {}\n'.format(rate))
    fid.write('NProcesses = {}\n\n'.format(NProcesses))
    for cnt in range(len(CombinedLines)):
       templine=CombinedLines[cnt][:].replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.split(' ')
       #print('POC {}...{}'.format(cnt,templine[2:22]))
       fid.write('POC {}...{}\n'.format(cnt,templine[2:22]))

    #pdb.set_trace()
    for cnt in range(len(CombinedLinesVMAF)):
       templine=CombinedLinesVMAF[cnt][:].replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.split(' ')
       #print('VMAF_Frame {}...{}\n'.format(cnt,templine[2:22]))
       fid.write('VMAF_Frame {}...{}\n'.format(cnt,templine[2:22]))
    fid.close

    fid = open((Combined_encoder_log[0:(len(Combined_encoder_log)-4)]+'All.dat'),'w')
    fid.write('Input File (MP4) = {}\n'.format(vid))
    fid.write('RankListFile = {}\n'.format(RankListFile))
    fid.write('Ref_active = {}\n'.format(num_ref_pics_active_Max))
    fid.write('Ref_stitch = {}\n'.format(num_ref_pics_active_Stitching))
    fid.write('QP = {}\n'.format(QP))
    fid.write('MaxCUSize = {}\n'.format(MaxCUSize))
    fid.write('MaxPartitionDepth = {}\n'.format(MaxPartitionDepth))
    fid.write('fps = {}\n'.format(fps))
    fid.write('RateControl = {}\n'.format(RateControl))
    fid.write('rate = {}\n'.format(rate))
    fid.write('NProcesses = {}\n\n'.format(NProcesses))
    for cnt in range(len(CombinedLinesAll)):
       templine=CombinedLinesAll[cnt][:].replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.split(' ')
       #print('POC {}...{}'.format(cnt,templine[2:22]))
       fid.write('POC {}...{}\n'.format(cnt,templine[1:22]))

    for cnt in range(len(CombinedLinesAllVMAF)):
       templine=CombinedLinesAllVMAF[cnt][:].replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.replace("  "," ")
       templine=templine.split(' ')
       #print('VMAF_Frame {}...{}\n'.format(cnt,templine[1:22]))
       fid.write('VMAF_Frame {}...{}\n'.format(cnt,templine[1:22]))

    fid.close

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
    NoBFrames=int(args.nobframes);

    
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
    export_frames(vid)
    Split_Video_GOP(Distributed_GOP_Matrix)
    print(Distributed_GOP_Matrix)
    #print(ref_pics_active_Stitching)
    #print(ref_pics_in_Distributed_GOP_Matrix)

    Create_Encoder_Config(Distributed_GOP_Matrix,ref_pics_in_Distributed_GOP_Matrix)
    #quit()
   
    Encode_decode_video(Distributed_GOP_Matrix)
    Combine_encoder_log(Distributed_GOP_Matrix)    
    #print(Distributed_GOP_Matrix)
