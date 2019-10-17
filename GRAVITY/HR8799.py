#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019
Revised on Mon Oct 14 10:45:00 2019

@author: slacour -- Revised by Jinyi Shangguan
"""

import os
import sys
filedir = os.path.dirname(os.path.realpath(__file__)) # gets the directory the current python script is in
sys.path.insert(0, filedir) # add parent dir to python pathÒ
from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB
#import createOBapi

timeOfObs=None # it means now

Observation={
    "runID" : "60.A-9102(H)",
    "star" :"HR8799",
    "RA"   :"23:07:28.71569",
    "DEC"  :"+21:08:03.3021",
    "pmRA" :108.301,
    "pmDEC":-49.480,
    "Kmag" :5.240,
    "Hmag" :5.280,
    "GSmag":5.953,
    "resolution": "MED",
    "wollaston" : "OUT"
    }

Sequence_obs={
        # "1": {
            "axis": "on",
            "planets": ["HR8799c","HR8799d"],
            "dit star": 0.3,
            "ndit star": 64,
            "dit planets": [10, 10],
            "ndit planets": [32, 32],
            "repeat": 5,
            "swap": False
        #         },
        # "2": {
        #         "axis": "off",
        #         "planets": ["HR8799e","HR8799d","HR8799c","HR8799b"],
        #         "dit planets": [10,10,10,10],
        #         "ndit planets": [32,32,32,32],
        #         "repeat": 5
        #         "swap": False
        #         },
        # "3": {
        #         "axis": "on",
        #         "planets": ["HR8799e"],
        #         "dit star": 0.3,
        #         "ndit star": 64,
        #         "dit planets": [10],
        #         "ndit planets": [32],
        #         "repeat": 6
        #         "swap": False
        #         },
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
#createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
