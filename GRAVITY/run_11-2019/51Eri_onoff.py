#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019
Revised on Mon Oct 14 10:45:00 2019

@author: slacour -- Revised by Jinyi Shangguan
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB
import createOBapi

timeOfObs="2019-11-10"
#timeOfObs=None # it means now

Observation={
    "runID" : "1104.C-0651(A)",
    "star" :"51Eri",
    "RA"   :"04:37:36.13231",
    "DEC"  :"-02:28:24.7788",
    "pmRA" :44.352,
    "pmDEC":-63.833,
    "Kmag" :4.537,
    "Hmag" :4.770,
    "GSmag":5.209,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
            "axis": "on-off",
            "planets": ["51erib"],
            "dit star": 1,
            "ndit star": 64,
            "dit planets": [300],
            "ndit planets": [4],
            "repeat": 6,
            "swap": False
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
#createOBapi.CreateOBapi(seq)
createOB.CreateOB(seq)
