"""A stellar inner companion must contribute to its own relative orbit mass."""
import numpy as np
from astropy import constants, units

import whereistheplanet.whereistheplanet as witp


def test_stellar_inner_reflex_matches_circular_two_body_solution(monkeypatch):
    # Face-on circular orbits have an analytic sky projection, so this
    # regression does not reuse the application's Kepler solver. Vary the
    # inner mass across posterior rows to exercise sample-dependent masses.
    post = np.zeros((3, 16))
    post[:, 0], post[:, 6], post[:, 12] = 1., 12., 50.
    post[:, 13], post[:, 14], post[:, 15] = [.5, 1., 1.5], .05, 1.
    inner_mass, outer_mass, star_mass = post[:, 13:].T
    ref, elapsed = 58849., 100.

    def circular_position(a_au, total_mass_msun):
        period = (2*np.pi*np.sqrt((a_au*units.au)**3 /
                  (constants.G*total_mass_msun*units.Msun))).to_value(units.day)
        phase = 2*np.pi*elapsed/period
        return 50*a_au*np.sin(phase), 50*a_au*np.cos(phase)

    outer_ra, outer_dec = circular_position(12., star_mass+inner_mass+outer_mass)
    inner_ra, inner_dec = circular_position(1., star_mass+inner_mass)
    fraction = inner_mass/(star_mass+inner_mass)
    ra, dec = outer_ra+fraction*inner_ra, outer_dec+fraction*inner_dec
    expected = [(np.median(value), np.std(value)) for value in
                (ra, dec, np.hypot(ra, dec), np.degrees(np.arctan2(ra, dec)) % 360)]
    monkeypatch.setitem(witp.multi_dict, '_stellar_inner_reflex', (1, 2))
    actual = witp.print_prediction('_stellar_inner_reflex', ref+elapsed, post, ref)
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-6)


def test_reflex_hierarchy_is_decided_per_posterior_draw(monkeypatch):
    # Body 2 is the outer object in row 0 and the inner one in row 1.
    # The exact circular solution checks both enclosed mass and masking
    # of the extra stellar-reflex displacement.
    post = np.zeros((2, 16))
    post[:, 0], post[:, 6], post[:, 12] = [1., 12.], [12., 1.], 50.
    post[:, 13], post[:, 14], post[:, 15] = .5, .05, 1.
    ref, elapsed = 58849., 100.

    def circular(a, mass):
        period = (2*np.pi*np.sqrt((a*units.au)**3 /
                  (constants.G*mass*units.Msun))).to_value(units.day)
        phase = 2*np.pi*elapsed/period
        return 50*a*np.sin(phase), 50*a*np.cos(phase)

    ra0, dec0 = circular(12., 1.55)
    ira, idec = circular(1., 1.5)
    ra1, dec1 = circular(1., 1.05)
    ra, dec = np.array([ra0+ira/3, ra1]), np.array([dec0+idec/3, dec1])
    monkeypatch.setitem(witp.multi_dict, '_crossing_hierarchy', (1, 2))
    actual = witp.print_prediction('_crossing_hierarchy', ref+elapsed, post, ref)
    np.testing.assert_allclose(actual[:3], [(np.median(x), np.std(x)) for x in
                                          (ra, dec, np.hypot(ra, dec))], atol=1e-6, rtol=0)
