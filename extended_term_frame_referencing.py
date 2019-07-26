import numpy as np
import matplotlib.pyplot as plt
import cv2, os, sys, subprocess, pdb
import scenedetect, re
import datetime, math, time
import argparse
import scipy.io as sio
from numpy import *

FRMPERWIN = 1 ; INF = 9999999

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--f', type=str,
                    help='file name')

parser.add_argument('--fps', type=int,
                    help='frame rate (ffmpeg -r ?)')

parser.add_argument('--gp', type=int,
                    help='Guard Period')

parser.add_argument('--suffix', type=str,
                    help='suffix added to all output files')

parser.add_argument('--wpp', type=int,
                    help='Popularity weight')

parser.add_argument('--wd', type=int,
                    help='Dissimilarity weight')

parser.add_argument('--maxn', type=int,
                    help='Maximum Number of Stitching Frames')

parser.add_argument('--maxf', type=int,
                    help='Maximum umber of Frames to be considered')


args = parser.parse_args()

fn=args.f;
fps=args.fps;
GP=args.gp;
suffix=args.suffix;
wpp=args.wpp;
wd=args.wd;
MaxN=args.maxn;
Maxf=args.maxf;


def call(cmd):
    # proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen(cmd, \
                   stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

def export_frames(fn):
    osout = call('rm -rf pngall')
    osout = call('mkdir pngall')
    osout = call('ffmpeg -r 1 -i {} -r 1 -qp 0 pngall/%d.png'.format(fn)) ##no downsampling 1:1

    osout = call('rm -rf ../vid/out.mp4')
    osout = call('ls -v pngall/*.png') ; temp = osout[0]
    temp = temp.split('\n')[0:-1]
    if Maxf>0 :
       for cnt in range(Maxf+1,len(temp)+1):
       #print('{} ... {}'.format(cnt,len(temp)))
       #print('rm -rf pngall/{}.png'.format(cnt))
         osout = call('rm -rf pngall/{}.png'.format(cnt))

    osout = call('ls -v pngall/*.png') ; lfrmall = osout[0]
    lfrmall = lfrmall.split('\n')[0:-1]

    osout = call('ffmpeg -start_number 0 -i "pngall/%d.png" -c:v libx264 -qp 0 -vf "fps={},format=yuv420p" ../vid/out.mp4'.format(fps))
    return lfrmall

def window_similarity(win_0, win_1):
    lfrmsim = []
    if (type(win_0) == str and type(win_1) == str):
       lfrmsim.append(content_similarity(win_0, win_1))
    elif (type(win_0) == str and type(win_1) <> str):
       lfrmsim.append(content_similarity(win_0, win_1[0]))
    elif (type(win_0) <> str and type(win_1) == str):
       lfrmsim.append(content_similarity(win_0[0], win_1))
    else:
       lfrmsim.append(content_similarity(win_0[0], win_1[0]))
        
    return np.mean(lfrmsim)

