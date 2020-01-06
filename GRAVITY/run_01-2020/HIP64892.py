#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIP 64892 B on axis
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
    "star" :"HIP 64892",
    "RA"   :"13:18:05.1042056946",
    "DEC"  :"-44:03:19.376995020",
    "pmRA" : -30.666,
    "pmDEC": -20.272,
    "Kmag" : 6.832,
    "Hmag" : 6.879,
    "GSmag":  6.79,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["hip64892b"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [8],
    "repeat": 8
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
