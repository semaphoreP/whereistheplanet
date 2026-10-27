# Changelog

## 1.1.0 — 2026-10-27

- Expand the public catalog from 71 to 99 targets, with 70 updated posterior
  files serving 75 updated or new entries. Selected posteriors contain 1000
  exact samples with matching likelihoods where supplied. PDS 70 is unchanged.
- Add the accepted local single-companion beta Pic d fit and the HIP 64892 B
  fit with HGCA. Include the published epsilon Indi Ab observable-prior
  posterior and the wide VHS 1256 b orbit relative to the AB barycenter.
- Correct orvara/Octofitter element conversions, HR 8799 planet and mass
  ordering, and HD 284149's outer-companion selection. Preserve source row
  mappings and distinguish log posterior scores from true likelihoods.
- Centralize public files, references, aliases, component layouts and web
  choices. Load saved samples without rebuilding an HGCA fitting system.
- Correct enclosed masses and stellar reflex motion for joint fits, using
  each posterior draw's orbital ordering. Handle PA intervals crossing north.
- Include all public posterior files in the installable package. Validate
  independent propagation, source pairing, literature/input astrometry,
  command-line predictions, and the web form.

The beta Pic d orbit uses a single-companion Keplerian approximation.
Position-prediction uncertainties reflect the supplied fits and their
measurement models; they do not establish convergence or dynamical stability.
