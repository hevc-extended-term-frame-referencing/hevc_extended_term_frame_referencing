# Sequence-Level Reference Frames In Video Coding

## Introduction

This repository contains our public tools for compressing videos based on HEVC refernce software with extended long-term prediction using sequence-level refernce frames

## Prerequisites

In order to compile and run the tools provided in this repository you will need:
1. Python 2.7 
2. ffmpeg (version 2.8.15 or higher)
3. opencv

## To generate a list of sequence level reference frames
python sequence_level_reference_frames.py: produce a list of sitching frames saved to a text file [OrderedFrames.txt]

example:
python sequence_level_reference_frames.py --f=./SV_LowQuality/SV1.mp4 --fps=24 --gp=0 --wd=1 --wpp=1 --suffix='test' --maxf=400 --maxn=5

Option | Description
---|---
--f | input file name 
--fps | frame per second
--gp | minimum distance (number of frames) between two stitching frames
--wd | weight of dissimilarity score
--wpp | weight of popularity score
--maxf | number of original video frames to be considered for stitching frames [maxf=0; consider all of frames in the input video]
--maxn | number of stitch frames [maxn=0; number of stitch frames equals the number of scnene cuts]
--suffix | text to be appended to the output file name

## Edit the sequence level configuration file [sequence_level.cfg]
Parametters | Description [example]
---|---
RankListFile | text file containing the list of sequence-level frames produced sequence_level_reference_frames.py [Orderedlist.txt]
GOP | size of the GOP, must be the full length of the video [1200]
num_ref_pics_active_Max | maximum number of reference frames which includes the short-term and long-term refernce frames (stitching reference frames) [12]
num_ref_pics_active_Stitching | maximum number of long-term refernce fframes (stitching reference frames) [4]
vid | input video [SV1.mp4]
W | width of the YUV video [640]
H | height of the YUV video
QP | initial QP
fps |  frames per second [30]
MaxCUSiz | maximum coding unit size [64]
MaxPartitionDepth | maximum partition depth [4]
RateControl | enable rate control [1]
Rate | target bitrate [1000000]
NoBFrames | number of Bidirection frames [0]

## To create an encoder sequenc-level configuration file [encoding structure of a GOP]
python cfg_hevc_sequence_level_reference_frames.py --c=sequence_level.cfg


## Encoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppEncoderStatic -c ./encoder_HMS.cfg -c ./encoder_HMS_sequence_level_GOP.cfg --InputFile=input.yuv --SourceWidth=640 --SourceHeight=480  --QP=30 --FrameRate=24 
--FramesToBeEncoded=120 --MaxCUSize=64 --MaxPartitionDepth=4 --QuadtreeTULog2MaxSize=4 --BitstreamFile=stream.bin --RateControl=1 --TargetBitrate=100000

## Decoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppDecoderStatic --BitstreamFile=stream.bin --ReconFile=./input_recon.yuv

## Cropped AVC/H.264 Bitstream and Optical Flow Approximation (MVs)
To produce AVC/H.264 cropped bitstreams and their corresponding approximated optical flow run:
```
cd JM_MV_CNN
./JM_Cropped_MV_Stats -svid <input_video>
```

The following encoding parameters can be set directly:

Option | Description [default]
---|---
--svid |  Input video [./v_BoxingPunchingBag_g05_c01.avi]
--W  | width of the YUV video [320]
--H | height of thhe YUV video [240]
--ecfg |  JM configuration file [encoder_option2.cfg]
--qp  |   QP value for P and I frames [40]
--sr  |   search range [16]
--res  |  resolution of the MB Grid (4,8,16) [8]

A successful run using the default parameters passes the following to stdout:
```
%########################################################################################
JM config file=encoder_option2.cfg, Source Video=v_BoxingPunchingBag_g05_c01.avi, QP=40, Search Range=16, MV Resolution=8
%########################################################################################
- Converting source video to YUV format
- Producing cropped H.264 bitstream (encoder)
- Extracting MVs from the cropped H.264 bitstream (decoder)
- Original JM: encoding to produce rate (bps) per frame (optional: for comparison purposes) 
- Mapping MV to a grid according to Macroblocks positions
- Moving outputs to JMMV parent directory
```
The JM_Cropped_MV_Stats generates the following outputs in the JMMV parent directory:

