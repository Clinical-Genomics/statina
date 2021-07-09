# Change Log

This change log will document the notable changes to this project in this file and it is following [Semantic Versioning](https://semver.org/)


## [x.x.x]
### Added
- samples view

## [1.1.0]

### Fixed
- Correcting release documentation
- ziped batch archive download

### Added
- two plots to QC-Data view
- html-report download


## [1.0.2]

### Added
- Changes FF-x tresholds and shows the tresholds in the XY plot
- Change FF-y treshold #81 
- Makes the bath table scrollable with fixed header #83 

### Fixed
- Fixes a bug in the QC-plots - ticktext showing batch ids was based on a soted list of batch_ids, while the box-plots was not sorted acordingly #87
- Fixed a "bug" in the fetal fraction xy plot and z-score plots, where only 'included' samples were shown instead of all samples in the batch.  #79 

## [1.0.0]

### Fixed
- adjust warning thresholds for FF

### Added
- adds automatic sex classification


## [0.2.0]

### Added
- This PR adds a admin user view


## [0.1.0]

### Fixed
- updates the report view with proper data
- replaces ncv with zscore

## [0.0.4]

### Added
- Sample views
- Batch views
- Dockerfile

### Fixed

### Changed
- Changed name of package to statina
