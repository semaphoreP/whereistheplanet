#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 11:59:30 2019

@author: slacour
"""

import os 
filedir = os.path.dirname(os.path.realpath(__file__)) # gets the directory the current python script is in
parent_dir = os.path.dirname(filedir) # up one leve
module_dir = os.path.join(parent_dir, "whereistheplanet")
import sys
sys.path.insert(0, module_dir) # add parent dir to python path
import whereistheplanet

import json
import numpy as np
import subprocess

def get_xy(planet_name,timeOfObs):
    if planet_name == "HD206893b":
        return 124,200
    values=whereistheplanet.predict_planet(planet_name,timeOfObs)
    return values[0][0],values[1][0]

def makeSequence(Sequence_obs,obs,timeOfObs):
    
    runID=obs["runID"]
    star=obs["star"]
    RA=obs["RA"]
    DEC=obs["DEC"]
    pmRA=obs["pmRA"]
    pmDEC=obs["pmDEC"]
    Kmag=obs["Kmag"]
    Hmag=obs["Hmag"]
    GSmag=obs["GSmag"]
    resolution=obs["resolution"]
    wollaston=obs["wollaston"]
    
    
    # check numbering of keys
    for n in np.arange(len(Sequence_obs))+1:
        if str(n) not in Sequence_obs:
            raise ValueError("Sequence numbering not correct, missing %i"%n)
    
    # check size arrays,
    for n in np.arange(len(Sequence_obs))+1:
        s=Sequence_obs[str(n)]
        if (len(s["planets"])!=len(s["dit planets"])|(len(s["planets"])!=len(s["ndit planets"]))) :
            raise ValueError("The sequence number %i has a wrong number of planets/dit/ndits"%n)
        if ((s['axis']!="on")&(s['axis']!="off")):
            raise ValueError("The sequence number %i has wrong axis value (must be on or off)"%n)
            
            
    # axis off or on
    
    # do test sur la sequence
            
    
    Sequence_templates={
            "template1" :{
                    "type": "header",
                    "run ID": runID,
                    "OB name": star,
                    "Obs time": timeOfObs,
                    },
            "template2" :{
                    "type": "acquisition",
                    "target name": star,
                    "RA": RA,
                    "DEC": DEC,
                    "pmRA": pmRA,
                    "pmDEC": pmDEC,
                    "K mag": Kmag,
                    "H mag": Hmag,
                    "resolution": resolution,
                    "wollaston": wollaston,
                    "GS mag": GSmag
                    }
            }
            
    RA_init,DEC_init=get_xy(Sequence_obs["1"]["planets"][0],timeOfObs)
    if Sequence_obs["1"]["axis"]=="on":
            RA_init/=100
            DEC_init/=100
    Sequence_templates["template2"]["RA offset"]=RA_init
    Sequence_templates["template2"]["DEC offset"]=DEC_init
            
    for seqN in range(len(Sequence_obs)):
        
        obs=Sequence_obs[str(seqN+1)]
        if obs["axis"] == "on":
            Nstart=len(Sequence_templates)
            if Nstart > 2:
                RA_init,DEC_init=get_xy(obs['planets'][0],timeOfObs)
                RA_init/=100
                DEC_init/=100
                new_template = {
                    "type": "dither",
                    "name science": obs['planets'][0],
                    "mag science": Kmag+9,
                    "RA offset":RA_init,
                    "DEC offset":DEC_init,
                    }
                Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
            for r in range(obs["repeat"]):
                new_template = {
                    "type": "observation",
                    "name science": star,
                    "RA offset":-RA_init,
                    "DEC offset":-DEC_init,
                    "DIT": obs["dit star"],
                    "NDIT": obs["ndit star"],
                    "sequence":"O",
                    }
                if (len(Sequence_templates)<=Nstart+1): new_template["sequence"]="O S"
                Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
                    
                for name,dit,ndit in zip(obs["planets"],obs["dit planets"],obs["ndit planets"]):
                    RA_planet,DEC_planet=get_xy(name,timeOfObs)
                    new_template = {
                        "type": "observation",
                        "name science": name,
                        "RA offset":RA_planet-RA_init,
                        "DEC offset":DEC_planet-DEC_init,
                        "DIT": dit,
                        "NDIT": ndit,
                        "sequence":"O",
                        }
                    Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
                    
            new_template = {
                "type": "observation",
                "name science": star,
                "RA offset":-RA_init,
                "DEC offset":-DEC_init,
                "DIT": obs["dit star"],
                "NDIT": obs["ndit star"],
                "sequence":"O",
                }
            if (len(Sequence_templates)<=Nstart+1): new_template["sequence"]="O"
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
                    
        
        if obs["axis"] == "off":
            for r in range(obs["repeat"]):
                for name,dit,ndit in zip(obs["planets"],obs["dit planets"],obs["ndit planets"]):
                    Nstart=len(Sequence_templates)
                    if Nstart > 2:
                        RA_init,DEC_init=get_xy(name,timeOfObs)
                        new_template = {
                            "type": "dither",
                            "name science": name,
                            "mag science": Kmag+9,
                            "RA offset":RA_init,
                            "DEC offset":DEC_init,
                            }
                        Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
                    new_template = {
                        "type": "observation",
                        "name science": name,
                        "RA offset":0.0,
                        "DEC offset":0.0,
                        "DIT": dit,
                        "NDIT": ndit,
                        "sequence":"O",
                        }
                    Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
                    
                    
    Total_time=0.0
    for n in range(len(Sequence_templates)):
        s=Sequence_templates["template%i"%(n+1)]
        if s["type"]=="acquisition":
            Total_time+=10
        if s["type"]=="dither":
            Total_time+=1
        if s["type"]=="observation":
            Total_time+=s["DIT"]*s["NDIT"]/60*1.1*len(s['sequence'].replace(' ',''))
            
    print("Estimated time for OB: %i hours, %i min"%(int(Total_time/60),int(Total_time%60)))
            
#    with open("OBs/"+star+".json", 'w') as f:
#        json.dump(Sequence_templates, f)
        
    return Sequence_templates
        
def send_to_wgv(star,computer):
    p=subprocess.Popen(["scp","OBs/"+star+".obd",computer+':targets/exoplanets/.'])
    sts=os.waitpid(p.pid,0)
