"""Orbit context must use the same physical samples as the dated prediction."""
import configparser
from html import unescape
from html.parser import HTMLParser
import importlib
import json
from pathlib import Path
from urllib.parse import urlsplit

import numpy as np
import pytest
from astropy import constants, units
from astropy.time import Time

import whereistheplanet.whereistheplanet as witp


def period_days(sma, mass):
    """Independent two-body period, using physical rather than rounded units."""
    return (2*np.pi*np.sqrt((np.asarray(sma)*units.au)**3 /
            (constants.G*np.asarray(mass)*units.Msun))).to_value(units.day)


def circular_position(epochs, sma, plx, mass, reference, tau=0):
    phase = 2*np.pi*((np.asarray(epochs)-reference)/period_days(sma, mass)-tau)
    return sma*plx*np.sin(phase), sma*plx*np.cos(phase)


def install_chain(monkeypatch, post, name='_plot_test', reference=58849.):
    monkeypatch.setattr(witp, 'get_chains', lambda target: (post.copy(), reference))
    return name, reference


def assert_summary_matches_draws(answer):
    ra, dec = answer['ra'], answer['dec']
    sep = np.hypot(ra, dec)
    expected = [(np.median(x), np.std(x)) for x in (ra, dec, sep)]
    np.testing.assert_allclose(answer['prediction'][:3], expected, rtol=0, atol=1e-10)
    # Test PA as a circular quantity across north as well as elsewhere.
    pas = np.degrees(np.arctan2(ra, dec)) % 360
    pa_center = answer['prediction'][3][0]
    offsets = (pas-pa_center+180) % 360-180
    assert np.median(offsets) == pytest.approx(0, abs=1e-10)
    assert answer['prediction'][3][1] == pytest.approx(np.std(offsets), abs=1e-10)


def test_full_circular_orbits_and_markers_use_each_draws_period(monkeypatch):
    post = np.zeros((3, 8))
    post[:, 0], post[:, 6], post[:, 7] = [1., 3., 7.], [10., 20., 30.], [.5, 1., 2.]
    post[:, 5] = [.2, .7, .99]
    name, reference = install_chain(monkeypatch, post)
    requested = reference+123.
    answer = witp.predict_orbit(name, requested, num_samples=None, num_points=257)

    assert answer['ra_tracks'].shape == answer['dec_tracks'].shape == (257, 3)
    assert answer['epochs'].shape == (257, 3)
    assert answer['time_mjd'] == requested
    periods = period_days(post[:, 0], post[:, 7])
    np.testing.assert_allclose(answer['period_days'], periods, rtol=1e-12)
    np.testing.assert_allclose(answer['epochs'][-1]-answer['epochs'][0], periods,
                               rtol=1e-12, atol=1e-8)
    assert np.all(answer['epochs'][0] <= requested)
    assert np.all(answer['epochs'][-1] >= requested)
    for index, row in enumerate(post):
        expected_tracks = circular_position(answer['epochs'][:, index], row[0], row[6],
                                            row[7], reference, row[5])
        np.testing.assert_allclose([answer['ra_tracks'][:, index],
                                    answer['dec_tracks'][:, index]],
                                   expected_tracks, rtol=0, atol=1e-6)
        expected_marker = circular_position(requested, row[0], row[6], row[7],
                                            reference, row[5])
        np.testing.assert_allclose([answer['ra'][index], answer['dec'][index]],
                                   expected_marker, rtol=0, atol=1e-6)
    np.testing.assert_allclose(answer['ra_tracks'][0], answer['ra_tracks'][-1], atol=1e-6)
    np.testing.assert_allclose(answer['dec_tracks'][0], answer['dec_tracks'][-1], atol=1e-6)
    assert_summary_matches_draws(answer)


