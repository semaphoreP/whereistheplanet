"""JSON figure specifications for the optional interactive web orbit plot."""

from html import escape
from textwrap import wrap

import numpy as np


def build_orbit_plot(data, planet_label, date_label):
    """Return a Plotly figure specification of sampled sky orbits.

    Coordinates and the median marker come from the same posterior draws as
    the numerical prediction. Ordinary Python lists keep the result directly
    JSON serializable without Plotly's encoded array representation. Orbit
    epochs remain MJD because some posterior periods exceed calendar ranges.
    """
    ra_tracks = np.asarray(data['ra_tracks'], dtype=float)
    dec_tracks = np.asarray(data['dec_tracks'], dtype=float)
    ra = np.asarray(data['ra'], dtype=float).reshape(-1)
    dec = np.asarray(data['dec'], dtype=float).reshape(-1)
    epochs = np.asarray(data['epochs'], dtype=float)
    if (ra_tracks.ndim != 2 or ra_tracks.shape != dec_tracks.shape
            or ra_tracks.shape[0] == 0 or ra_tracks.shape[1] != ra.size
            or ra.size != dec.size or ra.size == 0):
        raise ValueError("Orbit tracks and date positions must contain matching samples")
    if epochs.shape != ra_tracks.shape:
        raise ValueError("Orbit epochs must match the orbit tracks")
    if not all(np.all(np.isfinite(values))
               for values in (ra_tracks, dec_tracks, ra, dec, epochs)):
        raise ValueError("Orbit plot coordinates and epochs must be finite")

    median_ra = float(data['prediction'][0][0])
    median_dec = float(data['prediction'][1][0])
    if not np.all(np.isfinite([median_ra, median_dec])):
        raise ValueError("Orbit plot median must be finite")

    # None separates independent posterior paths in one trace, keeping browser
    # rendering and legend toggling inexpensive even with a hundred draws.
    track_ra, track_dec, track_metadata = [], [], []
    for index in range(ra.size):
        track_ra.extend(ra_tracks[:, index].tolist() + [None])
        track_dec.extend(dec_tracks[:, index].tolist() + [None])
        track_metadata.extend([[epoch, index + 1]
                               for epoch in epochs[:, index].tolist()] + [None])

    safe_date = escape(str(date_label))
    coordinates = 'RA: %{x:.3f} mas<br>Dec: %{y:.3f} mas'
    traces = [
        {
            'type': 'scatter',
            'mode': 'lines',
            'x': track_ra,
            'y': track_dec,
            'customdata': track_metadata,
            'connectgaps': False,
            'line': {'color': 'rgba(40,120,181,0.23)', 'width': 1},
            'name': '{} sampled orbits'.format(ra.size),
            'legendgroup': 'orbits',
            'hovertemplate': ('Sample %{customdata[1]}<br>' + coordinates
                              + '<br>MJD: %{customdata[0]:.3f}<extra></extra>'),
        },
        {
            'type': 'scatter',
            'mode': 'markers',
            'x': ra.tolist(),
            'y': dec.tolist(),
            'customdata': list(range(1, ra.size + 1)),
            'marker': {'color': '#d97800', 'size': 6, 'opacity': 0.65},
            'name': 'Positions on {}'.format(safe_date),
            'legendgroup': 'date',
            'hovertemplate': (safe_date + '<br>Sample %{customdata}<br>'
                              + coordinates + '<extra></extra>'),
        },
        {
            'type': 'scatter',
            'mode': 'markers',
            'x': [median_ra],
            'y': [median_dec],
            'marker': {'symbol': 'diamond', 'size': 12, 'color': '#ffb347',
                       'line': {'color': '#5e3500', 'width': 1.5}},
            'name': 'Median predicted position',
            'legendgroup': 'median',
            'hovertemplate': ('Median on ' + safe_date + '<br>' + coordinates
                              + '<extra></extra>'),
        },
        {
            'type': 'scatter',
            'mode': 'markers',
            'x': [0.0],
            'y': [0.0],
            'marker': {'symbol': 'star', 'size': 16, 'color': '#222222'},
            'name': 'Reference position',
            'legendgroup': 'reference',
            'hovertemplate': 'Reference position<br>' + coordinates + '<extra></extra>',
        },
    ]
    axis_style = {
        'showgrid': True,
        'gridcolor': '#eeeeee',
        'zeroline': True,
        'zerolinecolor': '#cccccc',
        'automargin': True,
        'constrain': 'domain',
    }
    title = '<br>'.join(escape(line) for line in wrap(
        '{}: projected orbit'.format(planet_label), width=32,
        break_long_words=False, break_on_hyphens=False))
    return {
        'data': traces,
        'layout': {
            'title': {'text': title, 'font': {'size': 16},
                      'x': 0, 'xanchor': 'left', 'y': 0.95, 'yanchor': 'top'},
            'autosize': True,
            'margin': {'l': 70, 'r': 25, 't': 95, 'b': 150},
            'paper_bgcolor': '#ffffff',
            'plot_bgcolor': '#ffffff',
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'xaxis': dict(axis_style, title={'text': 'RA offset (mas; east \u2190)'},
                          autorange='reversed', constraintoward='left'),
            'yaxis': dict(axis_style, title={'text': 'Dec offset (mas; north \u2191)'},
                          scaleanchor='x', scaleratio=1),
            'hovermode': 'closest',
            'dragmode': 'zoom',
            'legend': {'orientation': 'h', 'x': 0, 'xanchor': 'left',
                       'y': -0.2, 'yanchor': 'top', 'font': {'size': 11},
                       'groupclick': 'togglegroup'},
        },
        'config': {
            'displaylogo': False,
            'displayModeBar': True,
            'responsive': True,
            'scrollZoom': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'format': 'png',
                                    'filename': 'whereistheplanet-orbit', 'scale': 2},
        },
    }
