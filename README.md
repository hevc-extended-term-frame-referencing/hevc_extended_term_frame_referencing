# Sequence-Level Reference Frames In Video Coding

## Introduction

This repository contains our public tools for compressing videos based on HEVC refernce software with extended long-term prediction using sequence-level refernce frames

## Prerequisites

In order to compile and run the tools provided in this repository you will need:
1. Python 2.7 
2. ffmpeg (version 2.8.15 or higher)
3. opencv

## Sequence-Level Reference Frames
To produce a list of sequence-level reference frames based on the method described in our paper:

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


## Generate encoder sequence-level configuration file
To produce an encoder sequenc-level configuration file which containg the coding structure of all frmes in the sequence

python cfg_hevc_sequence_level_reference_frames.py --c=sequence_level.cfg

The parameters used in the sequence_level,cfg file.
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

## Encoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppEncoderStatic -c ./encoder_HMS.cfg -c ./encoder_HMS_sequence_level_GOP.cfg --InputFile=input.yuv --SourceWidth=640 --SourceHeight=480  --QP=30 --FrameRate=24 
--FramesToBeEncoded=120 --MaxCUSize=64 --MaxPartitionDepth=4 --QuadtreeTULog2MaxSize=4 --BitstreamFile=stream.bin --RateControl=1 --TargetBitrate=100000

## Decoding a video using HEVC reference software (HM) with  sequence-level refernce frame
./HMS/bin/TAppDecoderStatic --BitstreamFile=stream.bin --ReconFile=./input_recon.yuv

## LQ Synthesized Videos
Due to limited available space, compressed version of synthesized videos used in our paper use provided in the directory SV_LowQuality

## Links to Natural Videos
The links below are for the naturla videos used in our paper
Video | link
---|---
Breathe|
City Lights|
Brink|
Naught List|
Jet|
Big Bunny|
