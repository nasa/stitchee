# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Common Changelog](https://common-changelog.org/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

- migrate to xarray.DataTree  ([#281](https://github.com/nasa/stitchee/pull/281))([**@ank1m**](https://github.com/ank1m), [**@danielfromearth**](https://github.com/danielfromearth))
- update the default python version from 3.10 to 3.12 ([#284](https://github.com/nasa/stitchee/pull/284))([**@danielfromearth**](https://github.com/danielfromearth))
- flip package and module names, so package is "stitchee" ([#285](https://github.com/nasa/stitchee/pull/285))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.6.1] - 2024-11-27

### Fixed

- prevent xarray from changing variable types on open_dataset ([#254](https://github.com/nasa/stitchee/pull/254))([**@ank1m**](https://github.com/ank1m))

## [1.6.0] - 2024-11-19

### Changed

- update pre-commit: to autoupdate and with gitleaks ([#247](https://github.com/nasa/stitchee/pull/247))([**@danielfromearth**](https://github.com/danielfromearth))
- improved test coverage ([#248](https://github.com/nasa/stitchee/pull/248))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.5.0] - 2024-11-08

### Changed

- Update tutorial notebook to use PROD instead of UAT and improve readability ([#241](https://github.com/nasa/stitchee/issues/241))([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Expose sorting variable argument in the command line interface ([#233](https://github.com/nasa/stitchee/issues/233))([**@danielfromearth**](https://github.com/danielfromearth))

### Removed

- Remove the dask dependency ([#235](https://github.com/nasa/stitchee/issues/235))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.4.0] - 2024-08-19

### Changed

- Allow single netCDF file input in addition to single text file listings ([#230](https://github.com/nasa/stitchee/issues/230))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.3.0] - 2024-07-11

### Changed

- Group dependabot updates into one PR ([#206](https://github.com/nasa/stitchee/issues/206))([**@danielfromearth**](https://github.com/danielfromearth))
- Increase continuous integration/unit test coverage ([#208](https://github.com/nasa/stitchee/issues/208))([**@danielfromearth**](https://github.com/danielfromearth))
- Use time variable instead of concat dim for ordering datasets ([#198](https://github.com/nasa/stitchee/issues/198))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))
- Update `CHANGELOG.md` to follow Common Changelog conventions ([#226](https://github.com/nsidc/earthaccess/pull/226))([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add readthedocs documentation build ([#133](https://github.com/nasa/stitchee/issues/133))([**@danielfromearth**](https://github.com/danielfromearth))
- Add arguments for temporary file copies and overwriting output file in main stitchee function ([#185](https://github.com/nasa/stitchee/issues/185))([**@danielfromearth**](https://github.com/danielfromearth))
- Add a group delimiter argument ([#181](https://github.com/nasa/stitchee/issues/181))([**@danielfromearth**](https://github.com/danielfromearth))
- Add an integration test that runs stitchee on files first subsetted by the operational Harmony subsetter ([#134](https://github.com/nasa/stitchee/issues/134))([**@danielfromearth**](https://github.com/danielfromearth))
- Add page about the SAMBAH service chain to the Readthedocs documentation ([#194](https://github.com/nasa/stitchee/issues/194))([**@danielfromearth**](https://github.com/danielfromearth))
- Add autoupdate schedule for pre-commit ([#193](https://github.com/nasa/stitchee/issues/193))([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Fix integration test failure ([#204](https://github.com/nasa/stitchee/issues/204))([**@danielfromearth**](https://github.com/danielfromearth))


## [1.2.1]

### Changed

- Update UMM-S record ID ([#183](https://github.com/nasa/stitchee/issues/183))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))

## [1.2.0]

### Changed

- Propagate first empty granule if all input files are empty ([#153](https://github.com/nasa/stitchee/issues/153))([**@ank1m**](https://github.com/ank1m), [**@danielfromearth**](https://github.com/danielfromearth))
- Remove compression for string array of small size ([#168](https://github.com/nasa/stitchee/issues/168))([**@ank1m**](https://github.com/ank1m), [**@danielfromearth**](https://github.com/danielfromearth))

### Added

- Add PyPI badges to readme ([#170](https://github.com/nasa/stitchee/issues/170))([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Resolve linting error ([#177](https://github.com/nasa/stitchee/pull/177))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.1.0]

### Added

- Add code coverage to CI pipeline ([#164](https://github.com/nasa/stitchee/pull/164))([**@danielfromearth**](https://github.com/danielfromearth))

## [1.0.0]

### Changed

- Change name to "stitchee" ([#12](https://github.com/danielfromearth/stitchee/pull/12))([**@danielfromearth**](https://github.com/danielfromearth))
- Use ruff+black chain for pre-commit lint & format ([#15](https://github.com/danielfromearth/stitchee/pull/15))([**@danielfromearth**](https://github.com/danielfromearth))
- Rename CLI argument to clarify temporary copying behavior ([#45](https://github.com/danielfromearth/stitchee/issues/45))([**@danielfromearth**](https://github.com/danielfromearth))
- Remove `nco` related code ([#83](https://github.com/nasa/stitchee/pull/83))([**@danielfromearth**](https://github.com/danielfromearth))
- Sort according to extend dimension ([#129](https://github.com/danielfromearth/stitchee/pull/129))([**@danielfromearth**](https://github.com/danielfromearth))
- Consider empty a netCDF with only singleton null-values ([#152](https://github.com/danielfromearth/stitchee/pull/152))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))
- Update CI pipeline ([#157](https://github.com/danielfromearth/stitchee/pull/157))([**@danielfromearth**](https://github.com/danielfromearth))
- Add pypi publishing steps to CI pipeline ([#158](https://github.com/danielfromearth/stitchee/pull/158))([**@danielfromearth**](https://github.com/danielfromearth))

### Added

- An initial GitHub Actions workflow ([#1](https://github.com/danielfromearth/stitchee/pull/1))([**@danielfromearth**](https://github.com/danielfromearth))
- Create working Docker image ([#40](https://github.com/nasa/stitchee/pull/40))([**@danielfromearth**](https://github.com/danielfromearth))
- Add code necessary to communicate with Harmony ([#40](https://github.com/nasa/stitchee/pull/40))([**@danielfromearth**](https://github.com/danielfromearth))
- More CLI arguments for finer control of concatenation method ([#50](https://github.com/nasa/stitchee/pull/50))([**@danielfromearth**](https://github.com/danielfromearth))
- Add Docker build steps to GitHub Actions workflow ([#99](https://github.com/danielfromearth/stitchee/pull/99), [#108](https://github.com/nasa/stitchee/pull/108))([**@danielfromearth**](https://github.com/danielfromearth))
- Add history attributes ([#113](https://github.com/danielfromearth/stitchee/pull/113))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))
- Add readme badges ([#115](https://github.com/danielfromearth/stitchee/pull/115))([**@danielfromearth**](https://github.com/danielfromearth))
- Add tutorial Jupyter notebook ([#116](https://github.com/danielfromearth/stitchee/pull/116))([**@ank1m**](https://github.com/ank1m), [**@danielfromearth**](https://github.com/danielfromearth))
- Create toy netCDFs in testing suite ([#128](https://github.com/danielfromearth/stitchee/pull/128))([**@danielfromearth**](https://github.com/danielfromearth))

### Fixed

- Error with TEMPO ozone profile data because of duplicated dimension names ([#4](https://github.com/danielfromearth/stitchee/pull/4))([**@danielfromearth**](https://github.com/danielfromearth))
- Fix conflicting dimensions on record dimension sorting ([#136](https://github.com/danielfromearth/stitchee/pull/136))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))
- Concatenation dimension CLI argument is required but isn't listed as such in the help message ([#44](https://github.com/danielfromearth/stitchee/issues/44))([**@danielfromearth**](https://github.com/danielfromearth))
