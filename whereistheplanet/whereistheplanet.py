import os
import argparse
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import h5py
from astropy.time import Time

import orbitize.kepler as kepler

moduledir = os.path.dirname(__file__)
basedir = os.path.dirname(moduledir) # up one leve
datadir = os.path.join(basedir, "data")

# name of all of the posteriors and reference
post_dict = {'hr8799b' : ("post_hr8799.hdf5", "GRAVITY (unpublished)"),
             'hr8799c' : ("post_hr8799.hdf5", "GRAVITY (unpublished)"),
             'hr8799d' : ("post_hr8799.hdf5", "GRAVITY (unpublished)"),
             'hr8799e' : ("post_hr8799.hdf5", "GRAVITY (unpublished)"),
             'betapicb' : ("post_betpic.hdf5", "Lacour et al. 2021"),
             'betapicc' : ("post_betpic.hdf5", "Lacour et al. 2021"),
             '51erib' : ('post_51erib.hdf5', 'De Rosa et al. 2019'),
             'hd206893b' : ("post_hd206893.hdf5", 'Hinkley et al. 2022'),
             'hd206893c' : ("post_hd206893.hdf5", 'Hinkley et al. 2022'),
             '1rxs0342+1216b' : ('post_1rxs0342+1216b.hdf5', 'Bowler et al. 2019'),
             '1rxs2351+3127b' : ('post_1rxs2351+3127b.hdf5', 'Bowler et al. 2019'),
             '1rxs1609b' : ('post_1rxs1609b.hdf5', 'Keck (unpublished)'),
             '2m1559+4403b' : ('post_2m1559+4403b.hdf5', 'Bowler et al. 2019'),
             'cd-352722b' : ('post_cd-352722b.hdf5', 'Bowler et al. 2019'),
             'dhtaub' : ('post_dhtaub.hdf5', 'Keck (unpublisehd)'),
             'gj504b' : ('post_gj504b.hdf5', 'Bowler et al. 2019'),
             'hd984b' : ('post_hd984b.hdf5', 'GRAVITY (unpublished)'),
             'hd1160b' : ('post_hd1160b.hdf5', 'Bowler et al. 2019'),
             'hd19467b' : ('post_hd19467b.hdf5', 'Brandt et al. 2021'),
             'hd23514b' : ('post_hd23514b.hdf5', 'Bowler et al. 2019'),
             'hd49197b' : ('post_hd49197b.hdf5', 'Bowler et al. 2019'),
             'hd95086b' : ('post_hd95086b.hdf5', 'Bowler et al. 2019'),
             'hip65426b' : ('post_hip65426b.hdf5', 'Bowler et al. 2019'),
             'hr2562b' : ('post_hr2562b.hdf5', 'Bowler et al. 2019'),
             'hr3549b' : ('post_hr3549b.hdf5', 'Bowler et al. 2019'),
             'kappaandb' : ('post_kappaandb.hdf5', 'Keck (unpublished)'),
             'pds70b' : ('post_pds70.hdf5', 'Wang et al. 2021'),
             'pds70c' : ('post_pds70.hdf5', 'Wang et al. 2021'),
             'pztelb' : ('post_pztelb.hdf5', 'Bowler et al. 2019'),
             'ross458b' : ('post_ross458b.hdf5', 'Bowler et al. 2019'),
             'twa5b' : ('post_twa5b.hdf5', 'Bowler et al. 2019'),
             'hip64892b' : ('post_hip64892b.hdf5', 'Cheetham et al. 2018'),
             '2m0103b': ("post_2m0103b.hdf5", "Blunt et al. 2017"),
             'roxs42b' : ("post_roxs42b.hdf5", "Bryan et al. 2016"),
             "roxs12b" : ("post_roxs12b.hdf5", "Bryan et al. 2016"),
             "gqlupb" : ("post_gqlupb.hdf5", "Ginski et al. 2014b"),
             "gsc6214-210b" : ("post_gsc6214-210b.hdf5", "Pearce et al. 2019"),
             "hip79098abb" : ("post_hip79098b.hdf5", "Kasper et al. 2019"),
             "gsc08047-00232b" : ("post_gsc08047-0023b.hdf5", "Ginski et al. 2014a"),
             "2m0122b" : ("post_2m0122b.hdf5", "Bryan et al. 2020"),
             "gj758b" : ("post_gj758b.hdf5", "Brandt et al. 2021"),
             "hd4747b" : ("post_hd4747b.hdf5", "Peretti et al. 2018"),
             "fwtauc" : ("post_fwtauc.hdf5", "Data: Kraus et al. 2013; Orbit: unpublished"),
             "hd284149abb" : ("post_hd284149abb.hdf5", "Data: Bonavita et al. 2017; Orbit: unpublished"),
             "hd72946b" : ("post_hd72946b.hdf5", "Brandt et al. 2021"),
             "hd13724b" : ("post_hd13724b.hdf5", "Brandt et al. 2021"),
             "gl229b" : ("post_gl229b.hdf5", "Brandt et al. 2021"),
             "hd33632b" : ("post_hd33632b.hdf5", "Brandt et al. 2021"),
             "hip78530b" : ("post_hip78530b.hdf5", "Lafreniere et al. 2011")}

