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
    "wollaston" : "OUT",
    "baseline" : "small",
    "vltitype" : "astrometry"
    }

Sequence_obs={
            "axis": "off",
            "planets": ["HR8799b", "HR8799c", "HR8799d", "HD8799e"],
            "dit star": 10,
            "ndit star": 16,
            "dit planets": [300, 300, 300, 300],
            "ndit planets": [4, 4, 4, 4],
            "repeat": 4,
            "swap": False
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
#createOBapi.CreateOBapi(seq)
createOB.CreateOB(seq)
