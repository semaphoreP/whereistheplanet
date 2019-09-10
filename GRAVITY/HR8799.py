#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 16:55:02 2019

@author: slacour
"""

from numpy import *
from matplotlib.pyplot import *
from makeSequence import makeSequence


Observation={
    "runID" : "0103.B-0032(D)",
    "star" :"HR8799",
    "RA"   :"23:07:28.715",
    "DEC"  :"+21:08:03.302",
    "pmRA" :0.0,
    "pmDEC":0.0,
    "Kmag" :3.8,
    "Hmag" :6.5,
    "GSmag":4,
    "resolution": "MED",
    "wollaston" : "IN"
    }

Sequence_obs={
        "1": {
                "axis": "on",
                "planets": ["HR8799e"],
                "dit star": 0.3,
                "ndit star": 0.6,
                "dit planets": [60],
                "ndit planets": [6],
                "repeat": 4
                },
        "2": {
                "axis": "off",
                "planets": ["HR8799e","HR8799b"],
                "dit planets": [30,30],
                "ndit planets": [10,10],
                "repeat": 3
                },
        "3": {
                "axis": "on",
                "planets": ["HR8799e"],
                "dit star": 0.3,
                "ndit star": 64,
                "dit planets": [60],
                "ndit planets": [6],
                "repeat": 4
                },
        }
        
seq=makeSequence(Sequence_obs,Observation)
