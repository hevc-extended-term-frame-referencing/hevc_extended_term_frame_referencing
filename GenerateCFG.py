#python ./Compare_Rate_PSNR_Frame.py --fn1=../HMSsync/HMSResu --fn2=../HMSsync/HMSRe

from __future__ import division
import numpy as np
import os, sys, subprocess, pdb
import argparse, re
import matplotlib.pyplot as plt


# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')

# Optional argument
parser.add_argument('--rate', type=str,
                    help='rate in second')


args = parser.parse_args()

if __name__ == '__main__':
   ##Inputs
   Rate=args.rate;

   if 'M' in Rate:
     Rate=str(int(Rate[:-1])*1000000)
   elif 'K' in Rate:
     Rate=str(int(Rate[:-1])*1000)
   elif 'k' in Rate:
     Rate=str(int(Rate[:-1])*1000)

   fname='Distributed_GOP_Config_template.cfg'
   with open(fname) as f:
      fl = f.readlines()
      f.close()
   flnew=[]
   for l in fl:
     l=l.strip()
     if ((l[0:5]=='rate=') or (l[0:4]=='Rate=')):
       flnew.append('Rate='+Rate)
     elif '.dat' in l:
       l1=l.split('Rate')[0]
       flnew.append(l1+'Rate'+Rate+'.dat')
     else:
       flnew.append(l)
   #print(flnew)

   f=open('Distributed_GOP_Config.cfg','w')
   print >> f , "\n".join(str(l) for l in flnew)
   f.close()
   



