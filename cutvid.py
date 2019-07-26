import numpy as np
import os,sys, subprocess, pdb
import datetime, math, time
import argparse, random, ntpath, re

from os import listdir
from os.path import isfile, join   
from random import randint

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--input_dir', type=str,
                    help='videos input dir')

parser.add_argument('--output_dir', type=str,
                    help='videos output dir')

parser.add_argument('--splits', type=int,
                    help='number of splits')


args = parser.parse_args()

##Inputs
input_dir=args.input_dir;
output_dir=args.output_dir;
splits=args.splits;

def call(cmd):
    # proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen(cmd, \
                   stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

def getLength(filename):
  result = subprocess.Popen(["ffprobe", filename],
  stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
  duration_Line=[x for x in result.stdout.readlines() if "Duration" in x]
  duration_Line_array=re.split(' |,',str(duration_Line))
  x = time.strptime(str(duration_Line_array[3]).split('.')[0],'%H:%M:%S')
  tsec = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
  return int(tsec)

if __name__ == '__main__':
    
    inputvideofilesOrig = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
    randIdx=random.sample(range(0, len(inputvideofilesOrig)), len(inputvideofilesOrig))
   
    inputvideofiles=[]
    for Idx in randIdx:
        inputvideofiles.append(inputvideofilesOrig[Idx])
  
    clipslenOrig=[]
    for videofile in inputvideofiles:
        clipslenOrig.append(getLength(input_dir+videofile))  
    
    cnt=0
    print(clipslenOrig)
    
    osout = call('rm -rf {}'.format(output_dir))
    osout = call('mkdir {}'.format(output_dir))
    for cnt in range(len(clipslenOrig)):
        #print("\n\n\n\n {}").format(clipslenOrig[cnt])
        clipslenInc=float(clipslenOrig[cnt])/splits
        starttime=0
        cntInc=0
        while ((starttime+clipslenInc)<=clipslenOrig[cnt]):
           clipname=inputvideofiles[cnt]
           #print("input_dir={},clipname={},starttime={},clipslen={},input_dir_cropped={},clipname={},cntInc={}").format(input_dir,clipname,str(datetime.timedelta(seconds=starttime)),str(datetime.timedelta(seconds=(starttime+clipslenInc))),output_dir,clipname.split('.')[0],cntInc)
           osout = call('ffmpeg -y -i {}/{} -ss {}  -t {} -c:v libx264 -crf 0 {}/{}_split{}.avi'.format(input_dir,clipname,str(datetime.timedelta(seconds=starttime)),str(datetime.timedelta(seconds=(starttime+clipslenInc))),output_dir,clipname.split('.')[0],cntInc))
           starttime=starttime+clipslenInc
           cntInc=cntInc+1
           
           
