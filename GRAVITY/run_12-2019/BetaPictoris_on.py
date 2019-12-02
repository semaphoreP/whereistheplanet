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

timeOfObs="2019-12-09"
#timeOfObs=None # it means now

Observation={
    "runID" : "1103.B-0626(B)", #'1104.C-0651(A)',
    "star" :"betapic",
    "RA"   :"05:47:17.0877",
    "DEC"  :"-51:03:59.44",
    "pmRA" :4.65,
    "pmDEC":83.10,
    "Kmag" :3.48,
    "Hmag" :3.51,
    "GSmag":3.86,
    "resolution": "HIGH",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2648618, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["betapicb"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [8],
    "repeat": 30
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
