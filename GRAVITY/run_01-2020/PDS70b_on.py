#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDS 70 b on axis
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
    "star" :"PDS 70",
    "RA"   :"14:08:10.15",
    "DEC"  :"-41:23:52.57",
    "pmRA" : -29.661,
    "pmDEC": -23.823,
    "Kmag" :8.542,
    "Hmag" :8.823,
    "GSmag":12.199,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["pds70b"],
    "dit star": 10,
    "ndit star": 8,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [8],
    "repeat": 12
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
