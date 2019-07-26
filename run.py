import numpy as np
import matplotlib.pyplot as plt
import cv2, os, sys, subprocess, pdb

FRMPERWIN = 3 ; INF = 999

def call(cmd):
    # proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
    proc = subprocess.Popen(cmd, \
                   stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)

def export_frames(fn):
    osout = call('rm -rf png'.format(fn))
    osout = call('mkdir png'.format(fn))
    osout = call('ffmpeg -i {} -qp 0 png/%d.png'.format(fn))
    osout = call('ls -v png/*.png') ; lfrm = osout[0] 
    lfrm = lfrm.split('\n')[0:-1]

    return lfrm

def sliding_window_similarity(win_0, win_1):

    def window_similarity(win_0, win_1):
        lfrmsim = []
        for i in range(0, len(win_0)): 
            lfrmsim.append(content_similarity(win_0[i], win_1[i]))
        return np.mean(lfrmsim)

    short_win_len = min(len(win_0), len(win_1))
    long_win_len  = max(len(win_0), len(win_1))

    if len(win_0) > len(win_1):
        short_win = win_1
        long_win  = win_0
    else:
        short_win = win_0
        long_win  = win_1

    # Slide windows and content_similarity(img_0, img_1)
    lwinsim = [] ; 
    win_margin = long_win_len - short_win_len + 1
    for i in range(0, win_margin):
        # print('Running for win_margin = {}'.format(i))
        lwinsim.append(window_similarity(short_win, long_win[i:i+short_win_len]))

    max_window_similarity = max(lwinsim)
    mean_window_similarity = np.mean(lwinsim)

    return (max_window_similarity, mean_window_similarity, lwinsim)


def content_similarity(img_0, img_1):

    img1 = cv2.imread(img_0, 0)          
    img2 = cv2.imread(img_1, 0)          

    # Initiate SIFT detector
    orb = cv2.ORB_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # Match descriptors.
    matches = bf.match(des1,des2)
    # pdb.set_trace()
    
    # Sort them in the order of their distance.
    matches   = sorted(matches, key = lambda x:x.distance)
    distances = [ _.distance for _ in matches]
    simind_1    =  np.mean(distances)
 
    # Match descriptors.
    matches = bf.match(des2,des1)
    # pdb.set_trace()
    
    # Sort them in the order of their distance.
    matches   = sorted(matches, key = lambda x:x.distance)
    distances = [ _.distance for _ in matches]
    simind_2    =  np.mean(distances)
    
    simind = (simind_1 + simind_2)/float(2)

    # Draw first 10 matches.
    # img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10], flags=2)
    # plt.imshow(img3),plt.show()

    return simind

def make_windows(lfrm, lframestamps):
    numfrm = len(lfrm) ; numwin = numfrm/numfrmwin
    lwin = []
    for i in range(0, numfrm, numfrmwin ): lwin.append(lfrm[i:i+numfrmwin])
    return lwin

def get_scene_windows(fn):
    
    lfrm = export_frames(fn) ; 
    def framestamp(timestamp):
        sec_ = int(float(timestamp.split(':')[0]))
        min_ = int(float(timestamp.split(':')[1]))
        hor_ = int(float(timestamp.split(':')[2]))
        fps = 10
        return ((sec_ + min_ * 60 + hor_ * (60^2)) * fps)

    osout = call('scenedetect --input {} --detector threshold --threshold 30'.format(fn))
    ltimestamps  = osout[0].strip().split('\n')[-1].split(',')
    lframestamps = [ framestamp(timestamp) for timestamp in ltimestamps ] 

    lwin = [] ; start_framestamp = 1
    for end_framestamp in lframestamps: 
        lwin.append([ 'png/{}.png'.format(i) for i in range(start_framestamp, end_framestamp) ])
        start_framestamp = end_framestamp

    end_framestamp = len(lfrm) - 1
    lwin.append([ 'png/{}.png'.format(i) for i in range(start_framestamp, end_framestamp) ])

    # pdb.set_trace() 
    return lwin


if __name__ == '__main__':

    # Apply scene detection and get windows to compare
    fn = sys.argv[-1] ; lwin = get_scene_windows(fn)
    def get_opt_permutation(lwin):
        # matches = content_similarity(sys.argv[-1], sys.argv[-2])
        # sim = sliding_window_similarity(['A.jpg','B.jpg'], ['B.jpg','C.jpg'])
        # lfrm = export_frames(sys.argv[-1]) ; lwin = make_windows(lfrm, FRMPERWIN)
        lwinsim = []

        # Get global window similarity matrix
        for win in lwin:
            lwinsim_ = []
            for win_ in lwin: lwinsim_.append(sliding_window_similarity(win, win_)[0]) # 0 for max
            lwinsim.append(lwinsim_)
        print('\nWindow similarity matrix:') ; print(np.matrix(lwinsim))

        # lwinfreq = [ np.mean(_) for _ in lwinsim ]
        lwin_popularity_index = [ np.mean(_) for _ in lwinsim ]

        lwin_opt_sorting = [] ; lwin_opt_sorting.append(np.argmin(lwin_popularity_index))
        current_top_win = lwin[np.argmin(lwin_popularity_index)]
        current_top_win_index = np.argmin(lwin_popularity_index)
        for i in range(0, len(lwin) - 1):
            # lwinsim_ = []
            # for win_ in lwin: lwinsim_.append(sliding_window_similarity(current_top_win, win_)[0])
            # lwin_popularity_index = [np.mean(_) for _ in lwinsim_]

            # for i in range(0, len(lwinsim)):
            # Find next candidates with maximum dissimilarity

            # next_candidates = lwin[np.argmax(lwinsim[current_top_win_index])]
            # next_candidates_indices = lwin[np.argmax(lwinsim[current_top_win_index])]

            # Make choice criterion list
            next_candidate_criterion = [dissimilarity/float(popularity) for dissimilarity, popularity \
                                            in zip(lwinsim[current_top_win_index], lwin_popularity_index)]
            # Sorted list indices
            sorted_candidate_criterion = [ _[0] for _ \
                  in sorted(enumerate(next_candidate_criterion), key=lambda x:x[1], reverse=True)]

            # next_candidate = lwin[np.argmax(lwinsim[current_top_win_index])]
            for next_candidate in sorted_candidate_criterion:

                if next_candidate not in lwin_opt_sorting:
                   lwin_opt_sorting.append(next_candidate)
                   current_top_win_index = next_candidate

        print('\nOptimal window sorting:') ; print(lwin_opt_sorting)
