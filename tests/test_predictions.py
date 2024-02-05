"""
Testing the prediciton tool
"""
import subprocess
import numpy as np
import whereistheplanet.whereistheplanet as witp

def test_all_predictions():
    """
    Test all predictions to make sure the posteriors exist. 
    Checks the values produced are not nan
    """
    labels = witp.post_dict.keys()

    for name in labels:
        print(name)
        ra_args, dec_args, sep_args, pa_args = witp.predict_planet(name)
        assert np.all(~np.isnan(ra_args))
        assert np.all(~np.isnan(pa_args))

def test_cmd_line():
    """
    Test command line script
    """
    subprocess.run(['whereistheplanet', 'betpicb', '-t', '2022-01-01'])

if __name__ == "__main__":
    test_all_predictions()

