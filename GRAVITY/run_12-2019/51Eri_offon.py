#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019
Revised on Mon Oct 14 10:45:00 2019

@author: slacour -- Revised by Jinyi Shangguan
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB
import createOBapi

timeOfObs="2019-12-09"
#timeOfObs=None # it means now

Observation={
    "runID" : "1103.B-0626(B)", #"1104.C-0651(A)", #"0104.B.0649(A)", #
    "star" :"51Eri",
    "RA"   :"04:37:36.13231",
    "DEC"  :"-02:28:24.7788",
    "pmRA" :44.352,
    "pmDEC":-63.833,
    "Kmag" :4.537,
    "Hmag" :4.770,
    "GSmag":5.209,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2648618, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
            "axis": "off-on",
            "planets": ["51erib"],
            "dit star": 1,
            "ndit star": 64,
            "dit planets": [100], # bypass the p2 check, it should be 300
            "ndit planets": [12], # bypass the p2 check, it should be 4
            "repeat": 12,
            "swap": False
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
