import os
import argparse
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import h5py
from astropy.time import Time

import orbitize.kepler as kepler
import orbitize.results as results

moduledir = os.path.dirname(__file__)
basedir = os.path.dirname(moduledir) # up one leve
datadir = os.path.join(basedir, "data")

from .catalog import (aliases, display_names, dyn_mass_single_comp, multi_dict,
                      position_notes, post_dict as public_post_dict)

# Optional private fits remain available through the API/CLI. The web menu
# uses public display_names, so a private module cannot expose new choices.
post_dict = public_post_dict.copy()

#### import any propritary data not stored here. 
try:
    import whereistheplanet.private_data as private_data
    private_dict = private_data.private_dict
    for key in private_dict:
        post_dict[key] = private_dict[key]
except:
    pass


def print_prediction(planet_name, date_mjd, chains, tau_ref_epoch, num_samples=None):
    """
    Prints out a prediction for the prediction of a planet given a set of posterior draws

    Args:
        planet_name (str): name of the planet, already checked to be in the list
        date_mjd (float): MJD of date for which we want a prediction
        chains (np.array): Nx8 array of N orbital elements. Orbital elements are ordered as:
                            sma, ecc, inc, aop, pan, tau, plx, mtot
        tau_ref_epoch (float): MJD for reference epoch of tau (see orbitize for details on tau)
        num_samples (int): number of random samples for prediction. If None, will use all of them

    Returns:
        ra_args (tuple): a two-element tuple of the median RA offset, and stddev of RA offset
        dec_args (tuple): a two-element tuple of the median Dec offset, and stddev of Dec offset
        sep_args (tuple): a two-element tuple of the median separation offset, and stddev of sep offset
        pa_args (tuple): a two-element tuple of the median PA offset, and stddev of PA offset
    """

    if num_samples is None:
        num_samples = chains.shape[0]
        rand_draws = np.arange(num_samples) # don't need to randomize
    else:
        # if num_samples > chains.shape[0]:
        #     print("Requested too many samples. Maximum is {0}.".format(chains.shape[0]))
        #     return
    
        # randomly draw values
        rand_draws = np.random.randint(0, chains.shape[0], num_samples)

    planet_name = resolve_name(planet_name)

    rand_orbits = chains[rand_draws]

    if planet_name not in multi_dict:
        # single Keplerian orbit fits
        sma = rand_orbits[:, 0]
        ecc = rand_orbits[:, 1]
        inc = rand_orbits[:, 2]
        aop = rand_orbits[:, 3]
        pan = rand_orbits[:, 4]
        tau = rand_orbits[:, 5]
        plx = rand_orbits[:, 6]
        mtot = rand_orbits[:, 7]

        if planet_name in dyn_mass_single_comp:
            mtot = np.sum(rand_orbits[:,[-2,-1]], axis=1)

        rand_ras, rand_decs, rand_vzs = kepler.calc_orbit(date_mjd, sma, ecc, inc, aop, pan, tau, plx, mtot,
                                                        tau_ref_epoch=tau_ref_epoch)
    else:
        # massive multi-planet orbit fits
        planet_num, tot_planets = multi_dict[planet_name]
        orb_indices = np.arange(6 * planet_num, 6 * planet_num+6, 1)
        sma, ecc, inc, aop, pan, tau = rand_orbits[:, orb_indices].T
        plx = rand_orbits[:, 6 * tot_planets]
        mass_planets = rand_orbits[:, -1-tot_planets:-1]
        mass_star = rand_orbits[:, -1]

        all_pl_smas = rand_orbits[:, 0:6*tot_planets:6]
        # The semi-major-axis ordering can change between posterior draws.
        # Determine enclosed masses separately for every draw.
        inside = all_pl_smas < sma[:, None]
        mtot = mass_star + mass_planets[:, planet_num] + np.sum(mass_planets * inside, axis=1)

        rand_ras, rand_decs, rand_vzs = kepler.calc_orbit(date_mjd, sma, ecc, inc, aop, pan, tau, plx, mtot,
                                                        tau_ref_epoch=tau_ref_epoch)

        # add perturbation from other planets
        for inner_pl in range(tot_planets):
            if inner_pl == planet_num:
                continue

            is_inner = inside[:, inner_pl]
            if not np.any(is_inner):
                continue
            within_inner_orbit = all_pl_smas < all_pl_smas[:, inner_pl, None]
            mass_inner = mass_planets[:, inner_pl]
            # The inner relative orbit is governed by both bodies' masses;
            # the same enclosed mass sets its stellar reflex fraction.
            inner_mtot = mass_star + mass_inner + np.sum(mass_planets * within_inner_orbit, axis=1)

            inner_orb_indices = np.arange(6 * inner_pl, 6 * inner_pl + 6, 1)
            in_sma, in_ecc, in_inc, in_aop, in_pan, in_tau = rand_orbits[:, inner_orb_indices].T

            inner_rand_ras, inner_rand_decs, inner_rand_vzs = kepler.calc_orbit(date_mjd, in_sma, in_ecc, in_inc, in_aop, in_pan, in_tau, plx, inner_mtot,
                                                          tau_ref_epoch=tau_ref_epoch)

            fraction = is_inner * mass_inner / inner_mtot
            rand_ras += fraction * inner_rand_ras
            rand_decs += fraction * inner_rand_decs
            rand_vzs += fraction * inner_rand_vzs

    rand_seps = np.sqrt(rand_ras**2 + rand_decs**2)
    rand_pas = np.degrees(np.arctan2(rand_ras, rand_decs)) % 360

    ra_args = np.median(rand_ras), np.std(rand_ras)
    dec_args = np.median(rand_decs), np.std(rand_decs)
    sep_args = np.median(rand_seps), np.std(rand_seps)
    # Keep a tight distribution crossing north tight (359.9 and 0.1 deg
    # are close). Report the center in the usual [0, 360) range.
    pa_center = np.angle(np.mean(np.exp(1j*np.radians(rand_pas))), deg=True)
    centered_pas = pa_center + (rand_pas-pa_center+180) % 360-180
    pa_args = np.median(centered_pas) % 360, np.std(centered_pas)
    rv_args = np.median(rand_vzs), np.std(rand_vzs)

    print("RA Offset = {0:.3f} +/- {1:.3f} mas".format(ra_args[0], ra_args[1]))
    print("Dec Offset = {0:.3f} +/- {1:.3f} mas".format(dec_args[0], dec_args[1]))
    print("Separation = {0:.3f} +/- {1:.3f} mas".format(sep_args[0], sep_args[1]))
    print("PA = {0:.3f} +/- {1:.3f} deg".format(pa_args[0], pa_args[1]))
    print("Planetary RV = {0:.3f} +/- {1:.3f} km/s".format(rv_args[0], rv_args[1]))

    return ra_args, dec_args, sep_args, pa_args

