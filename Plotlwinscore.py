#python ./Compare_Rate_PSNR_Frame.py --fn1=../HMSsync/HMSResu --fn2=../HMSsync/HMSRe

from __future__ import division
import numpy as np
import os, sys, subprocess, pdb
import argparse, re, time
import matplotlib.pyplot as plt


# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--fn1', type=str,
                    help='file name of first Rate_PSNR file')

parser.add_argument('--Lfn1', type=str,
                    help='Label of legend in plots related to first Rate_PSNR file')

parser.add_argument('--axes', type=int,
                    help='Plot data across this axes')

args = parser.parse_args()

if __name__ == '__main__':
   ##Inputs
   fname1=args.fn1;
   Lfname1=args.Lfn1;
   axes_fn1=args.axes;
   #np.set_printoptions(threshold=np.nan)
   
   lwinscore_fn1=np.load((fname1))

   print(np.shape(lwinscore_fn1))

   if axes_fn1==0:
      for  cnt in range(np.shape(lwinscore_fn1)[1]):
          if len(np.unique(lwinscore_fn1[:][cnt]))!=1:
              plt.subplot(2, 1, 1)
              plt.plot(range(np.shape(lwinscore_fn1)[0]),lwinscore_fn1[:][cnt],"r--")
              plt.title('SIFT Score with Frame #'+str(cnt))
              plt.xlabel('Frame Number')
              plt.ylabel('SIFT Score')
              plt.legend([Lfname1])
              plt.subplot(2, 1, 2)
              plt.plot(range(np.shape(lwinscore_fn1)[0]),np.mean(lwinscore_fn1,1),"r--")
              plt.title('average SIFT Score')
              plt.xlabel('Frame Number')
              plt.ylabel('Average SIFT Score') 
              plt.show()
   else:
      for  cnt in range(np.shape(lwinscore_fn1)[0]):
          if len(np.unique(lwinscore_fn1[cnt][:]))!=1:
              plt.subplot(2, 1, 1)
              plt.plot(range(np.shape(lwinscore_fn1)[1]),lwinscore_fn1[cnt][:],"b--")
              plt.title('SIFT Score with Frame #'+str(cnt))
              plt.xlabel('Frame Number')
              plt.ylabel('SIFT Score')
              plt.legend([Lfname1])
              plt.subplot(2, 1, 2)
              plt.plot(range(np.shape(lwinscore_fn1)[1]),np.mean(lwinscore_fn1,0),"r--")
              plt.title('average SIFT Score')
              plt.xlabel('Frame Number')
              plt.ylabel('Average SIFT Score') 
              plt.show()

   #plt.subplot(3, 1, 1)
   #plt.plot(range(len(next_candidate_criterion_fn1)),next_candidate_criterion_fn1,"r--")
   #plt.title('Comparing 2 videos')
   #plt.xlabel('Frame Number')
   #plt.ylabel('score of next_candidate_criterion')

   #plt.subplot(3, 1, 2)
   #plt.plot(range(len(next_candidate_criterion_fn2)),next_candidate_criterion_fn2,"b--")
   #plt.title('Comparing 2 videos')
   #plt.xlabel('Frame Number')
   #plt.ylabel('score of next_candidate_criterion')

   #plt.subplot(3, 1, 3)
   #plt.plot(range(len(next_candidate_criterion_fn1)),next_candidate_criterion_fn1,"r--")
   #plt.plot(range(len(next_candidate_criterion_fn2)),next_candidate_criterion_fn2,"b--")
   #plt.legend([Lfname1,Lfname2])
   #plt.title('Comparing 2 videos')
   #plt.xlabel('Frame Number')
   #plt.ylabel('score of next_candidate_criterion')


   
