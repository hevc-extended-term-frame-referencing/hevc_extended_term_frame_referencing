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

parser.add_argument('--output_filename', type=str,
                    help='videos output filename')

parser.add_argument('--infps', type=int,
                    help='input frames per second')

parser.add_argument('--outfps', type=int,
                    help='output frames per second')

parser.add_argument('--W', type=int,
                    help='video width')

parser.add_argument('--H', type=int,
                    help='video hight')

parser.add_argument('--vidd', type=int,
                    help='video duration in minutes')

parser.add_argument('--ctmin', type=int,
                    help='minimum duration of video clip in seconds')

parser.add_argument('--ctmax', type=int,
                    help='maximum duration of video clip in seconds')


args = parser.parse_args()

##Inputs
input_dir=args.input_dir;
output_dir=args.output_dir;
output_filename=args.output_filename;
infps=args.infps;
outfps=args.outfps;
width=args.W;
hight=args.H;
vidd=args.vidd;
ctmin=args.ctmin
ctmax=args.ctmax

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
    #print('total length of all videos is {} mins'.format(float(np.sum(np.array(clipslenOrig)))/60))
    #time.sleep(5)

    cnt=0
    clipslen=np.random.randint(ctmin, ctmax,len(inputvideofiles))
    x=(clipslen<clipslenOrig)+0
    clipslen=np.multiply(x,clipslen)+np.multiply(np.absolute(x-1),clipslenOrig)
    if (float(np.sum(clipslenOrig))/60 < vidd):
        clipslen=clipslenOrig
        print(clipslenOrig)
        print('The requested video duration ({} mins) is greater than the sum of duration of all video clips ({} mins), all clips are concatenated'.format(vidd,float(np.sum(clipslenOrig))/60))
        time.sleep(5)
    else:
        while ((float(np.sum((clipslen)))/60 > vidd) or (float(np.sum((clipslen)))/60 < 0.9*vidd)) :
           clipslen=np.random.randint(ctmin, ctmax+1,len(inputvideofiles))
           x=(clipslen<clipslenOrig)+0
           clipslen=np.multiply(x,clipslen)+np.multiply(np.absolute(x-1),clipslenOrig)
           cnt=cnt+1
           if (cnt > 99999):
               print('requested video duration can not be achieved, due to \n(1) reuqested video duration \n(2) the clips cropping margin (ctmin,ctmax)\n(3) of available video clipss')
               time.sleep(5)
               break

    clipstart=np.random.randint(0,ctmax,len(inputvideofiles))
    for cnt in range(len(clipslenOrig)):
           #print('{}...{}...{}...{}').format(cnt,clipstart[cnt],clipslen[cnt],clipslenOrig[cnt])
           if ((clipstart[cnt]+clipslen[cnt])>clipslenOrig[cnt]):
                 if (clipslen[cnt]==clipslenOrig[cnt]):
                     clipstart[cnt]=0
                 else:
                     clipstart[cnt]=np.random.randint(0,(clipslenOrig[cnt]-clipslen[cnt]),1)
           print('{}...{}...{}...{}').format(cnt,clipstart[cnt],clipslen[cnt],clipslenOrig[cnt])
    
    osout = call('rm -rf {}/cropped/'.format(output_dir))
    osout = call('mkdir {}/cropped/'.format(output_dir))
    input_dir_cropped=output_dir+'/cropped/'
    for cnt in range(len(clipslen)):
        clipname=inputvideofiles[cnt]
        osout = call('ffmpeg -y -i {}/{} -ss {}  -t {} -c:v libx264 -preset ultrafast -qp 0 -strict -2 {}/{}'.format(input_dir,clipname,str(datetime.timedelta(seconds=clipstart[cnt])),str(datetime.timedelta(seconds=clipslen[cnt])),input_dir_cropped,clipname))

    thefile = open('concat_clips_temp.txt', 'w')
    for videofile in inputvideofiles:
        thefile.write("file '{}/{}'\n".format(input_dir_cropped,videofile))
    thefile.close() 

    osout = call('rm {}/output_temp.mp4'.format(output_dir))
    osout = call('ffmpeg -f concat  -safe 0 -i concat_clips_temp.txt -c:v libx264 -strict -2 -qp 0 -c copy {}/output_temp.mp4'.format(output_dir))

    osout = call('rm {}/{}.mp4'.format(output_dir,output_filename))
    osout = call('ffmpeg -y -r {} -i {}/output_temp.mp4 -strict -2 -vf scale={}:{} -strict -2 -c:v libx264 -preset ultrafast -r {} -qp 0 {}/{}.mp4 -hide_banner'.format(infps,output_dir,width,hight,outfps,output_dir,output_filename))
   
    osout = call('rm {}/{}.yuv'.format(output_dir,output_filename))
    osout = call('ffmpeg -y -i {}/{}.mp4 -vcodec rawvideo -pix_fmt yuv420p {}/{}.yuv'.format(output_dir,output_filename,output_dir,output_filename))
    print('{}/{}.mp4 is generated'.format(output_dir,output_filename))
    print('{}/{}.yuv is generated'.format(output_dir,output_filename))
    
    print('======= summary =======')
    print('{}/{}.mp4 is generated'.format(output_dir,output_filename))
    print('{}/{}.yuv is generated'.format(output_dir,output_filename))
    print('Number of concatenated vido clips are {}'.format(len(clipslenOrig)))
    print('Total length of all video clips is {} mins'.format(float(np.sum(np.array(clipslenOrig)))/60))
    print('Total length of the generated mp4 video is {} mins'.format(float(getLength(output_dir+output_filename+'.mp4'))/60))

