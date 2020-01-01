#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HD 95086 b copied from 51 Eri b template
"""
import sys
sys.path.append("..")

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB
import createOBapi

timeOfObs="2020-01-06"
#timeOfObs=None # it means now

Observation={
    "runID" : "1104.C-0651(A)", #
    "star" :"HD95086",
    "RA"   :"10:57:03.0216129217",
    "DEC"  :"-68:40:02.446874288",
    "pmRA" :-41.136,
    "pmDEC":12.700,
    "Kmag" :6.789,
    "Hmag" :6.867,
    "GSmag":7.3092,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
            "axis": "on-off",
            "planets": ["hd95086b"],
            "dit star": 1,
            "ndit star": 64,
            "dit planets": [300], # bypass the p2 check, it should be 300
            "ndit planets": [4], # bypass the p2 check, it should be 4
            "repeat": 6,
            "swap": False
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
