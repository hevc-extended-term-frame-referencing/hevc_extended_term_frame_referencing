#Frame1: Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference pictures     predict deltaRPS #ref_idcs reference idcs
#print >> fid, 'Frame1:  P    1   5       -6.5                      0.2590         0          0          1.0   0            0               0           1                1         -1      0');
from __future__ import division
import numpy as np
import os, sys, subprocess, pdb
import argparse


# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--GOP', type=int,
                    help='GOP size')

parser.add_argument('--stitch_frame', type=int,
                    help='Number of stitched frame')

args = parser.parse_args()

##Inputs
GOP=args.GOP;
stitch_frame=args.stitch_frame;

ref_pics_active_Stitching=1
ref_pics_active_Max=1

def Build_encoding_struct_stitch():
	## Buidling encoding structure for Stitching mode
	ref_pics_stitch_to_use=[]
	if 0 in ref_pics_Stitching_array:
		if ref_pics_active_Stitching>0:
			ref_pics_stitch_to_use=np.append(ref_pics_stitch_to_use,0)

	ref_pics=np.array([stitch_frame])

        GOPLine='Frame' + str(1) + ': I '+ str(stitch_frame) +' 0 -6.5 0.2590 0 0 1.0 0 0 0 '+ str(0) + ' ' + str(0)+' '+str(int(0))
	print >> fid, GOPLine

	cntin=1
	for cnt in range(1,NumFrames):
            if cnt != stitch_frame:
	
		GOPLine='Frame' + str(cnt+cntin) + ': P '+ str(cnt) +' 0 -6.5 0.2590 0 0 1.0 0 0 0 '+ str(len(ref_pics)) + ' ' + str(len(ref_pics))
		for cnt1 in range(len(ref_pics)):
			GOPLine=GOPLine+' '+str(int(ref_pics[cnt1]-cnt))
	
		GOPLine=GOPLine+' 2 0'
			
		print >> fid, GOPLine
            else:
                cntin=0
  


if __name__ == '__main__':

   iFNums=map(int, range(GOP+1))

   ## get total number of frames
   NumFrames=round(len(iFNums))
   NumFrames=int(NumFrames)

   ##write config files header
   fid = open('encoder_HMS_GOP.cfg','w')
   print >> fid, '#======== Coding Structure ============='
   print >> fid, 'IntraPeriod                   : -1           # Period of I-Frame ( -1 = only first)'
   print >> fid, 'DecodingRefreshType           : 2           # Random Accesss 0:none, 1:CRA, 2:IDR, 3:Recovery Point SEI'
   print >> fid, 'GOPSize                       : '+str(GOP)+'           # GOP Size (number of B slice = GOPSize-1)'
   print >> fid, 'ReWriteParamSetsFlag          : 1           # Write parameter sets with every IRAP'
   '#        Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference pictures     predict     deltaRPS' '#ref_idcs reference idcs'
   print >> fid,''
   
   ## Produce iFNums_array2 [stitch_frame; other frames ordered]
   iFNums_array = np.array(iFNums)
   #iFNums_array=iFNums_array.clip(0, 999999999)
   #indexes = np.unique(iFNums_array, return_index=True)[1]
   #iFNums_array=[iFNums_array[index] for index in sorted(indexes)]
   #iFNums_array=np.array(iFNums_array)

   ref_pics_Stitching_array=np.array([stitch_frame])

   ref_pics_RemovedStitching_array=np.array(range(0,NumFrames))
   index=np.where(np.isin(ref_pics_RemovedStitching_array,ref_pics_Stitching_array))
   ref_pics_RemovedStitching_array=np.delete(ref_pics_RemovedStitching_array,index)

   ref_pics_RemovedStitching_array.sort()
   iFNums_array2=np.concatenate((ref_pics_Stitching_array,ref_pics_RemovedStitching_array), axis=0) #Stitching Frames + Ordered remaining Frames
   #print(iFNums_array2)

   ## Write GOP structure to config file
   Build_encoding_struct_stitch()


