#python ./Compare_Rate_PSNR_Frame.py --fn1=../HMSsync/HMSResu --fn2=../HMSsync/HMSRe

from __future__ import division
import numpy as np
import os, sys, subprocess, pdb
import argparse, re
import matplotlib.pyplot as plt


# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--fn1', type=str,
                    help='file name of first Rate_PSNR file')

parser.add_argument('--Lfn1', type=str,
                    help='Label of legend in plots related to first Rate_PSNR file')

parser.add_argument('--fn2', type=str,
                    help='file name of second Rate_PSNR file')

parser.add_argument('--Lfn2', type=str,
                    help='Label of legend in plots related to second Rate_PSNR file')

args = parser.parse_args()

if __name__ == '__main__':
   ##Inputs
   fname1=args.fn1;
   fname2=args.fn2;
   Lfname1=args.Lfn1;
   Lfname2=args.Lfn2;
   #np.set_printoptions(threshold=np.nan)
   
   next_candidate_criterion_fn1=np.load((fname1))
   next_candidate_criterion_fn2=np.load((fname2))

   
   print(len(next_candidate_criterion_fn1))

   plt.subplot(3, 1, 1)
   plt.plot(range(len(next_candidate_criterion_fn1)),next_candidate_criterion_fn1,"r--")
   #plt.title('Comparing 2 videos')
   plt.xlabel('Frame Number')
   plt.ylabel('score of next_candidate_criterion')

   plt.subplot(3, 1, 2)
   plt.plot(range(len(next_candidate_criterion_fn2)),next_candidate_criterion_fn2,"b--")
   #plt.title('Comparing 2 videos')
   plt.xlabel('Frame Number')
   plt.ylabel('score of next_candidate_criterion')

   plt.subplot(3, 1, 3)
   plt.plot(range(len(next_candidate_criterion_fn1)),next_candidate_criterion_fn1,"r--")
   plt.plot(range(len(next_candidate_criterion_fn2)),next_candidate_criterion_fn2,"b--")
   plt.legend([Lfname1,Lfname2])
   #plt.title('Comparing 2 videos')
   plt.xlabel('Frame Number')
   plt.ylabel('score of next_candidate_criterion')

   plt.show()
   
