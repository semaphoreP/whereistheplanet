#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HD 72946 B on axis
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
    "star" :"HD 72946",
    "RA"   :"08:35:51.2665",
    "DEC"  :"+06:37:21.9706",
    "pmRA" : -136.543,
    "pmDEC": -138.166,
    "Kmag" : 5.497,
    "Hmag" : 5.609,
    "GSmag":  7,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["HD72946B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [8],
    "repeat": 8
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
