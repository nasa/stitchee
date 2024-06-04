# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added
- [Issue #133](https://github.com/nasa/stitchee/issues/133): Add readthedocs documentation build
- [Issue #185](https://github.com/nasa/stitchee/issues/185): Added arguments for temporary file copies and overwriting output file in main stitchee function
- [Issue #181](https://github.com/nasa/stitchee/issues/181): Add a group delimiter argument
- [Issue #134](https://github.com/nasa/stitchee/issues/134): Add an integration test that runs stitchee on files first subsetted by the operational Harmony subsetter
- [Issue #194](https://github.com/nasa/stitchee/issues/194): Add page about the SAMBAH service chain to the Readthedocs documentation
### Changed
### Deprecated
### Removed
### Fixed
- [Issue #204](https://github.com/nasa/stitchee/issues/204): Fix integration test failure

## [1.2.1]

### Added
### Changed
  - [Issue #183](https://github.com/nasa/stitchee/issues/183): Update UMM-S record ID
### Deprecated
### Removed
### Fixed

## [1.2.0]

### Added
  - [Issue #170](https://github.com/nasa/stitchee/issues/170): Add PyPI badges to readme
### Changed
  - [Issue #153](https://github.com/nasa/stitchee/issues/153): propagate first empty granule if all input files are empty
  - [Issue #168](https://github.com/nasa/stitchee/issues/168): remove compression for string array of small size
### Deprecated
### Removed
### Fixed
  - [Pull #177](https://github.com/nasa/stitchee/pull/177): Resolve linting error

## [1.1.0]

### Added
  - [Pull #164](https://github.com/nasa/stitchee/pull/164): Add code coverage to CI pipeline
### Changed
### Deprecated
### Removed
### Fixed

## [1.0.0]

### Added
  - [Pull #1](https://github.com/danielfromearth/stitchee/pull/1): An initial GitHub Actions workflow
  - [Issue #8](https://github.com/danielfromearth/stitchee/issues/8): Create working Docker image
  - [Issue #10](https://github.com/danielfromearth/stitchee/issues/10): Add code necessary to communicate with Harmony
  - [Issue #49](https://github.com/danielfromearth/stitchee/issues/49): More CLI arguments for finer control of concatenation method
  - [Pull #99](https://github.com/danielfromearth/stitchee/pull/99): Add Docker build steps to GitHub Actions workflow
  - [Pull #113](https://github.com/danielfromearth/stitchee/pull/113): Add history attributes
  - [Pull #115](https://github.com/danielfromearth/stitchee/pull/115): Add readme badges
  - [Pull #116](https://github.com/danielfromearth/stitchee/pull/116): Add tutorial Jupyter notebook
  - [Pull #128](https://github.com/danielfromearth/stitchee/pull/116): Create toy netCDFs in testing suite
### Changed
  - [Pull #12](https://github.com/danielfromearth/stitchee/pull/12): Changed name to "stitchee"
  - [Pull #15](https://github.com/danielfromearth/stitchee/pull/15): Use ruff+black chain for pre-commit lint & format
  - [Issue #45](https://github.com/danielfromearth/stitchee/issues/45): Rename CLI argument to clarify temporary copying behavior
  - [Issue #44](https://github.com/danielfromearth/stitchee/issues/44): Concatenation dimension CLI argument is required but isn't listed as such in the help message
  - [Issue #81](https://github.com/danielfromearth/stitchee/issues/81): Remove `nco` related code
  - [Pull #129](https://github.com/danielfromearth/stitchee/pull/129): Sort according to extend dimension
  - [Pull #152](https://github.com/danielfromearth/stitchee/pull/152): Consider empty a netCDF with only singleton null-values
  - [Pull #157](https://github.com/danielfromearth/stitchee/pull/157): Update CI pipeline
  - [Pull #158](https://github.com/danielfromearth/stitchee/pull/158): Add pypi publishing steps to CI pipeline
### Deprecated
### Removed
### Fixed
- [Pull #4](https://github.com/danielfromearth/stitchee/pull/4): Error with TEMPO ozone profile data because of duplicated dimension names
- [Pull #133](https://github.com/danielfromearth/stitchee/pull/133): Fix conflicting dimensions on record dimension sorting
