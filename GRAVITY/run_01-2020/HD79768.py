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
    "star" :"HD79768",
    "RA"   :"09:15:03.74396",
    "DEC"  :"-30:22:01.5585",
    "pmRA" :-9.42,
    "pmDEC":7.24,
    "Kmag" :7.481,
    "Hmag" :7.498,
    "GSmag":7.86,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : True, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD79768B"],
    "dit star": 3,
    "ndit star": 22,
    "dit planets": [10],
    "ndit planets": [6],
    "repeat": 1,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
