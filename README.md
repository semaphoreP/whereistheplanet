# whereistheplanet?
Prediciting the position of exoplanets. Web version is available at https://www.whereistheplanet.com/.
 
![Teseting Badge](https://github.com/semaphoreP/whereistheplanet/actions/workflows/ci-tests.yml/badge.svg) [![ASCL Reference](https://img.shields.io/badge/ascl-2101.003-blue.svg?colorB=262255)](https://ascl.net/2101.003)

## Install

`whereistheplanet` is easily installed through PyPI:

```
pip install whereistheplanet
```

### Developer Install

Requires `orbitize!` (https://github.com/sblunt/orbitize/) and `git-lfs` to pull the posteriors. After you clone the repositroy and use `git lfs pull` to pull the posteriors, install using 
```
pip install -e .
``` 
This creates a script `whereistheplanet` that you can call from anywhere in the terminal. 

If you have issues running whereistheplanet on your machine, you can check out the [querytheplanet](https://github.com/vandalt/querytheplanet) package. Howevert, please do not run large amounts (100+) queries in a short span of time, to avoid overloading the webserver. To avoid large number of queries, you should probably be computing the orbit yourself.

## Tutorial

Open a terminal window and run
```
whereistheplanet hr8799b
```

If you want the planet location at a particular date.
```
whereistheplanet hr8799b --time 2019-01-01
```

To see all of the planets currently supported:
```
whereistheplanet --list
```

On the web app, select **Show full orbit plot** before predicting to include an
interactive plot of sampled orbits and the companion's position at the requested date. Blue curves
show the projected full orbits, orange points show the date positions, and a
diamond marks the same median RA/Dec shown in the numerical prediction. North is
up and east is left; the star at the origin marks the reference position, with
any target-specific reference-frame notes shown with the numerical prediction. Plotting is
optional and off by default. Drag to zoom, use the toolbar to pan or download a
PNG, double-click to reset, hover for coordinates, and click legend entries to
show or hide the orbits and positions. The web app requirements include Plotly;
its JavaScript is served locally by the app, so no external chart service is needed.

## Catalog maintenance

Public target names, references and companion layouts live in
`whereistheplanet/catalog.py`; the web menu uses the same catalog.
The catalog includes 99 targets. See [CHANGELOG.md](CHANGELOG.md) for release changes.

## Attribution

This software was built by Jason Wang, with Matas Kulikauskas helping develop
the web app.

We thank Sarah Blunt, Mirek Brandt, Jonathan Roberts, Will Balmer, and other
members of the community for providing orbit posteriors.

If you used this for your research, please cite the [ASCL entry](https://ascl.net/2101.003) of it:

    Wang, J. J., Kulikauskas, M., Blunt, S. 2021, Astrophysics Source Code Library, ascl:2101.003