def resolve_name(planet_name):
    """Use the same canonical companion for API, CLI, and reference queries."""
    key = planet_name.strip().lower()
    return aliases.get(key, key)


def get_position_note(planet_name):
    """Describe reference frames that distinguish ambiguous companion names."""
    return position_notes.get(resolve_name(planet_name), "")


def print_supported_orbits():
    """
    Prints out to the screen currently supported orbits
    """
    # list all possible planet options
    # right now all possible orbits are in the keys to post_dict
    for name in post_dict:
        filename, reference = post_dict[name]
        print("    {0} ({1})".format(name, reference))
    return

def get_chains(planet_name):
    """
    Return posteriors for a given planet name

    Args:
        planet_name (str): name of planet. no space

    Returns:
        chains (np.array): Nx8 array of N posterior draws
        tau_ref_epoch (float): MJD for reference tau epoch
    """
    planet_name = resolve_name(planet_name)

    if planet_name not in post_dict:
        raise ValueError("Invalid planet name '{0}'".format(planet_name))
    
    filename, reference = post_dict[planet_name]
    filepath = os.path.join(datadir, filename)
    # Predicting from saved draws does not require rebuilding the fitting
    # System (which can require external HGCA files and create temp files).
    with h5py.File(filepath, 'r') as hf:
        if 'post' in hf and 'tau_ref_epoch' in hf.attrs:
            post = hf['post'][:]
            tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])
        else:
            res = results.Results()
            res.load_results(filepath)
            post, tau_ref_epoch = res.post, res.tau_ref_epoch
    post = np.array(post, dtype=float)

    return post, tau_ref_epoch

