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
import createOBapi
import createOB

timeOfObs="2019-11-09" # it means now

Observation={
    "runID" : "1103.B-0626(B)", #"1104.C-0651(A)", #
    "star" :"HD23121",
    "RA"   :"03:42:04.13476", 
    "DEC"  :"-17:08:45.2805",
    "pmRA" :33.97,
    "pmDEC":-18.21,
    "Kmag" :6.434,
    "Hmag" :6.495,
    "GSmag":7.79,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD23121B"],
    "dit star": 3,
    "ndit star": 40,
    "dit planets": [30],
    "ndit planets": [8], # set to 4 in BOB
    "repeat": 2,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
