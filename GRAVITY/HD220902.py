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
    "runID" : "60.A-9102(H)",
    "star" :"HD220902",
    "RA"   :"23:27:45.28775",
    "DEC"  :"-26:40:42.1723",
    "pmRA" :47.46,
    "pmDEC":-1.00,
    "Kmag" :7.205,
    "Hmag" :7.293,
    "GSmag":8.96,
    "resolution": "MED",
    "wollaston" : "OUT"
    }

Sequence_obs={
            "axis": "off",
            "planets": ["HD220902B"],
            "dit star": 10,
            "ndit star": 16,
            "dit planets": [10],
            "ndit planets": [16],
            "repeat": 2,
            "swap": True
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOBapi.CreateOBapi(seq)
