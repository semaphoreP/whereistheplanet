#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR 3549 B on axis
"""
import sys
sys.path.append("..")

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOBapi
import createOB

timeOfObs="2020-01-06"
#timeOfObs=None # it means now

Observation={
    "runID" : "1104.C-0651(A)", #'1104.C-0651(A)',
    "star" :"HR 3549",
    "RA"   :"08:53:03.7788",
    "DEC"  :"-56:38:58.13",
    "pmRA" : -22.321,
    "pmDEC": 35.882,
    "Kmag" : 6.044,
    "Hmag" : 6.047,
    "GSmag":  5.998,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["hr3549b"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [8],
    "repeat": 8
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