def get_reference(planet_name):
    """
    Return reference for a given planet's orbit fit

    Args:
        planet_name (str): name of planet. no space

    Returns:
        reference (str): Reference of orbit fit
    """
    planet_name = resolve_name(planet_name)

    if planet_name not in post_dict:
        raise ValueError("Invalid planet name '{0}'".format(planet_name))
    
    filename, reference = post_dict[planet_name]
    return reference

def predict_planet(planet_name, time_mjd=None, num_samples=100):
    """
    Tells you where the planet is

    Args:
        planet_name (str): name of planet. no space
        time_mjd (float): UT Time to evaluate at. Either MJD or YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS. Default is current time
        num_samples (int): number of samples to use consider when predicting the planet's location. Default is 100. 

    Returns:
        ra_args (tuple): a two-element tuple of the median RA offset, and stddev of RA offset
        dec_args (tuple): a two-element tuple of the median Dec offset, and stddev of Dec offset
        sep_args (tuple): a two-element tuple of the median separation offset, and stddev of sep offset
        pa_args (tuple): a two-element tuple of the median PA offset, and stddev of PA offset
    """
    if time_mjd is None:
        # use the current time
        time_mjd = Time.now().mjd
    else:
        # check if it is MJD. Otherwise astropy.time can read it and give MJD
        if "-" in str(time_mjd):
            # dashes mean not MJD. Probably formatted as a date
            time_mjd = Time(time_mjd).mjd
        else:
            time_mjd = float(time_mjd)

    # we always refer to lowercase planet names
    planet_name = resolve_name(planet_name)

    # do real stuff
    chains, tau_ref_epoch = get_chains(planet_name)

    ra_args, dec_args, sep_args, pa_args = print_prediction(planet_name, time_mjd, chains, tau_ref_epoch, num_samples=num_samples)

    note = get_position_note(planet_name)
    if note:
        print(note)

    return ra_args, dec_args, sep_args, pa_args


######### Main Function #########
def main():
    """
    Main script for command line usage
    """
    # parse input arguments
    parser = argparse.ArgumentParser(description='Predicts the location of a companion based on the current knowledge of its orbit')
    parser.add_argument("planet_name", help="Name of the planet. No spaces", default="",  nargs='?')
    parser.add_argument("-t", "--time", help="UT Time to evaluate at. Either MJD or YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
    parser.add_argument('-l', '--list', action='store_true', help='Lists all the possible orbits currently supported')
    parser.add_argument('-a', '--all', action='store_true', help='Makes prediction for all supported orbits')
    args = parser.parse_args()

    if args.list:
        print("Current supported orbits (reference in parenthesis):")
        print_supported_orbits()
    elif args.planet_name == "" and not args.all:
        print("No planet name passed in. Here are the currently supported ones (reference for the orbit fit in parenthesis):")
        print_supported_orbits()

    else:
        # perform regular functionality.
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
        
        # give us the answer
        if not args.all:
            # resolve aliases
            if args.planet_name.lower() in aliases:
                args.planet_name = aliases[args.planet_name.lower()]

            # standard case where the user didn't request all of the orbits
            predict_planet(args.planet_name, time_mjd=time_mjd)
        else:
            # give us all of them
            for planet_name in post_dict:
                print(planet_name)
                predict_planet(planet_name, time_mjd=time_mjd)


########## Command Line Function ##########
if __name__ == "__main__":
    main()
