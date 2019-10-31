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
    "star" :"HR8799",
    "RA"   :"23:07:28.71569",
    "DEC"  :"+21:08:03.3021",
    "pmRA" :108.301,
    "pmDEC":-49.480,
    "Kmag" :5.240,
    "Hmag" :5.280,
    "GSmag":5.953,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
            "axis": "off",
            "planets": ["HR8799b", "HR8799c", "HR8799d", "HR8799e"],
            "dit star": 1,
            "ndit star": 64,
            "dit planets": [30, 30, 30, 30],
            "ndit planets": [16, 16, 16, 16],
            "repeat": 7,
            "swap": False
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
#createOBapi.CreateOBapi(seq)
createOB.CreateOB(seq)
