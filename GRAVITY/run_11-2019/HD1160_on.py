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
    "star" : "HD1160",
    "RA"   : "00:15:57.30201",
    "DEC"  : "+04:15:04.0050",
    "pmRA" : 20.089,
    "pmDEC": -14.575,
    "Kmag" : 7.040,
    "Hmag" : 7.013,
    "GSmag": 7.119,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry"
    }

Sequence_obs={
    "axis": "on",
    "planets": ["HD1160B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [30],
    "ndit planets": [16],
    "repeat": 14
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
