#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIP 65426 B modified from beta Pic b on-sequence.
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
    "star" :"HIP65426",
    "RA"   :"13:24:36.0982987288",
    "DEC"  :"-51:30:16.046513257",
    "pmRA" :-34.246,
    "pmDEC":-18.811,
    "Kmag" :6.771,
    "Hmag" : 6.853,
    "GSmag":6.98,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    "template_ob_id" : 2642031, # The ob with new instrument package
    "calib" : False, # Indicate whether this is a calibrator
    }

Sequence_obs={
    "axis": "on",
    "planets": ["hip65426b"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [100], #bypass p2 check, it should be 100
    "ndit planets": [4],
    "repeat": 12
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