def test_sampled_paths_markers_and_summary_keep_the_same_posterior_draws(monkeypatch):
    post = np.zeros((3, 8))
    post[:, 0], post[:, 6], post[:, 7] = [1., 3., 7.], [10., 20., 30.], [.5, 1., 2.]
    name, reference = install_chain(monkeypatch, post)
    # More draws than rows exercises replacement without depending on a
    # particular random-number generator or a particular sequence of indices.
    answer = witp.predict_orbit(name, reference+123., num_samples=7, num_points=33)
    assert answer['ra_tracks'].shape == (33, 7)
    assert answer['ra'].shape == answer['dec'].shape == (7,)
    for index in range(7):
        radius = np.hypot(answer['ra_tracks'][0, index], answer['dec_tracks'][0, index])
        row_index = np.argmin(abs(post[:, 0]*post[:, 6]-radius))
        sma, plx, mass = post[row_index, [0, 6, 7]]
        assert radius == pytest.approx(sma*plx, abs=1e-6)
        np.testing.assert_allclose([answer['ra'][index], answer['dec'][index]],
                                   circular_position(reference+123., sma, plx, mass, reference),
                                   rtol=0, atol=1e-6)
        np.testing.assert_allclose([answer['ra_tracks'][:, index],
                                    answer['dec_tracks'][:, index]],
                                   circular_position(answer['epochs'][:, index], sma, plx,
                                                     mass, reference), rtol=0, atol=1e-6)
    assert_summary_matches_draws(answer)


def test_eccentric_track_traces_complete_projected_ellipse(monkeypatch):
    post = np.array([[4., .95, 0., 0., 0., .23, 25., 1.]])
    name, reference = install_chain(monkeypatch, post)
    answer = witp.predict_orbit(name, reference+500, num_samples=None, num_points=257)
    ra, dec = answer['ra_tracks'][:, 0], answer['dec_tracks'][:, 0]
    scale, eccentricity = 100., .95
    ellipse = (ra/(scale*np.sqrt(1-eccentricity**2)))**2+(dec/scale+eccentricity)**2
    np.testing.assert_allclose(ellipse, 1., rtol=0, atol=1e-7)
    assert np.max(dec) == pytest.approx(scale*(1-eccentricity), abs=1e-6)
    assert np.min(dec) == pytest.approx(-scale*(1+eccentricity), abs=1e-6)
    assert np.max(ra) == pytest.approx(scale*np.sqrt(1-eccentricity**2), abs=1e-6)
    assert np.min(ra) == pytest.approx(-scale*np.sqrt(1-eccentricity**2), abs=1e-6)


def test_orbit_dynamic_single_uses_trailing_component_masses(monkeypatch):
    post = np.zeros((2, 15))
    post[:, 0], post[:, 6], post[:, 7] = 3., 40., 100.
    post[:, -2], post[:, -1] = [.1, .4], [1., 1.2]
    name, reference = install_chain(monkeypatch, post)
    monkeypatch.setattr(witp, 'dyn_mass_single_comp', witp.dyn_mass_single_comp+[name])
    answer = witp.predict_orbit(name, reference+100, num_samples=None, num_points=33)
    masses = np.sum(post[:, -2:], axis=1)
    np.testing.assert_allclose(answer['period_days'], period_days(3., masses), rtol=1e-12)
    ra, dec = circular_position(reference+100, 3., 40., masses, reference)
    np.testing.assert_allclose([answer['ra'], answer['dec']], [ra, dec], atol=1e-6, rtol=0)
    for index, mass in enumerate(masses):
        ra, dec = circular_position(answer['epochs'][:, index], 3., 40., mass, reference)
        np.testing.assert_allclose([answer['ra_tracks'][:, index],
                                    answer['dec_tracks'][:, index]],
                                   [ra, dec], atol=1e-6, rtol=0)


