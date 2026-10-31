import os
import argparse
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import h5py
from astropy.time import Time
from astropy import constants, units

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


def _sample_orbits(chains, num_samples):
    """Select posterior rows once so paths and date markers use the same draws."""
    if len(chains) == 0:
        raise ValueError("The posterior contains no orbit samples")
    if num_samples is None:
        return chains
    if not isinstance(num_samples, (int, np.integer)) or num_samples < 1:
        raise ValueError("num_samples must be a positive integer or None")
    return chains[np.random.randint(0, chains.shape[0], num_samples)]


def _orbit_parameters(planet_name, rand_orbits):
    """Extract this companion's elements and physical enclosed mass per draw."""
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

    return sma, ecc, inc, aop, pan, tau, plx, mtot


def _propagate_orbits(planet_name, date_mjd, rand_orbits, tau_ref_epoch):
    """Propagate saved draws with the same reference frame for plots and predictions."""
    parameters = _orbit_parameters(planet_name, rand_orbits)
    rand_ras, rand_decs, rand_vzs = kepler.calc_orbit(
        date_mjd, *parameters, tau_ref_epoch=tau_ref_epoch)

    if planet_name in multi_dict:
        planet_num, tot_planets = multi_dict[planet_name]
        sma, _, _, _, _, _, plx, _ = parameters
        mass_planets = rand_orbits[:, -1-tot_planets:-1]
        mass_star = rand_orbits[:, -1]
        all_pl_smas = rand_orbits[:, 0:6*tot_planets:6]
        inside = all_pl_smas < sma[:, None]

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

    return rand_ras, rand_decs, rand_vzs


def _summarize_positions(rand_ras, rand_decs):
    """Summarize offsets while treating position angle as a circular quantity."""
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
    return ra_args, dec_args, sep_args, pa_args


def print_prediction(planet_name, date_mjd, chains, tau_ref_epoch, num_samples=None):
    """Print and return median/stddev RA, Dec, separation and PA for saved draws.

    ``date_mjd`` and ``tau_ref_epoch`` are MJDs. Posterior columns follow the
    catalog's single-companion or joint-fit layout. ``num_samples=None`` uses
    every posterior row; a positive integer draws that many rows with replacement.
    """
    planet_name = resolve_name(planet_name)
    rand_orbits = _sample_orbits(chains, num_samples)
    rand_ras, rand_decs, rand_vzs = _propagate_orbits(
        planet_name, date_mjd, rand_orbits, tau_ref_epoch)
    ra_args, dec_args, sep_args, pa_args = _summarize_positions(rand_ras, rand_decs)
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


def _parse_time(time_mjd):
    """Accept an MJD or an Astropy-readable date, rejecting nonfinite epochs."""
    if time_mjd is None:
        return Time.now().mjd
    try:
        epoch = float(time_mjd)
    except (ValueError, TypeError):
        epoch = float(Time(time_mjd).mjd)
    if not np.isfinite(epoch):
        raise ValueError("Date must be finite")
    return epoch


def predict_orbit(planet_name, time_mjd=None, num_samples=100, num_points=256):
    """Sample full sky-projected orbits and positions at the requested date.

    Args:
        planet_name (str): catalog key or alias.
        time_mjd (float or str): MJD or date; defaults to the current time.
        num_samples (int or None): posterior draws (with replacement), or all rows.
        num_points (int): points along each orbit, at least four.

    Returns:
        dict: ``prediction`` has the same four median/stddev tuples as
        :func:`predict_planet`, calculated from the returned ``ra`` and ``dec``
        date-position samples in mas. ``ra_tracks``, ``dec_tracks`` (mas) and
        ``epochs`` (MJD) have shape (num_points, num_samples). ``period_days``
        holds each draw's period, and ``time_mjd`` is the requested epoch.

    Each path spans one companion period containing the requested date, from
    periastron to periastron. Uniform eccentric-anomaly sampling resolves highly
    eccentric ellipses. Joint fits include the same inner-companion stellar
    reflex correction as numerical predictions, so their apparent paths need
    not close after exactly one outer-companion period.
    """
    if not isinstance(num_points, (int, np.integer)) or num_points < 4:
        raise ValueError("num_points must be an integer of at least four")
    epoch = _parse_time(time_mjd)
    planet_name = resolve_name(planet_name)
    chains, tau_ref_epoch = get_chains(planet_name)
    orbits = _sample_orbits(chains, num_samples)
    parameters = _orbit_parameters(planet_name, orbits)
    sma, ecc, _, _, _, tau, _, mtot = parameters
    if (not np.isfinite(tau_ref_epoch) or
            not all(np.all(np.isfinite(value)) for value in parameters) or
            np.any(sma <= 0) or np.any(mtot <= 0) or
            np.any((ecc < 0) | (ecc >= 1))):
        raise ValueError("Full orbits require finite, bound orbital elements")
    periods = (2*np.pi*np.sqrt((sma*units.au)**3 /
               (constants.G*mtot*units.Msun))).to_value(units.day)
    if not np.all(np.isfinite(periods)) or np.any(periods <= 0):
        raise ValueError("Full orbits require finite, bound orbital elements")

    # Use each draw's own period and periastron, rather than median elements.
    # Work in floating-point MJD: some posterior periods span millions of years.
    cycles = np.floor((epoch-tau_ref_epoch)/periods-tau)
    periastron = tau_ref_epoch+(tau+cycles)*periods
    eccentric_anomaly = np.linspace(0, 2*np.pi, num_points)[:, None]
    mean_anomaly = eccentric_anomaly-ecc*np.sin(eccentric_anomaly)
    epochs = periastron+periods*mean_anomaly/(2*np.pi)
    ra_tracks = np.empty_like(epochs)
    dec_tracks = np.empty_like(epochs)
    # calc_orbit takes a common 1D epoch vector. Loop over the bounded set of
    # draws so each uses its own phase grid, including all joint-fit columns.
    for index in range(len(orbits)):
        ras, decs, _ = _propagate_orbits(
            planet_name, epochs[:, index], orbits[index:index+1], tau_ref_epoch)
        ra_tracks[:, index] = np.asarray(ras).reshape(-1)
        dec_tracks[:, index] = np.asarray(decs).reshape(-1)

    ras, decs, _ = _propagate_orbits(planet_name, epoch, orbits, tau_ref_epoch)
    if not all(np.all(np.isfinite(value)) for value in (ra_tracks, dec_tracks, ras, decs)):
        raise ValueError("Orbit propagation produced nonfinite sky positions")
    return {
        'prediction': _summarize_positions(ras, decs),
        'ra_tracks': ra_tracks,
        'dec_tracks': dec_tracks,
        'ra': np.asarray(ras).reshape(-1),
        'dec': np.asarray(decs).reshape(-1),
        'epochs': epochs,
        'period_days': periods,
        'time_mjd': epoch,
    }


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
    time_mjd = _parse_time(time_mjd)

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
