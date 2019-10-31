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
import createOBapi

timeOfObs=None # it means now

Observation={
    "runID" : "1104.C-0651(A)",
    "star" :"HD25535",
    "RA"   :"04:02:03.45083",
    "DEC"  :"-34:28:55.7772",
    "pmRA" :379.84,
    "pmDEC":-15.67,
    "Kmag" :5.240,
    "Hmag" :5.327,
    "GSmag":6.73,
    "resolution": "HIGH",
    "wollaston" : "OUT",
    "baseline" : "UTs",
    "vltitype" : "astrometry",
    }

Sequence_obs={
    "axis": "off",
    "planets": ["HD25535B"],
    "dit star": 1,
    "ndit star": 64,
    "dit planets": [1],
    "ndit planets": [64],
    "repeat": 2,
    "swap": True
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