def content_similarity(img_0, img_1):
    
    img1 = cv2.imread(img_0, 0)
    img2 = cv2.imread(img_1, 0)

    # Initiate SIFT detector
    orb = cv2.ORB_create(nfeatures=1000)
    #orb = cv2.ORB(nfeatures=1000)
    #print("{} ...... {}\n").format(img_0,img_1)

    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)
    #print(img_0);print(img_1);print(img1);print(img2)
    #print(des1)
    #print(des2)
    #pdb.set_trace()
    if (type(des1)==type(des2)):
    	# create BFMatcher object
    	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    	# Match descriptors.
    	matches = bf.match(des1,des2)
        #pdb.set_trace()
        #print("simind_1 matches={}").format(matches)

    	# Sort them in the order of their distance.
    	matches   = sorted(matches, key = lambda x:x.distance)
    	distances = [ _.distance for _ in matches if _.distance < 100]
        if not distances:
	   simind_1=INF
        else:
    	   simind_1    =  np.mean(distances)
           #simind_1    =  np.mean(distances)*len(distances)

        
        #pdb.set_trace()
    	#print("simind_1={}\n").format(simind_1)

    	# Match descriptors.
    	#matches = bf.match(des2,des1)
    	#pdb.set_trace()

    	# Sort them in the order of their distance.
    	#matches   = sorted(matches, key = lambda x:x.distance)
        #print("simind_2 matches={}").format(matches)

    	#distances = [ _.distance for _ in matches]
    	#simind_2    =  np.mean(distances)
        
        if math.isnan(simind_1):
          simind_1=INF

        simind_2=simind_1
    	simind = (simind_1 + simind_2)/float(2)
        #print("simind={}").format(simind)
	#print("dis1={}\n dis2={}...{}\n").format(des1,des2,simind)
    else:
        simind=INF
	#print("dis1={}\n dis2={}...{}\n").format(des1,des2,simind)

    # Draw first 10 matches.
    #img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10], flags=2)
    #plt.imshow(img3),plt.show()
    #pdb.set_trace()
    return simind

def make_windows(lfrm, numfrmwin):
    numfrm = len(lfrm) ; numwin = numfrm/numfrmwin
    lwin = []
    for i in range(0, numfrm, numfrmwin ): lwin.append(lfrm[i:i+numfrmwin])
    return lwin

def find_scene_cuts(fn):

    scene_list = []		# Modified by detect_scenes(...) below.
    
    cap = cv2.VideoCapture(fn)	
    # Make sure to check cap.isOpened() before continuing!

    # Usually use one detector, but multiple can be used.
    detector_list = [scenedetect.ContentDetector()]
    #detector_list = [scenedetect.ContentDetector(threshold = 30,min_scene_len = 1)]
    #detector_list = [scenedetect.ThresholdDetector(threshold = 1, min_percent = 0.95, min_scene_len = 1)]


    frames_read = scenedetect.detect_scenes(cap, scene_list, detector_list)

    # scene_list now contains the frame numbers of scene boundaries.
    #print(scene_list)

    # Ensure we release the VideoCapture object.
    cap.release()
    
    scene_list=np.array(scene_list) ;
    scene_list=scene_list+1;
    #print(scene_list)
    np.save(('../savenpy/'+fname+'_SceneCutFrames'+suffix),scene_list-1)

    win_sc=[];
    for i in range(0, len(scene_list)): 
        if Maxf > 0:
           if scene_list[i]<(Maxf+1):
               win_sc.append('pngall/'+str(scene_list[i])+'.png')
        else:
           win_sc.append('pngall/'+str(scene_list[i])+'.png')
    #print(win_sc)
    return win_sc

def comp_similarity(lwin_,lwin_sc_,lwinsim):
    #print(type(lwin_))
    for win in lwin_:
        #lwinsim_ = []
        now = datetime.datetime.now()
        print('{} ... {}   ({})').format(win,now.strftime("%Y-%m-%d %H:%M:%S"),(now.replace(microsecond=0)-time_begin.replace(microsecond=0)))
        for win_sc in lwin_sc_:
          s=re.search('(?<=/)\w+', str(win))
          iwin=int(s.group(0))
          s=re.search('(?<=/)\w+', str(win_sc))
          iwin_sc=int(s.group(0))
          #lwinsim[iwin-1][iwin_sc-1]=sliding_window_similarity(win, win_sc)[0]
	  #if iwin >= iwin_sc:
          lwinsim[iwin-1][iwin_sc-1]=window_similarity(win, win_sc)
	  #print('{}..&..{}=..{}').format(win,win_sc,lwinsim[iwin-1][iwin_sc-1])
          #lwinsim[iwin_sc-1][iwin-1]=lwinsim[iwin-1][iwin_sc-1]
    return lwinsim

