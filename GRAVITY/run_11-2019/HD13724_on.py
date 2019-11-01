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
    "star" : "HD13724",
    "RA"   : "02:12:20.67740",
    "DEC"  : "-46:48:58.9566",
    "pmRA" : -30.714,
    "pmDEC": -68.967,
    "Kmag" : 6.378,
    "Hmag" : 6.482,
    "GSmag": 7.87,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
    "axis": "on",
    "planets": ["HD13724B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [30],
    "ndit planets": [16],
    "repeat": 14
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOB.CreateOB(seq)
