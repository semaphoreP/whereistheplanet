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

timeOfObs=None # it means now

Observation={
    "runID" : "60.A-9102(H)",
    "star" :"HD220541",
    "RA"   :"23:24:23.87912",
    "DEC"  :"+14:28:44.7210",
    "pmRA" :16.564,
    "pmDEC":-16.970,
    "Kmag" :6.305,
    "Hmag" :6.371,
    "GSmag":7.60,
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline": "small",
    "vltitype": "astrometry"
    }

Sequence_obs={
    "axis": "on",
    "planets": ["HD220541B"],
    "dit star": 30,
    "ndit star": 12,
    "dit planets": [60],
    "ndit planets": [8],
    "repeat": 3
    }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