def test_orbit_tracks_and_markers_include_per_draw_inner_reflex(monkeypatch):
    # The requested companion is outer in draw 0, inner in draw 1. Its
    # stellar-relative motion must retain the draw-specific mass ordering.
    post = np.zeros((2, 16))
    post[:, 0], post[:, 6], post[:, 12] = [1., 12.], [12., 1.], 50.
    post[:, 13], post[:, 14], post[:, 15] = .5, .05, 1.
    name, reference = install_chain(monkeypatch, post)
    monkeypatch.setitem(witp.multi_dict, name, (1, 2))
    requested = reference+100
    answer = witp.predict_orbit(name, requested, num_samples=None, num_points=65)
    np.testing.assert_allclose(answer['period_days'],
                               period_days([12., 1.], [1.55, 1.05]), rtol=1e-12)
    for index, (sma, mass) in enumerate([(12., 1.55), (1., 1.05)]):
        def expected_position(epochs):
            ra, dec = circular_position(epochs, sma, 50., mass, reference)
            if index == 0:
                inner_ra, inner_dec = circular_position(epochs, 1., 50., 1.5, reference)
                ra, dec = ra+inner_ra/3, dec+inner_dec/3
            return ra, dec
        np.testing.assert_allclose([answer['ra'][index], answer['dec'][index]],
                                   expected_position(requested), rtol=0, atol=1e-6)
        np.testing.assert_allclose([answer['ra_tracks'][:, index],
                                    answer['dec_tracks'][:, index]],
                                   expected_position(answer['epochs'][:, index]),
                                   rtol=0, atol=1e-6)
    assert_summary_matches_draws(answer)


def test_orbit_resolves_alias_and_iso_date(monkeypatch):
    post = np.zeros((1, 16))
    post[:, 0], post[:, 6], post[:, 12] = 1., .1, 10.
    post[:, -3:] = [.001, .0001, 1.]
    calls = []
    def get_chains(name):
        calls.append(name)
        return post.copy(), 58849.
    monkeypatch.setattr(witp, 'get_chains', get_chains)
    answer = witp.predict_orbit(' BETPICB ', '2025-01-01', num_samples=None, num_points=33)
    assert calls == ['betapicb']
    assert answer['time_mjd'] == Time('2025-01-01').mjd


def test_invalid_inner_companion_cannot_return_nonfinite_plot_positions(monkeypatch):
    post = np.zeros((1, 16))
    post[:, 0], post[:, 6], post[:, 12] = 1., 12., 50.
    post[:, 13:] = [.5, .05, 1.]
    post[:, 2] = np.nan
    name, reference = install_chain(monkeypatch, post)
    monkeypatch.setitem(witp.multi_dict, name, (1, 2))
    with pytest.raises(ValueError, match='nonfinite sky positions'):
        witp.predict_orbit(name, reference+100, num_samples=None, num_points=33)


@pytest.mark.parametrize('options', [{'time_mjd': 'bad-date'}, {'time_mjd': np.nan},
                                    {'time_mjd': np.inf}, {'num_samples': 0},
                                    {'num_samples': -1}, {'num_samples': 1.5},
                                    {'num_points': 3}, {'num_points': 4.5}])
def test_orbit_rejects_invalid_dates_and_sampling(monkeypatch, options):
    post = np.array([[1., 0., 0., 0., 0., 0., 10., 1.]])
    name, reference = install_chain(monkeypatch, post)
    arguments = {'time_mjd': reference, 'num_samples': None, 'num_points': 33}
    arguments.update(options)
    with pytest.raises((ValueError, TypeError)):
        witp.predict_orbit(name, **arguments)


@pytest.mark.parametrize('elements,reference', [({2: np.nan}, 58849.),
                                               ({5: np.inf}, 58849.),
                                               ({6: np.nan}, 58849.),
                                               ({0: -1., 7: -1.}, 58849.),
                                               ({1: 1.}, 58849.),
                                               ({}, np.nan)])
def test_orbit_rejects_invalid_elements_before_propagation(monkeypatch, elements, reference):
    post = np.array([[1., 0., 0., 0., 0., 0., 10., 1.]])
    for column, value in elements.items():
        post[0, column] = value
    name, _ = install_chain(monkeypatch, post, reference=reference)
    def unexpected_propagation(*args, **kwargs):
        pytest.fail('Invalid orbital elements must be rejected before propagation')
    monkeypatch.setattr(witp.kepler, 'calc_orbit', unexpected_propagation)
    with pytest.raises(ValueError, match='finite, bound orbital elements'):
        witp.predict_orbit(name, 58849., num_samples=None, num_points=33)


@pytest.mark.parametrize('num_samples', [None, 1])
def test_orbit_rejects_empty_posterior(monkeypatch, num_samples):
    name, reference = install_chain(monkeypatch, np.empty((0, 8)))
    with pytest.raises(ValueError, match='no orbit samples'):
        witp.predict_orbit(name, reference, num_samples=num_samples, num_points=33)


