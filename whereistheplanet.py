import os
import argparse
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import h5py
from astropy.time import Time

import orbitize.kepler as kepler

basedir = os.path.dirname(__file__)
datadir = os.path.join(basedir, "data")

def print_prediction(date_mjd, chains, tau_ref_epoch, num_samples=None):
    """
    Prints out a prediction for the prediction of a planet given a set of posterior draws

    Args:
        date_mjd (float): MJD of date for which we want a prediction
        chains (np.array): Nx8 array of N orbital elements. Orbital elements are ordered as:
                            sma, ecc, inc, aop, pan, tau, plx, mtot
        tau_ref_epoch (float): MJD for reference epoch of tau (see orbitize for details on tau)
        num_samples (int): number of random samples for prediction. If None, will use all of them
    """

    if num_samples is None:
        num_samples = chains.shape[0]
        rand_draws = np.arange(num_samples) # don't need to randomize
    else:
        if num_samples > chains.shape[0]:
            print("Requested too many samples. Maximum is {0}.".format(chains.shape[0]))
            return
    
        # randomly draw values
        rand_draws = np.random.randint(0, chains.shape[0], num_samples)

    rand_orbits = chains[rand_draws]

    sma = rand_orbits[:, 0]
    ecc = rand_orbits[:, 1]
    inc = rand_orbits[:, 2]
    aop = rand_orbits[:, 3]
    pan = rand_orbits[:, 4]
    tau = rand_orbits[:, 5]
    plx = rand_orbits[:, 6]
    mtot = rand_orbits[:, 7]

    rand_ras, rand_decs, rand_vzs = kepler.calc_orbit(date_mjd, sma, ecc, inc, aop, pan, tau, plx, mtot,
                                                     tau_ref_epoch=tau_ref_epoch)

    rand_seps = np.sqrt(rand_ras**2 + rand_decs**2)
    rand_pas = np.degrees(np.arctan2(rand_ras, rand_decs)) % 360

    print("RA Offset = {0:.3f} +/- {1:.3f} mas".format(np.mean(rand_ras), np.std(rand_ras)))
    print("Dec Offset = {0:.3f} +/- {1:.3f} mas".format(np.mean(rand_decs), np.std(rand_decs)))
    print("Separation = {0:.3f} +/- {1:.3f} mas".format(np.mean(rand_seps), np.std(rand_seps)))
    print("PA = {0:.3f} +/- {1:.3f} deg".format(np.mean(rand_pas), np.std(rand_pas)))


def get_chains(planet_name):
    """
    Return posteriors for a given planet name

    Args:
        planet_name (str): name of planet. no space

    Returns:
        chains (np.array): Nx8 array of N posterior draws
        tau_ref_epoch (float): MJD for reference tau epoch
    """

    if planet_name.lower() == 'hr8799b':
        filepath = os.path.join(datadir, "post_hr8799b.hdf5")
        with h5py.File(filepath,'r') as hf: # Opens file for reading
            post = np.array(hf.get('post'))
            tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])
    
    elif planet_name.lower() == 'hr8799c':
        filepath = os.path.join(datadir, "post_hr8799c.ecsv")
        with h5py.File(filepath,'r') as hf: # Opens file for reading
            post = np.array(hf.get('post'))
            tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])
    
    elif planet_name.lower() == 'hr8799d':
        filepath = os.path.join(datadir, "post_hr8799d.ecsv")
        with h5py.File(filepath,'r') as hf: # Opens file for reading
            post = np.array(hf.get('post'))
            tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])   
    
    elif planet_name.lower() == 'hr8799e':
        filepath = os.path.join(datadir, "post_hr8799e.ecsv")
        with h5py.File(filepath,'r') as hf: # Opens file for reading
            post = np.array(hf.get('post'))
            tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])

    return post, tau_ref_epoch



########## Main Function ##########

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("planet_name", help="Name of the planet. No spaces")
parser.add_argument("-t", "--time", help="UT Time to evaluate at. Either MJD or YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
args = parser.parse_args()

if args.time is None:
    # use the current time
    time_mjd = Time.now().mjd
else:
    # check if it is MJD. Otherwise astropy.time can read it and give MJD
    if "-" in args.time:
        # dashes mean not MJD. Probably formatted as a date
        time_mjd = Time(args.time).mjd
    else:
        time_mjd = float(args.time)

chains, tau_ref_epoch = get_chains(args.planet_name)

print_prediction(time_mjd, chains, tau_ref_epoch, num_samples=100)

