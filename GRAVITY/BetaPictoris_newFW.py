#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019

@author: slacour
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOBapi

timeOfObs="2019-09-09"
timeOfObs=None # it means now
Observation={
    "runID" : '0103.C-0183(C)',
    "star" :"betapic",
    "RA"   :"05:47:17.0877",
    "DEC"  :"-51:03:59.44",
    "pmRA" :93.0,
    "pmDEC":00.0,
    "Kmag" :5.593,
    "Hmag" :5.687,
    "GSmag":6.67,
    "resolution": "MED",
    "wollaston" : "OUT"
    }

Sequence_obs={
        "1": {
                "axis": "on",
                "planets": ["betapicb"],
                "dit star": 0.3,
                "ndit star": 64,
                "dit planets": [10],
                "ndit planets": [32],
                "repeat": 20
                },
        }
        
seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