class FormElements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.scripts = []
        self.current_script = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in ('input', 'option'):
            self.elements.append((tag, dict(attrs)))
        if tag == 'script':
            self.current_script = {'attrs': dict(attrs), 'text': ''}
            self.scripts.append(self.current_script)

    def handle_data(self, text):
        if self.current_script is not None:
            self.current_script['text'] += text

    def handle_endtag(self, tag):
        if tag == 'script':
            self.current_script = None


def plot_spec_from_html(html):
    scripts = FormElements(html).scripts
    payloads = [script for script in scripts
                if script['attrs'].get('id') == 'orbit-plot-data']
    assert len(payloads) == 1
    assert payloads[0]['attrs'].get('type') == 'application/json'
    return json.loads(payloads[0]['text'])


def small_plot_data():
    return {'ra_tracks': np.array([[1., 2.], [3., 4.], [1., 2.]]),
            'dec_tracks': np.array([[-1., -2.], [-3., -4.], [-1., -2.]]),
            'epochs': np.array([[58849., 58850.], [58859., 58870.], [58869., 58890.]]),
            'ra': np.array([1.5, 2.5]), 'dec': np.array([-2.5, -3.5]),
            'prediction': ((2., .5), (-3., .5), (4., .5), (90., .5)),
            'time_mjd': 58860.}


def assert_sky_axes(spec):
    assert spec['layout']['xaxis']['autorange'] == 'reversed'
    assert spec['layout']['yaxis']['scaleanchor'] == 'x'
    assert spec['layout']['yaxis']['scaleratio'] == 1


def test_interactive_spec_preserves_orbits_and_requested_date_samples():
    orbit_plot = importlib.import_module('whereistheplanet.orbit_plot')
    data = small_plot_data()
    spec = orbit_plot.build_orbit_plot(data, 'Example planet', '2020-01-12')
    # It must be portable JSON, with actual numeric values available to hover.
    spec = json.loads(json.dumps(spec, allow_nan=False))
    path = next(trace for trace in spec['data'] if trace.get('mode') == 'lines')
    assert path['connectgaps'] is False
    samples = []
    current = []
    for ra, dec in zip(path['x'], path['y']):
        if ra is None:
            if current:
                samples.append(current)
                current = []
        else:
            current.append((ra, dec))
    if current:
        samples.append(current)
    np.testing.assert_allclose(samples,
                               np.stack((data['ra_tracks'].T, data['dec_tracks'].T), axis=-1))
    metadata = np.asarray([value for value in path['customdata'] if value is not None])
    np.testing.assert_allclose(metadata[:, 0], data['epochs'].T.reshape(-1))
    np.testing.assert_array_equal(metadata[:, 1], [1, 1, 1, 2, 2, 2])
    dated = next(trace for trace in spec['data'] if '2020-01-12' in trace.get('name', ''))
    np.testing.assert_allclose(dated['x'], data['ra'])
    np.testing.assert_allclose(dated['y'], data['dec'])
    median = next(trace for trace in spec['data'] if 'median' in trace.get('name', '').lower())
    assert median['x'] == [data['prediction'][0][0]]
    assert median['y'] == [data['prediction'][1][0]]
    assert_sky_axes(spec)


@pytest.mark.parametrize('field,values', [
    ('ra_tracks', np.ones((3, 1))),
    ('ra_tracks', np.ones(3)),
    ('ra', np.ones(1)),
    ('dec', np.ones(1)),
    ('epochs', np.ones((3, 1))),
    ('epochs', np.array([[58849., 58850.], [np.nan, 58870.], [58869., 58890.]])),
    ('ra_tracks', np.array([[1., 2.], [np.nan, 4.], [1., 2.]])),
    ('dec_tracks', np.array([[-1., -2.], [-3., np.inf], [-1., -2.]])),
    ('ra', np.array([np.nan, 2.5])),
    ('dec', np.array([-2.5, np.inf])),
    ('prediction', ((np.nan, .5), (-3., .5), (4., .5), (90., .5))),
    ('prediction', ((2., .5), (np.inf, .5), (4., .5), (90., .5))),
])
def test_interactive_spec_rejects_mismatched_or_nonfinite_positions(field, values):
    orbit_plot = importlib.import_module('whereistheplanet.orbit_plot')
    data = small_plot_data()
    data[field] = values
    with pytest.raises(ValueError):
        orbit_plot.build_orbit_plot(data, 'Example planet', '2020-01-12')