File Name | Description
---|---
x.264 | Compressed JM bitstream
x_Cropped.264 | Cropped JM bitstream
x_JMMV.bin | Flow estimate using JM MVs
x_JMFrameStats_NoTexture.dat | States (including rate) per frame for the cropped bitstream
x_JMStats_NoTexture.dat | Summary of states for the cropped bitstream
x_JMFrameStats_Orig.dat | States (including rate) per frame for the bitstream produced by the original JM encoder
x_JMStats_Orig.dat | Summary of states for the original JM bitstream

## Cropped HEVC Bitstream and Optical Flow Approximation (MVs)
To produce HEVC cropped bitstreams and their corresponding approximated optical flow run:
```
cd HM_MV_CNN
./HM_Cropped_MV_Stats -svid <input_video>
```

HM_Cropped_MV_Stats takes a .avi input to produce the cropped bitsream and flow estimates according to the following steps:

Various encoding parameters can be set directly such as

Option | Description [default]
---|---
--svid |  input video [./v_BoxingPunchingBag_g05_c01.avi]
--W  | width of the YUV video [320]
--H | height of thhe YUV video [240]
--ecfg |  HM configuration file [encoder_rate_accuracy.cfg]
--qp  |   QP value for P and I frames [40]
--mcu |   maximum CTU size [16]
--mpd |   maximum partition depth [2]
--sr  |   search range [16]
--res  |  resolution of the CU Grid (4,8,16) [8]


A successful run using the default parameters passes the following to stdout:
```
%########################################################################################
HM config file=encoder_rate_accuracy.cfg, Source Video=v_BoxingPunchingBag_g05_c01.avi, QP=40, Search Range=16, MV Resolution=8
%########################################################################################
- Converting source video to YUV format
- Producing cropped HEVC bitstream (encoder)
- Extracting MVs from the cropped HEVC bitstream (decoder)
- Original HM: encoding and then decoding to produce rates and stats (optional: for comparsion purposes)
- Mapping MV to a grid according to CU positions
- Moving outputs to HMMV parent directory
```

The HM_Cropped_MV_Stats generates the following outputs in the HMMV parent directory:

File Name | Description
---|---
x.bin | Compressed HM bitstream
x_Cropped.bin | Cropped HM bitstream
x_HMMV.bin | Flow estimate using HM MVs
x_HMStats_NoTexture.dat | Summary of states for the cropped bitstream
x_HMStats_Orig.dat | Summary of states for the original HM bitstream

## Training And Testing On H.264 And HEVC Approximated Optical Flow
To train and test on the binary files produced using the tools described above please have a look at our previous work here:
https://github.com/mvcnn/mvcnn




#To get  list of stitch frames

sequence_level_reference_frames.py: produce a list of sitching frames saved to a text file [OrderedFrames.txt]

example:
python sequence_level_reference_frames.py --f=./SV_LowQuality/SV1.mp4 --fps=24 --gp=0 --wd=1 --wpp=1 --suffix='test' --maxf=400 --maxn=5

Options
--f		input file name 
--fps		frame per second
--gp		minimum distance (number of frames) between two stitching frames
--wd		weight of dissimilarity score
--wpp		weight of popularity score
--maxf		number of original video frames to be considered for stitching frames [maxf=0; consider all of frames in the input video]
--maxn		number of stitch frames [maxn=0; number of stitch frames equals the number of scnene cuts]
--suffix	text to be appended to the output file name


## To create a configuration file
python cfg_hevc_sequence_level_reference_frames.py --c=sequence_level.cfg


## Encoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppEncoderStatic -c ./encoder_HMS.cfg -c ./encoder_HMS_sequence_level_GOP.cfg --InputFile=input.yuv --SourceWidth=640 --SourceHeight=480  --QP=30 --FrameRate=24 
--FramesToBeEncoded=120 --MaxCUSize=64 --MaxPartitionDepth=4 --QuadtreeTULog2MaxSize=4 --BitstreamFile=stream.bin --RateControl=1 --TargetBitrate=100000

## Decoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppDecoderStatic --BitstreamFile=stream.bin --ReconFile=./input_recon.yuv
