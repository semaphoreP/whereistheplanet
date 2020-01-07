#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR 2562 B on axis
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
    "star" :"HR 2562",
    "RA"   :"06:50:01.0154778405",
    "DEC"  :"-60:14:56.919001147",
    "pmRA" : 4.663,
    "pmDEC": 108.377,
    "Kmag" : 5.020,
    "Hmag" : 5.128,
    "GSmag": 6.098,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["hr2562b"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [10], #bypass p2 check, it should be 100
    "ndit planets": [32],
    "repeat": 24
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
