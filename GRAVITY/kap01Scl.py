#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019
Revised on Mon Oct 14 10:45:00 2019

@author: slacour -- Revised by Jinyi Shangguan
"""

import os
import sys
filedir = os.path.dirname(os.path.realpath(__file__)) # gets the directory the current python script is in
sys.path.insert(0, filedir) # add parent dir to python pathÒ
from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB
import createOBapi

timeOfObs=None # it means now

Observation={
    "runID" : "60.A-9102(H)",
    "star" :"kap01 Scl",
    "RA"   :"00:09:21.06696",
    "DEC"  :"-27:59:16.5322",
    "pmRA" :70.11,
    "pmDEC":-8.97,
    "Kmag" :4.384,
    "Hmag" :4.513,
    "GSmag":5.51, # From 2008MNRAS.389..869E
    "resolution": "MED",
    "wollaston" : "OUT",
    "baseline" : "small",
    "vltitype" : "astrometry"
    }

Sequence_obs={
                "axis": "off", #"on", #
                "planets": ["kap01SclB"],
                "dit star": 10,
                "ndit star": 24,
                "dit planets": [10],
                "ndit planets": [24],
                "repeat": 2,
                "swap": True
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
#createOB.CreateOB(seq)