@pytest.fixture
def orbit_webapp(monkeypatch):
    # Import with an ephemeral secret without accessing a real flask.ini.
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


def test_web_orbit_is_optional_and_off_by_default(orbit_webapp, monkeypatch):
    def unexpected_plot(*args, **kwargs):
        pytest.fail('An unchecked request must not generate an orbit plot')
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_orbit', unexpected_plot)
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_planet',
                        lambda *args, **kwargs: ((1., .1), (2., .2), (3., .3), (4., .4)))
    client = orbit_webapp.app.test_client()
    for response in [client.get('/'), client.post('/', data={'planetname': 'betapicb',
                                                            'time': '2025-01-01'})]:
        assert response.status_code == 200
        assert b'data:image/png;base64,' not in response.data
        assert b'id="orbit-plot-data"' not in response.data
        assert b'/orbit-plot.js' not in response.data
        assert b'/static/orbit-plot.js' not in response.data
        elements = FormElements(response.get_data(as_text=True)).elements
        checkbox = next(attrs for tag, attrs in elements if attrs.get('name') == 'show_orbit')
        assert 'checked' not in checkbox


def test_web_requested_orbit_uses_same_prediction_and_preserves_form(orbit_webapp, monkeypatch):
    post = np.zeros((1, 16))
    post[:, 0], post[:, 1], post[:, 6], post[:, 12] = 1., .3, .1, 10.
    post[:, -3:] = [.001, .0001, 1.]
    monkeypatch.setattr(witp, 'get_chains', lambda name: (post.copy(), 58849.))
    calls = []
    def predict_orbit(name, date, **kwargs):
        calls.append((name, date))
        return witp.predict_orbit(name, date, num_samples=None, num_points=33)
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_orbit', predict_orbit)
    def unexpected_prediction(*args, **kwargs):
        pytest.fail('Orbit and coordinate output must use the same posterior draws')
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_planet', unexpected_prediction)
    response = orbit_webapp.app.test_client().post('/', data={'planetname': 'betapicb',
                                                             'time': '2025-01-01',
                                                             'show_orbit': 'y'})
    assert response.status_code == 200
    assert calls == [('betapicb', '2025-01-01')]
    html = response.get_data(as_text=True)
    spec = plot_spec_from_html(html)
    assert 'id="orbit-plot"' in html
    sources = [script['attrs'].get('src') for script in FormElements(html).scripts]
    assert any(source and urlsplit(source).path == '/orbit-plot.js' for source in sources)
    assert '/static/orbit-plot.js' in sources
    assert 'data:image/png;base64,' not in html
    requested = witp.predict_orbit('betapicb', '2025-01-01', num_samples=None, num_points=33)
    median = next(trace for trace in spec['data'] if 'median' in trace.get('name', '').lower())
    assert median['x'] == [requested['prediction'][0][0]]
    assert median['y'] == [requested['prediction'][1][0]]
    dated = next(trace for trace in spec['data'] if '2025-01-01' in trace.get('name', ''))
    np.testing.assert_allclose(dated['x'], requested['ra'])
    np.testing.assert_allclose(dated['y'], requested['dec'])
    assert_sky_axes(spec)
    assert 'Separation =' in html
    elements = FormElements(html).elements
    assert any(attrs.get('name') == 'show_orbit' and 'checked' in attrs
               for tag, attrs in elements)
    assert any(attrs.get('name') == 'time' and attrs.get('value') == '2025-01-01'
               for tag, attrs in elements)
    assert any(tag == 'option' and attrs.get('value') == 'betapicb' and 'selected' in attrs
               for tag, attrs in elements)