def comp_dissimilarity(lwin_r,lwin_c,lwinsim):
    for win_r in lwin_r:
        now = datetime.datetime.now()
        print('{} ... {}').format(win_r,now.strftime("%Y-%m-%d %H:%M:%S"))
        for win_c in lwin_c:
          s=re.search('(?<=/)\w+', str(win_r))
          iwin_r=int(s.group(0))
          s=re.search('(?<=/)\w+', str(win_c))
          iwin_c=int(s.group(0))
          if window_similarity(win_r, win_c)==INF:
              lwinsim[iwin_r-1][iwin_c-1]=0
          else:
              lwinsim[iwin_r-1][iwin_c-1]=window_similarity(win_r, win_c)
    return lwinsim

if __name__ == '__main__':
    time_begin=datetime.datetime.now()
    np.set_printoptions(threshold=np.nan)
    #fn=sys.argv[-1]
    fname=fn.split('/')[2]
    fname=fname[0:(len(fname)-4)]
    lfrm = export_frames(fn);
    lfrmdel=lfrm[1];
    lwin = make_windows(lfrm, FRMPERWIN)
    lwinsim = []
    #print(lwin)
    lwin1 = find_scene_cuts(fn);
    #lwin1 = find_scene_cuts('../vid/out.mp4') ;
    #print(lwin1)
    #lwin1=map_to_downsampled(lwin1,fname)
    print(lwin1)
    print("Number of SC frames is {}").format(len(lwin1))
    
    #lwin1.append('pngall/1.png') ##it is no neccessary to have first frame part of the stitching frames
    lwin_sc = make_windows(lwin1, FRMPERWIN)
    lwinsim=np.full((len(lwin),len(lwin)), INF)
    lwindissim=np.full((len(lwin),len(lwin)), INF)
   
    LambdaPoP=0.0000001
    LambdaPoP=0
    WeightPicPos=LambdaPoP*(np.transpose(np.full((len(lwin),1),1)))*np.array(range(1,len(lwin)+1))
    
    #lwinsimNorm=lwinsim/np.matrix.max(lwinsim)
    np.set_printoptions(threshold=np.nan)
    #print(lwinsim.shape)
    #print(np.amax(np.amax(lwinsim)))
    #pdb.set_trace()
    if os.path.isfile('../savenpy/'+fname+'_lwinsim_'+str(MaxN)+'.npy'):
       #pdb.set_trace()
       print("Loading similarity score between SC and all frames")
       lwinsim=np.load(('../savenpy/'+fname+'_lwinsim.npy'))
       np.save(('../savenpy/'+fname+'_lwinsim'+suffix),lwinsim)
    else:
       # Get global window similarity matrix
       print("Computing similarity between SC and all frames")
       #pdb.set_trace()
       lwinsim=comp_similarity(lwin,lwin_sc,lwinsim)
       np.save(('../savenpy/'+fname+'_lwinsim_'+str(MaxN)),lwinsim)
       np.save(('../savenpy/'+fname+'_lwinsim'+suffix),lwinsim)
    lwinsim_0=np.copy(lwinsim)
    lwinsim_0[lwinsim_0==INF]=-1
    lwinsim_0[lwinsim_0==-1]=np.amax(np.amax(lwinsim_0))
    np.save(('../savenpy/'+fname+'_lwinsim_0'+suffix),lwinsim_0)
    lwinsim_0=((lwinsim_0.astype(float))/np.amax(np.amax(lwinsim_0)))
    np.save(('../savenpy/'+fname+'_lwinsimNormalized'+suffix),lwinsim_0)
    print(np.unique(lwinsim_0))
    print(np.mean(np.mean(lwinsim_0,0),0))
    lwinsim_0=lwinsim_0+WeightPicPos
    np.save(('../savenpy/'+fname+'_lwinsimNormalizedWeighted'+suffix),lwinsim_0)
    #print(np.mean(lwinsim,0))
    

    #pdb.set_trace()
    #print('\nWindow similarity matrix:') ; print(np.matrix(lwinsim))
    lwinsim=lwinsim[:,np.mean(lwinsim,axis=0)!=INF]
    lwin_popularity_index = [ 1/np.mean(_) for _ in lwinsim ]
    #lwin_popularity_index=lwin_popularity_index-np.min(np.min(lwin_popularity_index))
    lwin_popularity_index_Norm_temp=((lwin_popularity_index)/np.amax(np.amax(lwin_popularity_index)))
    lwin_popularity_index_Norm=lwin_popularity_index_Norm_temp+WeightPicPos
    lwin_popularity_index_Norm=np.transpose(lwin_popularity_index_Norm)
    #pdb.set_trace()

    #print(lwin_popularity_index)
    #lwin_popularity_index = np.mean(lwinsim,1)
    #print(lwin_popularity_index)
    #pdb.set_trace()
    lwin_opt_sorting = [] ; lwin_opt_sorting.append(np.argmax(lwin_popularity_index))
    lwin_opt_sorting_GP = [] ;
    for i in range(-GP,GP+1):
       if ((np.argmax(lwin_popularity_index_Norm)+i) > -1 ) and ((np.argmax(lwin_popularity_index_Norm)+i) < len(lwin_popularity_index_Norm)):
          lwin_opt_sorting_GP.append(np.argmax(lwin_popularity_index_Norm)+i)
    #pdb.set_trace()
    current_top_win_index = np.argmax(lwin_popularity_index_Norm) 
    #pdb.set_trace()
    current_top_win = lwin[current_top_win_index]
    #print('{}....{}').format(current_top_win_index,current_top_win)
    print('Producing Popularity-Dissimilarity List')
    if MaxN>0:
       nstitch=min(len(lwin_sc),MaxN-1)
    else:
       nstitch=len(lwin_sc)
    for i in range(0, nstitch):
        #####os.system('python ps_mem.py')
        #pdb.set_trace()
	#print('i={}....{}').format(i,current_top_win_index)
        # lwinsim_ = []
        # for win_ in lwin: lwinsim_.append(sliding_window_similarity(current_top_win, win_)[0])
        # lwin_popularity_index = [np.mean(_) for _ in lwinsim_]

        # for i in range(0, len(lwinsim)):
        # Find next candidates with maximum dissimilarity


        # next_candidates = lwin[np.argmax(lwinsim[current_top_win_index])]
        # next_candidates_indices = lwin[np.argmax(lwinsim[current_top_win_index])]

        # Make choice criterion list
        #pdb.set_trace()
        lwindissim=comp_dissimilarity(lwin[current_top_win_index],lwin,lwindissim)
        lwindissim_0=np.copy(lwindissim);
        lwindissim_test=np.copy(lwindissim_0);
        lwindissim_test[lwindissim_test==INF]=0
        if size(lwindissim_test[np.mean(lwindissim_test,axis=1)!=0,:])==0:
	   lwindissim_0[lwindissim_0==0]=1;
        #pdb.set_trace()
        lwindissim_0[lwindissim_0==INF]=0
        lwindissim_0=lwindissim_0[np.mean(lwindissim_0,axis=1)!=0,:]
        #lwindissim_0=lwindissim_0-np.min(np.min(lwindissim_0))
        lwindissimNorm=((lwindissim_0.astype(float))/np.amax(np.amax(lwindissim_0)))
        #print(np.mean(lwindissimNorm,axis=1))
        #print(np.mean(lwindissimNorm,axis=0))
        #print('\nWindow dissimilarity matrix:') ; print(np.matrix(lwindissim))
        next_candidate_criterion = np.array([((wd*dissimilarity)+(wpp*popularity)) for dissimilarity, popularity \
                                        in zip(np.min(lwindissimNorm,axis=0), lwin_popularity_index_Norm)])  ##consider dissimilarity with all previously selected current_top_win_indexs
        np.save(('../savenpy/'+fname+'next_candidate_criterion'+str(i)+suffix),next_candidate_criterion)
	#next_candidate_criterion = [dissimilarity/float(popularity) for dissimilarity, popularity \
        #                                in zip(lwindissim[current_top_win_index], lwin_popularity_index)] ##consider dissimilarity with only the current_top_win_index

        #print(next_candidate_criterion)
        # Sorted list indices
        #sorted_candidate_criterion = [ _[0] for _ in sorted(enumerate(np.transpose(next_candidate_criterion)), key=lambda x:x[1], reverse=True) ]
        #sorted_candidate_criterion_Index_Value = [ _ for _ in sorted(enumerate(next_candidate_criterion), key=lambda x:x[1], reverse=True) ]
        #pdb.set_trace()
        sorted_candidate_criterion = [ _[0] for _ in sorted(enumerate(next_candidate_criterion), key=lambda x:x[1], reverse=True) ]
        sorted_candidate_criterion_Index_Value = [ _ for _ in sorted(enumerate(next_candidate_criterion), key=lambda x:x[1], reverse=True) ]
        sorted_candidate_criterion_Index_Value=np.array(sorted_candidate_criterion_Index_Value)
        #pdb.set_trace()
        #print(sorted_candidate_criterion_Index_Value)
        # next_candidate = lwin[np.argmax(lwinsim[current_top_win_index])]
        #for next_candidate in sorted_candidate_criterion:

        #    if next_candidate not in lwin_opt_sorting:
        #       lwin_opt_sorting.append(next_candidate)
        #       current_top_win_index = next_candidate
        #pdb.set_trace()
        for next_candidate in sorted_candidate_criterion:
            if next_candidate not in lwin_opt_sorting_GP:
               lwin_opt_sorting.append(next_candidate)
               current_top_win_index = next_candidate
               for i in range(-GP,GP+1):
       		  if ((next_candidate+i) > -1 ) and ((next_candidate+i) < len(lwin)):
                     lwin_opt_sorting_GP.append(next_candidate+i)
               #pdb.set_trace()
               break
        #pdb.set_trace()
        lwin_opt_sorting_GP=list(np.unique(lwin_opt_sorting_GP))
        #pdb.set_trace()
        if len(lwin_opt_sorting_GP)==len(lwin):
	    break
        #print(lwin_opt_sorting)
        now = datetime.datetime.now()
        print('{} .... {}% ... {}   ({})'.format(lwin_opt_sorting,100*len(lwin_opt_sorting)/(nstitch+1),now.strftime("%Y-%m-%d %H:%M:%S"),(now.replace(microsecond=0)-time_begin.replace(microsecond=0))))
 
    #reprint the SC frames
    print("Number of SC frames is {}").format(len(lwin1))    
    print(lwin1)

    np.save(('../savenpy/'+fname+'_lwindissim'+suffix),lwindissim)
    np.save(('../savenpy/'+fname+'_lwindissim_0'+suffix),lwindissim_0)
    np.save(('../savenpy/'+fname+'_lwindissimNormalized'+suffix),lwindissimNorm)
    np.save(('../savenpy/'+fname+'_lwin_popularity_index_Norm'+suffix),lwin_popularity_index_Norm)
    np.save(('../savenpy/'+fname+'_lwin_popularity_index'+suffix),lwin_popularity_index)


    lwin_opt_sorting=np.array(lwin_opt_sorting)
    print('\nOPTIMAL Stitching frames:') ; print(lwin_opt_sorting)
    for i in range(0, len(lwin)):
      if i not in lwin_opt_sorting:
               lwin_opt_sorting=np.append(lwin_opt_sorting,i)
  
    #print('\nOPTIMAL HEVC GOP ORDER at Downsampled space:') ; print(lwin_opt_sorting)
    fid = open('OrderedFrames_'+fname+suffix+'.txt','w')
    for FNum in lwin_opt_sorting:
    	print >> fid, FNum
    #pdb.set_trace()

    np.save(('../savenpy/'+fname+'_lwin_opt_sorting'+suffix),lwin_opt_sorting)
