# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
### Deprecated
### Removed
### Fixed
- [PR #4](https://github.com/danielfromearth/stitchee/pull/4): Error with TEMPO ozone profile data because of duplicated dimension names
