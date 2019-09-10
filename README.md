# whereistheplanet?
Prediciting the position of exoplanets. Requires `orbitize!` (https://github.com/sblunt/orbitize/) and `git lfs` to pull the posteriors. 

## Tutorial
Open a terminal window and go to the base directory of the code
```
python whereistheplanet.py hr8799b
```

If you want the planet location at a particular date.
```
python whereistheplanet.py hr8799b --time 2019-01-01
```

To see all of the planets currently supported:
```
python whereistheplanet.py --list
```

## Coming Soon
 * More planets
 * Web app