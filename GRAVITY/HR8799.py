#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019

@author: slacour
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence

timeOfObs="2019-09-09"
timeOfObs=None # it means now
Observation={
    "runID" : "0103.B-0032(D)",
    "star" :"HR8799",
    "RA"   :"23:07:28.715",
    "DEC"  :"+21:08:03.302",
    "pmRA" :108.0,
    "pmDEC":-49.5,
    "Kmag" :5.24,
    "Hmag" :5.28,
    "GSmag":5.953,
    "resolution": "LOW",
    "wollaston" : "IN"
    }

Sequence_obs={
        "1": {
                "axis": "on",
                "planets": ["HR8799e"],
                "dit star": 0.3,
                "ndit star": 64,
                "dit planets": [60],
                "ndit planets": [8],
                "repeat": 2
                },
        "2": {
                "axis": "off",
                "planets": ["HR8799e","HR8799d","HR8799c","HR8799b"],
                "dit planets": [30,30,30,30],
                "ndit planets": [8,8,8,8],
                "repeat": 4
                },
        "3": {
                "axis": "on",
                "planets": ["HR8799e"],
                "dit star": 0.3,
                "ndit star": 64,
                "dit planets": [60],
                "ndit planets": [8],
                "repeat": 2
                },
        }
        
seq=makeSequence(Sequence_obs,Observation,timeOfObs)
send_to_wgv(Observation["star"],"wgv")