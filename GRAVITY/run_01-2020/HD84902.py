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
    "star" :"HD84902",
    "RA"   :"09:47:28.63141",
    "DEC"  :"-37:43:28.2832",
    "pmRA" :-3.31,
    "pmDEC":-12.10,
    "Kmag" :6.274,
    "Hmag" :6.328,
    "GSmag":7.69,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : True, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD84902B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [10],
    "ndit planets": [8],
    "repeat": 1,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
