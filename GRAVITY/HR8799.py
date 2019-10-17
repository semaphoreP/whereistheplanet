#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019

@author: slacour
"""

import os
import sys
filedir = os.path.dirname(os.path.realpath(__file__)) # gets the directory the current python script is in
sys.path.insert(0, filedir) # add parent dir to python path
from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB 

timeOfObs="2019-09-09"
timeOfObs=None # it means now
Observation={
    "runID" : "0103.B-0649(A)",
    "star" :"HR8799",
    "RA"   :"23:07:28.715",
    "DEC"  :"+21:08:03.302",
    "pmRA" :108.0,
    "pmDEC":-49.5,
    "Kmag" :5.24,
    "Hmag" :5.28,
    "GSmag":5.953,
    "resolution": "LOW",
    "wollaston" : "IN"
    }

Sequence_obs={
        # "1": {
                "axis": "on",
                "planets": ["HR8799e","HR8799c"],
                "dit star": 0.3,
                "ndit star": 64,
                "dit planets": [10,10],
                "ndit planets": [32,32],
                "repeat": 2,
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
createOB.CreateOB(seq)
#send_to_wgv(Observation["star"],"wgv")
