# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2024-07-10

### Changed

- Group dependabot updates into one PR ([#206](https://github.com/nasa/stitchee/issues/206))([**@danielfromearth**](https://github.com/danielfromearth))
- Increase continuous integration/unit test coverage ([#208](https://github.com/nasa/stitchee/issues/208))([**@danielfromearth**](https://github.com/danielfromearth))
- Use time variable instead of concat dim for ordering datasets ([#198](https://github.com/nasa/stitchee/issues/198))([**@danielfromearth**](https://github.com/danielfromearth), [**@ank1m**](https://github.com/ank1m))

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

- Update UMM-S record ID ([#183](https://github.com/nasa/stitchee/issues/183))

## [1.2.0]

### Changed

- Propagate first empty granule if all input files are empty ([#153](https://github.com/nasa/stitchee/issues/153))
- Remove compression for string array of small size ([#168](https://github.com/nasa/stitchee/issues/168))

### Added

- Add PyPI badges to readme ([#170](https://github.com/nasa/stitchee/issues/170))

### Fixed

- Resolve linting error ([#177](https://github.com/nasa/stitchee/pull/177))

## [1.1.0]

### Added

- Add code coverage to CI pipeline ([#164](https://github.com/nasa/stitchee/pull/164))

## [1.0.0]

### Changed

- Change name to "stitchee" ([#12](https://github.com/danielfromearth/stitchee/pull/12))
- Use ruff+black chain for pre-commit lint & format ([#15](https://github.com/danielfromearth/stitchee/pull/15))
- Rename CLI argument to clarify temporary copying behavior ([#45](https://github.com/danielfromearth/stitchee/issues/45))
- Concatenation dimension CLI argument is required but isn't listed as such in the help message ([#44](https://github.com/danielfromearth/stitchee/issues/44))
- Remove `nco` related code ([#81](https://github.com/danielfromearth/stitchee/issues/81))
- Sort according to extend dimension ([#129](https://github.com/danielfromearth/stitchee/pull/129))
- Consider empty a netCDF with only singleton null-values ([#152](https://github.com/danielfromearth/stitchee/pull/152))
- Update CI pipeline ([#157](https://github.com/danielfromearth/stitchee/pull/157))
- Add pypi publishing steps to CI pipeline ([#158](https://github.com/danielfromearth/stitchee/pull/158))

### Added

- An initial GitHub Actions workflow ([#1](https://github.com/danielfromearth/stitchee/pull/1))
- Create working Docker image ([#8](https://github.com/danielfromearth/stitchee/issues/8))
- Add code necessary to communicate with Harmony ([#10](https://github.com/danielfromearth/stitchee/issues/10))
- More CLI arguments for finer control of concatenation method ([#49](https://github.com/danielfromearth/stitchee/issues/49))
- Add Docker build steps to GitHub Actions workflow ([#99](https://github.com/danielfromearth/stitchee/pull/99))
- Add history attributes ([#113](https://github.com/danielfromearth/stitchee/pull/113))
- Add readme badges ([#115](https://github.com/danielfromearth/stitchee/pull/115))
- Add tutorial Jupyter notebook ([#116](https://github.com/danielfromearth/stitchee/pull/116))
- Create toy netCDFs in testing suite ([#128](https://github.com/danielfromearth/stitchee/pull/116))

### Fixed

- Error with TEMPO ozone profile data because of duplicated dimension names ([#4](https://github.com/danielfromearth/stitchee/pull/4))
- Fix conflicting dimensions on record dimension sorting ([#133](https://github.com/danielfromearth/stitchee/pull/133))
