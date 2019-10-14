#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019

@author: slacour
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence,send_to_wgv
import createOB

timeOfObs="2019-09-09"
timeOfObs=None # it means now
Observation={
    "runID" : "0103.C-0649(D)",
    "star" :"HD206893",
    "RA"   :"21:45:21.9056",
    "DEC"  :"-12:47:00.068",
    "pmRA" :93.0,
    "pmDEC":00.0,
    "Kmag" :5.593,
    "Hmag" :5.687,
    "GSmag":6.67,
    "resolution": "MED",
    "wollaston" : "OUT"
    }

Sequence_obs={
        "1": {
                "axis": "on",
                "planets": ["HD206893b"],
                "dit star": 1,
                "ndit star": 48,
                "dit planets": [60],
                "ndit planets": [8],
                "repeat": 6
                },
        }

seq=makeSequence(Sequence_obs,Observation,timeOfObs)
createOB.CreateOB(seq)

send_to_wgv(Observation["star"],"wgv")