# massive multi-planet orbit fit bookkeeping
# for each planet, keep track of index of planet and total number of planets in the orbit fits
multi_dict = {'pds70b': (0, 2),
              'pds70c': (1, 2),
              'betapicb': (0, 2),
              'betapicc': (1, 2),
              'hr8799b' : (0, 4),
              'hr8799c' : (1, 4),
              'hr8799d' : (2, 4),
              'hr8799e' : (3, 4),
              'hd206893b' : (0, 2),
              'hd206893c' : (1, 2)}

# alias of planet names
aliases = {'betpicb': "betapicb",
           'betpicc': "betapicc"}

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

        all_pl_smas = rand_orbits[0, 0:6*tot_planets:6]
        within_orbit = np.where(all_pl_smas <= all_pl_smas[planet_num])
        mtot = mass_star + np.sum(mass_planets[:, within_orbit[0]], axis=1)

        rand_ras, rand_decs, rand_vzs = kepler.calc_orbit(date_mjd, sma, ecc, inc, aop, pan, tau, plx, mtot,
                                                        tau_ref_epoch=tau_ref_epoch)

        # add perturbation from other planets
        for inner_pl in within_orbit[0]:
            if inner_pl == planet_num:
                continue
            
            within_inner_orbit = np.where(all_pl_smas < all_pl_smas[inner_pl])
            inner_mtot = mass_star + np.sum(mass_planets[:, within_inner_orbit[0]], axis=1)
            mass_inner = mass_planets[:, inner_pl]

            inner_orb_indices = np.arange(6 * inner_pl, 6 * inner_pl + 6, 1)
            in_sma, in_ecc, in_inc, in_aop, in_pan, in_tau = rand_orbits[:, inner_orb_indices].T

            inner_rand_ras, inner_rand_decs, inner_rand_vzs = kepler.calc_orbit(date_mjd, in_sma, in_ecc, in_inc, in_aop, in_pan, in_tau, plx, inner_mtot,
                                                          tau_ref_epoch=tau_ref_epoch)

            rand_ras += mass_inner/inner_mtot * inner_rand_ras
            rand_decs += mass_inner/inner_mtot * inner_rand_decs
            rand_vzs += mass_inner/inner_mtot * inner_rand_vzs

    rand_seps = np.sqrt(rand_ras**2 + rand_decs**2)
    rand_pas = np.degrees(np.arctan2(rand_ras, rand_decs)) % 360

    ra_args = np.median(rand_ras), np.std(rand_ras)
    dec_args = np.median(rand_decs), np.std(rand_decs)
    sep_args = np.median(rand_seps), np.std(rand_seps)
    pa_args = np.median(rand_pas), np.std(rand_pas)
    rv_args = np.median(rand_vzs), np.std(rand_vzs)

    print("RA Offset = {0:.3f} +/- {1:.3f} mas".format(ra_args[0], ra_args[1]))
    print("Dec Offset = {0:.3f} +/- {1:.3f} mas".format(dec_args[0], dec_args[1]))
    print("Separation = {0:.3f} +/- {1:.3f} mas".format(sep_args[0], sep_args[1]))
    print("PA = {0:.3f} +/- {1:.3f} deg".format(pa_args[0], pa_args[1]))
    print("Planetary RV = {0:.3f} +/- {1:.3f} km/s".format(rv_args[0], rv_args[1]))

    return ra_args, dec_args, sep_args, pa_args

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
    planet_name = planet_name.lower()

    if planet_name not in post_dict:
        raise ValueError("Invalid planet name '{0}'".format(planet_name))
    
    filename, reference = post_dict[planet_name]
    filepath = os.path.join(datadir, filename)
    with h5py.File(filepath,'r') as hf: # Opens file for reading
        post = np.array(hf.get('post'))
        tau_ref_epoch = float(hf.attrs['tau_ref_epoch'])
    
    return post, tau_ref_epoch

def get_reference(planet_name):
    """
    Return reference for a given planet's orbit fit

    Args:
        planet_name (str): name of planet. no space

    Returns:
        reference (str): Reference of orbit fit
    """
    planet_name = planet_name.lower()

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

    # do real stuff
    chains, tau_ref_epoch = get_chains(planet_name)

    ra_args, dec_args, sep_args, pa_args = print_prediction(planet_name, time_mjd, chains, tau_ref_epoch, num_samples=num_samples)

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
