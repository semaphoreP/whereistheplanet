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
    "star" : "HR2562",
    "RA"   : "06:50:01.01548",
    "DEC"  : "-60:14:56.9190",
    "pmRA" : 4.663,
    "pmDEC": 108.377,
    "Kmag" : 5.020,
    "Hmag" : 5.128,
    "GSmag": 6.098,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
    "axis": "on",
    "planets": ["HR2562B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [30],
    "ndit planets": [16],
    "repeat": 14
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
