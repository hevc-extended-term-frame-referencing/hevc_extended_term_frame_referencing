# Sequence-Level Reference Frames In Video Coding

## Introduction

This repository contains our public tools for compressing videos based on HEVC reference software with extended long-term prediction using sequence-level reference frames

## Prerequisites

In order to compile and run the tools provided in this repository you will need:
1. Python 2.7 
2. ffmpeg (version 2.8.15 or higher)
3. opencv

## Sequence-Level Reference Frames
To produce a list of sequence-level reference frames based on the algorithm described in our paper run

```
python sequence_level_reference_frames.py --f=./SV_LowQuality/SV1.mp4 --fps=24 --gp=0 --wd=1 --wpp=1 --suffix='test' --maxf=400 --maxn=5
```

Option | Description
---|---
--f | input file name 
--fps | frame per second
--gp | minimum distance (number of frames) between two stitching frames
--wd | weight of dissimilarity score
--wpp | weight of popularity score
--maxf | number of original video frames to be considered for stitching frames [maxf=0; consider all of frames in the input video]
--maxn | number of stitch frames [maxn=0; number of stitch frames equals the number of scene cuts]
--suffix | text to be appended to the output file name

A successful run will produce an OrderedFrames.txt file which includes a list of stitch frames ordered based on popularity and dissimilarity scores.

## Generate encoder configuration file
In order to produce an encoder sequenc-level configuration file which contains the coding structure of all frames within a GOP run

```
python cfg_hevc_sequence_level_reference_frames.py --slist=./OrderedFrames.txt --gop=1200 --active=20 --stitch=16
```

Parameters | Description [example]
---|---
--slist | list of sequence-level refernce frames produced by sequence_level_reference_frames.py [Orderedlist.txt]
--gop | size of the GOP, must be the full length of the video [1200]
--active | number of reference frames inclduing short-term and long-term refernce frames [20]
--stitch | number of long-term refernce frames (stitching reference frames) [16]

A successfull run wil produce an encoder_HMS_sequence_level_GOP.txt file which includes a header and a coding structure of all frames in the GOP such as:

```
#======== Coding Structure =============
IntraPeriod                   : -1           # Period of I-Frame ( -1 = only first)
DecodingRefreshType           : 2           # Random Accesss 0:none, 1:CRA, 2:IDR, 3:Recovery Point SEI
GOPSize                       : 40           # GOP Size (number of B slice = GOPSize-1)
ReWriteParamSetsFlag          : 1           # Write parameter sets with every IRAP


Frame1: P 1 0 -6.5 0.2590 0 0 1.0 0 0 0 1 1 -1 0
Frame2: P 2 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame3: P 3 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame4: P 4 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame5: P 5 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame6: P 6 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame7: P 7 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame8: P 8 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame9: P 9 0 -6.5 0.2590 0 0 1.0 0 0 0 2 2 -1 -2 2 0
Frame10: P 10 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -3 2 0
Frame11: P 11 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -4 2 0
Frame12: P 12 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -5 2 0
Frame13: P 13 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -6 2 0
Frame14: P 14 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -7 2 0
Frame15: P 15 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -8 2 0
Frame16: P 16 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -9 2 0
Frame17: P 17 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -10 2 0
Frame18: P 18 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -11 2 0
Frame19: P 19 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -12 2 0
Frame20: P 20 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -13 2 0
Frame21: P 21 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -14 2 0
Frame22: P 22 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -15 2 0
Frame23: P 23 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -16 2 0
Frame24: P 24 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -17 2 0
Frame25: P 25 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -18 2 0
Frame26: P 26 0 -6.5 0.2590 0 0 1.0 0 0 0 3 3 -1 -2 -19 2 0
Frame27: P 27 0 -6.5 0.2590 0 0 1.0 0 0 0 4 4 -1 -2 -3 -20 2 0
Frame28: P 28 0 -6.5 0.2590 0 0 1.0 0 0 0 4 4 -1 -2 -4 -21 2 0
Frame29: P 29 0 -6.5 0.2590 0 0 1.0 0 0 0 4 4 -1 -2 -5 -22 2 0
Frame30: P 30 0 -6.5 0.2590 0 0 1.0 0 0 0 4 4 -1 -2 -6 -23 2 0
```

## Encoding using HEVC reference software (HM) with sequence-level reference frames
To compress a video using our method, include the sequenc-level configuration file [encoder_HMS_sequence_level_GOP.cfg] in the HM encoder command line.

```
./HMS/bin/TAppEncoderStatic -c ./encoder_HMS.cfg -c ./encoder_HMS_sequence_level_GOP.cfg --InputFile=input.yuv --SourceWidth=640 --SourceHeight=480  --QP=30 --FrameRate=24 --FramesToBeEncoded=120 --MaxCUSize=64 --MaxPartitionDepth=4 --QuadtreeTULog2MaxSize=4 --BitstreamFile=stream.bin --RateControl=1 --TargetBitrate=100000
```

## Decoding using HEVC reference software (HM)
To decode the compressed video, use the HM decoder.

```
./HMS/bin/TAppDecoderStatic --BitstreamFile=stream.bin --ReconFile=./input_recon.yuv
```

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