@pytest.mark.parametrize('failure_stage', ['calculation', 'rendering'])
def test_web_plot_failure_keeps_numerical_prediction(orbit_webapp, monkeypatch, failure_stage):
    prediction = ((1.25, .1), (2., .2), (3., .3), (4., .4))
    numerical_calls, renderer_calls = [], []
    def predict_orbit(*args, **kwargs):
        if failure_stage == 'calculation':
            raise RuntimeError('private calculation diagnostic')
        return {'prediction': prediction}
    def predict_planet(*args, **kwargs):
        numerical_calls.append(True)
        return prediction
    def render_orbit(*args, **kwargs):
        renderer_calls.append(True)
        raise RuntimeError('private rendering diagnostic')
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_orbit', predict_orbit)
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_planet', predict_planet)
    orbit_plot = importlib.import_module('whereistheplanet.orbit_plot')
    monkeypatch.setattr(orbit_plot, 'build_orbit_plot', render_orbit)
    response = orbit_webapp.app.test_client().post('/', data={'planetname': 'betapicb',
                                                             'time': '2025-01-01',
                                                             'show_orbit': 'y'})
    assert response.status_code == 200
    assert b'RA Offset = 1.250 +/- 0.100 mas' in response.data
    assert b'The orbit plot could not be generated.' in response.data
    assert b'The numerical prediction is still available.' in response.data
    assert b'data:image/png;base64,' not in response.data
    assert b'id="orbit-plot-data"' not in response.data
    assert b'/orbit-plot.js' not in response.data
    assert b'/static/orbit-plot.js' not in response.data
    assert b'private calculation diagnostic' not in response.data
    assert b'private rendering diagnostic' not in response.data
    assert len(numerical_calls) == (failure_stage == 'calculation')
    assert len(renderer_calls) == (failure_stage == 'rendering')


@pytest.mark.parametrize('target,date,error', [('betapicb', 'bad-date', b'Invalid Date'),
                                              ('unknown-target', '2025-01-01', b'Invalid Planet')])
def test_web_invalid_request_does_not_plot(orbit_webapp, monkeypatch, target, date, error):
    def unexpected_plot(*args, **kwargs):
        pytest.fail('An invalid request must not generate an orbit plot')
    orbit_plot = importlib.import_module('whereistheplanet.orbit_plot')
    monkeypatch.setattr(orbit_plot, 'build_orbit_plot', unexpected_plot)
    response = orbit_webapp.app.test_client().post('/', data={'planetname': target, 'time': date,
                                                             'show_orbit': 'y'})
    assert response.status_code == 200
    assert error in response.data
    assert b'data:image/png;base64,' not in response.data
    assert b'id="orbit-plot-data"' not in response.data
    assert b'/orbit-plot.js' not in response.data
    assert b'/static/orbit-plot.js' not in response.data


def test_interactive_json_safely_contains_hostile_label(orbit_webapp, monkeypatch):
    label = '</script><script>window.unwantedScript = true;</script>'
    monkeypatch.setitem(orbit_webapp.whereistheplanet.display_names, 'betapicb', label)
    monkeypatch.setattr(orbit_webapp.whereistheplanet, 'predict_orbit',
                        lambda *args, **kwargs: small_plot_data())
    response = orbit_webapp.app.test_client().post('/', data={'planetname': 'betapicb',
                                                             'time': '2025-01-01',
                                                             'show_orbit': 'y'})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    spec = plot_spec_from_html(html)
    title = spec['layout']['title']
    title = title.get('text', '') if isinstance(title, dict) else title
    assert label in unescape(title).replace('<br>', ' ')
    assert label not in html
    assert '<script>window.unwantedScript' not in html


def test_local_plotly_bundle_is_javascript_and_cacheable(orbit_webapp, monkeypatch):
    javascript = 'window.Plotly = {newPlot: function () {}};'
    monkeypatch.setattr(orbit_webapp, '_get_plotly_javascript', lambda: javascript)
    client = orbit_webapp.app.test_client()
    response = client.get('/orbit-plot.js')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == javascript
    assert response.mimetype in ('text/javascript', 'application/javascript')
    assert response.cache_control.max_age >= 86400
    assert response.cache_control.public
    assert response.headers.get('ETag')
    cached = client.get('/orbit-plot.js', headers={'If-None-Match': response.headers['ETag']})
    assert cached.status_code == 304
