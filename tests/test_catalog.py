"""Predictions must select the intended orbit and its component masses."""
import importlib
from pathlib import Path
import configparser

import h5py
import numpy as np
import pytest
from astropy import constants, units

import whereistheplanet.whereistheplanet as witp
from whereistheplanet.catalog import CATALOG


def test_dynamic_single_uses_component_masses_after_rv_columns(monkeypatch, tmp_path):
    # A face-on circular orbit is an analytic mass/period check. The large
    # column-7 RV zero point must not be interpreted as the total mass.
    post = np.zeros((2, 15))
    post[:, 0], post[:, 6], post[:, 7] = 3., 40., 100.
    post[:, -2], post[:, -1] = [.1, .4], [1., 1.2]
    with h5py.File(tmp_path/'test.hdf5', 'w') as hf:
        hf['post'] = post
        hf.attrs['tau_ref_epoch'] = 58849.
    monkeypatch.setattr(witp, 'datadir', str(tmp_path))
    monkeypatch.setitem(witp.post_dict, '_test_mass', ('test.hdf5', 'test'))
    monkeypatch.setattr(witp, 'dyn_mass_single_comp', witp.dyn_mass_single_comp+['_test_mass'])
    loaded, ref = witp.get_chains('_test_mass')
    period = (2*np.pi*np.sqrt((3*units.au)**3 /
              (constants.G*np.sum(post[:, -2:], axis=1)*units.Msun))).to_value(units.day)
    phase = 2*np.pi*100/period
    expected_ra, expected_dec = 120*np.sin(phase), 120*np.cos(phase)
    answer = witp.print_prediction('_test_mass', ref+100, loaded, ref)
    np.testing.assert_allclose(answer[:2], [(np.median(x), np.std(x)) for x in
                                          (expected_ra, expected_dec)], atol=1e-6, rtol=0)


def test_north_crossing_pa_uncertainty_stays_small():
    post = np.zeros((2, 8))
    post[:, 0], post[:, 6], post[:, 7] = 1., 10., 1.
    post[:, 3] = np.radians([359.9, .1])
    *_, pa = witp.print_prediction('_test_north', 58849., post, 58849.)
    assert abs((pa[0]+180) % 360-180) < 1e-10
    assert pa[1] == pytest.approx(.1)


def test_aliases_resolve_through_library_and_references():
    assert witp.multi_dict['hd284149abb'] == (1, 2)
    assert witp.multi_dict['14herc'] == (1, 2)
    assert witp.post_dict['vhs1256b'][0] != witp.post_dict['vhs1256ab'][0]
    for alias in ['EPSINDAB', 'betpicb', 'betpicd', 'HD284149b', 'vhs1256+1257b']:
        canonical = witp.resolve_name(alias)
        actual, ref = witp.get_chains(alias)
        expected, expected_ref = witp.get_chains(canonical)
        np.testing.assert_array_equal(actual, expected)
        assert ref == expected_ref
        assert witp.get_reference(alias) == witp.get_reference(canonical)
        np.testing.assert_allclose(witp.predict_planet(alias, '2025-01-01', num_samples=None),
                                   witp.predict_planet(canonical, '2025-01-01', num_samples=None))


@pytest.fixture
def webapp(monkeypatch):
    # Import the real app with an ephemeral test secret; no flask.ini is
    # required and no user secret is read or changed.
    def read_test_config(self, *args, **kwargs):
        self.read_dict({'DEFAULT': {'token': 'test-only-key'}})
        return []
    monkeypatch.setattr(configparser.ConfigParser, 'read', read_test_config)
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    pytest.importorskip('flask')
    pytest.importorskip('flask_wtf')
    pytest.importorskip('wtforms')
    module = importlib.import_module('app')
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return module


def test_web_catalog_and_reference_frames(webapp):
    assert dict(webapp.multchoices[1:]) == {key: row[2] for key, row in CATALOG.items()}
    client = webapp.app.test_client()
    page = client.get('/')
    assert page.status_code == 200
    assert b'epsilon Indi Ab' in page.data
    assert b'VHS 1256 (AB)b (wide planet)' in page.data
    for target, expected in [('epsindiab', b'Sanghi et al.'),
                             ('vhs1256b', b'AB barycenter'),
                             ('hd130948bc', b'BC barycenter'),
                             ('hip64892b', b'HGCA'),
                             ('betapicd', b'Local single-companion fit')]:
        result = client.post('/', data={'planetname': target, 'time': '2025-01-01'})
        assert result.status_code == 200
        assert b'Separation =' in result.data
        assert expected in result.data
    for target, date, error in [('vhs1256b', 'bad-date', b'Invalid Date'),
                                ('unknown-target', '2025-01-01', b'Invalid Planet')]:
        result = client.post('/', data={'planetname': target, 'time': date})
        assert result.status_code == 200
        assert error in result.data
