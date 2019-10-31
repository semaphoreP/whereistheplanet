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
import createOB

timeOfObs="2019-11-10"
#timeOfObs=None # it means now

Observation={
    "runID" : '1104.C-0651(A)',
    "star" : "HD206893",
    "RA"   : "21:45:21.90560",
    "DEC"  : "-12:47:00.0681",
    "pmRA" : 93.776,
    "pmDEC": 0.016,
    "Kmag" : 5.593,
    "Hmag" : 5.687,
    "GSmag": 6.67,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD206893b"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [30],
    "ndit planets": [16],
    "repeat": 16
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOB.CreateOB(seq)
