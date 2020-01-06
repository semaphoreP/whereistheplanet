#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration Binary for HD 95086
"""
import sys
sys.path.append("..")

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOBapi
import createOB

timeOfObs="2020-01-06" # it means now

Observation={
    "runID" : "1104.C-0651(A)", #"1103.B-0626(B)", #
    "star" :"HD106257",
    "RA"   :"12:13:36.80571",
    "DEC"  :"-33:47:34.5059",
    "pmRA" :11.48,
    "pmDEC":-15.21,
    "Kmag" :6.116,
    "Hmag" :6.143,
    "GSmag":6.408,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : True, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD106257B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [3],
    "ndit planets": [24],
    "repeat": 1,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
