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
    "star" :"HD89828",
    "RA"   :"10:21:35.85868",
    "DEC"  :"-22:31:42.6434",
    "pmRA" :-47.96,
    "pmDEC":-0.22,
    "Kmag" :6.253,
    "Hmag" :6.275,
    "GSmag":6.65,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : True, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD89828B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [1],
    "ndit planets": [64],
    "repeat": 2,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
