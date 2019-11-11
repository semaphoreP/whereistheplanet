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

def send_to_wgv(star,computer):
    p=subprocess.Popen(["scp",filedir+"/OBs/"+star+".obd",computer+':targets/exoplanets/.'])
    sts=os.waitpid(p.pid,0)

def read_from_table(object_name, filename="look_up_objects.json"):
    """
    Read the coordinate information from the json table.

    Parameters
    ----------
    object_name : string
        The object name.
    filename : string
        The name of the look up table, which should be in JSON format.

    Returns
    -------
    coo : list
        The [RA, DEC] of the object for the offset of the secondary.
    """
    t = json.load(fp=open(filedir+"/"+filename, "r"))
    coo = t.get(object_name, None)
    return coo

def get_xy(planet_name,timeOfObs):
    print("\n****** {0} ******".format(planet_name))
    try:
        values=whereistheplanet.predict_planet(planet_name,timeOfObs)
        return values[0][0],values[1][0]
    except ValueError:
        print("The object ({0}) is not recognized as a planet, go for the look up table!".format(planet_name))
        coo = read_from_table(planet_name)
        if coo is None:
            raise ValueError("Cannot find the object ({0}) from the table!".format(planet_name))
        else:
            return coo[0], coo[1]

def makeSequence(seq,obs,timeOfObs):

    #######################################
    # 1 retreive observing block main parameters
    #######################################
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
    baseline=obs["baseline"] # ISS.BASELINE
    vltitype=obs["vltitype"] # ISS.VLTITYPE


    #######################################
    # 2 check observing sequence, looking for errors or inconsistency.
    #######################################
    planet1=seq["planets"][0]
    Nplanet=len(seq["planets"])
    if 'swap' not in seq:
        seq['swap'] = False
    if (Nplanet!=len(seq["dit planets"])|(Nplanet!=len(seq["ndit planets"]))) :
        raise ValueError("The sequence has a wrong number of planets/dit/ndits")
    if ((seq['axis']!="on")&(seq['axis']!="off")&(seq['axis']!="on-off")&(seq['axis']!="off-on")):
        raise ValueError("The sequence has wrong axis value (must be on, off, on-off, or off-on)")
    if ((seq['axis']=="on")&(seq['swap']==True)):
        raise ValueError("We do not swap in on-axis mode")
    if ((seq['axis']=="on-off")&(seq['swap']==True)):
        raise ValueError("We do not swap in on-off mode")
    if ((seq['axis']=="off-on")&(seq['swap']==True)):
        raise ValueError("We do not swap in off-on mode")
    if ((seq['swap']==True)&(Nplanet!=1)):
        raise ValueError("A swap can only be done with a single companion (here %i)"%Nplanet)

    #######################################
    # 3 Making the first template of the sequence (acquisition)
    #######################################
    Sequence_templates={
            "template1" :{
                    "type": "header",
                    "run ID": runID,
                    "OB name": star,
                    "Obs time": timeOfObs,
                    "mode": seq["axis"],
                    "template_ob_id" : obs.get('template_ob_id', None), # The ob with new instrument package
                    "calib": obs.get("calib", False), # Indicate whether it is a calibrator.
                    },
            "template2" :{
                    "type": "acquisition",
                    "star name": star,
                    "target name": planet1,
                    "RA": RA,
                    "DEC": DEC,
                    "pmRA": pmRA,
                    "pmDEC": pmDEC,
                    "K mag": Kmag,
                    "H mag": Hmag,
                    "resolution": resolution,
                    "wollaston": wollaston,
                    "GS mag": GSmag,
                    "baseline": baseline,
                    "vltitype": vltitype
                    }
            }

    if (seq["axis"]=="on"):
        RA_init, DEC_init=get_xy(seq["planets"][0],timeOfObs)
        #RA_init, DEC_init=0.0,0.0
        #for planets in seq["planets"]:
        #    RA, DEC=get_xy(planets,timeOfObs)
        #    RA_init += RA
        #    DEC_init += DEC
        ratio=0.01
        RA_init*=ratio
        DEC_init*=ratio
    if (seq["axis"]=="on-off"):
        RA_init, DEC_init=get_xy(planet1,timeOfObs)
        ratio=0.01
        RA_init*=ratio
        DEC_init*=ratio
        Sequence_templates["template2"]["target name"] = star
    if (seq["axis"]=="off-on"):
        RA_init, DEC_init=get_xy(planet1,timeOfObs)
    if seq["axis"]=="off":
        RA_init, DEC_init=get_xy(planet1,timeOfObs)

    Sequence_templates["template2"]["RA offset"]=RA_init
    Sequence_templates["template2"]["DEC offset"]=DEC_init

    #######################################
    # 4 Making templates for the on axis case
    #######################################
    if seq["axis"] == "on":
            for r in range(seq["repeat"]):
                new_template = {
                    "type": "observation",
                    "name science": star,
                    "RA offset":-RA_init,
                    "DEC offset":-DEC_init,
                    "DIT": seq["dit star"],
                    "NDIT": seq["ndit star"],
                    "sequence":"O",
                    }
                if r==(seq["repeat"])//2:
                        new_template["sequence"]="O S"
                Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

                for name,dit,ndit in zip(seq["planets"],seq["dit planets"],seq["ndit planets"]):
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
                "DIT": seq["dit star"],
                "NDIT": seq["ndit star"],
                "sequence":"O",
                }
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

    #######################################
    # 5 Making the templates for the off axis
    #######################################

    if ((seq["axis"] == "off") | (seq["axis"] == "on-off") | (seq["axis"] == "off-on") )&(seq['swap']==False):
        if (seq["axis"] == "on-off"):
            new_template = {
                "type": "observation",
                "name science": star,
                "RA offset": -RA_init,
                "DEC offset":-DEC_init,
                "DIT": seq["dit star"],
                "NDIT": seq["ndit star"],
                "sequence":"O",
                }
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
        for r in range(seq["repeat"]):
            for n in range(Nplanet):
                name,dit,ndit=seq["planets"][n],seq["dit planets"][n],seq["ndit planets"][n]
                RA_planet,DEC_planet=get_xy(name,timeOfObs)
                if np.sqrt((RA_planet-RA_init)**2+(DEC_planet-DEC_init)**2)>20:
                    RA_init=RA_planet
                    DEC_init=DEC_planet
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
                    "RA offset":RA_planet-RA_init,
                    "DEC offset":DEC_planet-DEC_init,
                    "DIT": dit,
                    "NDIT": ndit,
                    "sequence":"O",
                    }
                Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
        if (seq["axis"] == "off-on"):
            new_template = {
                "type": "dither",
                "name science": star,
                "mag science": Kmag,
                "RA offset":RA_init * 0.01,
                "DEC offset":DEC_init * 0.01,
                }
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template
            new_template = {
                "type": "observation",
                "name science": star,
                "RA offset":-RA_init * 0.01,
                "DEC offset":-DEC_init * 0.01,
                "DIT": seq["dit star"],
                "NDIT": seq["ndit star"],
                "sequence":"O",
                }
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template


    #######################################
    # 6 Making the templates for the swap
    #######################################

    if (seq["axis"] == "off")&(seq['swap']==True):
        for r in range(seq["repeat"]):
            new_template = {
                "type": "observation",
                "name science": seq["planets"][0],
                "RA offset":0.0,
                "DEC offset":0.0,
                "DIT": seq["dit planets"][0],
                "NDIT": seq["ndit planets"][0],
                "sequence":"O O",
                }
            if r == int(seq["repeat"]/2):
                new_template["sequence"]="O S O"
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

            new_template = {
                "type": "swap"
            }
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

            new_template = {
                "type": "observation",
                "name science": star,
                "RA offset":0.0,
                "DEC offset":0.0,
                "DIT": seq["dit star"],
                "NDIT": seq["ndit star"],
                "sequence":"O O",
                }
            if r == int(seq["repeat"]/2):
                new_template["sequence"]="O S O"
            Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

            if r < (seq["repeat"]-1):
                new_template = {
                    "type": "swap"
                }
                Sequence_templates["template%i"%(len(Sequence_templates)+1)]=new_template

    #######################################
    # 6 Calculating total time and making json file
    #######################################

    Total_time=0.0
    for n in range(len(Sequence_templates)):
        s=Sequence_templates["template%i"%(n+1)]
        if s["type"]=="acquisition":
            Total_time+=10
        if s["type"]=="swap":
            Total_time+=3
        if s["type"]=="dither":
            Total_time+=1
        if s["type"]=="observation":
            Total_time+=s["DIT"]*s["NDIT"]/60*1.1*len(s['sequence'].replace(' ',''))

    print("Estimated time for OB: %i hours, %i min"%(int(Total_time/60),int(Total_time%60)))

    with open(filedir+"/OBs/"+star+".json", 'w') as f:
        json.dump(Sequence_templates, f, sort_keys=True, indent=4)

    return Sequence_templates
