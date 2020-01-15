# whereistheplanet?
Prediciting the position of exoplanets. Web version is available at https://www.whereistheplanet.com/. Credit: Jason Wang, Matas Kulikauskas, and Sarah Blunt. 

## Install
Requires `orbitize!` (https://github.com/sblunt/orbitize/) and `git-lfs` to pull the posteriors. After you clone the repositroy and use `git lfs pull` to pull the posteriors, install using 
```
python setup.py develop
``` 
This creates a script `whereistheplanet` that you can call from anywhere in the terminal. 

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

## Coming Soon
 * More planets
 * Web app