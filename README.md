# Statina  [![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/statina/badge.svg?branch=master)](https://coveralls.io/github/Clinical-Genomics/statina?branch=master) [![Build Status](https://travis-ci.org/Clinical-Genomics/statina.svg?branch=master)](https://travis-ci.org/Clinical-Genomics/statina) ![Latest Release](https://img.shields.io/github/v/release/clinical-genomics/statina)


Statina is a visualisation tool for the data produced by the [Fluffy] pipeline running [WisecondorX] to analyze NIPT.

## Installation

```bash
git clone https://github.com/Clinical-Genomics/statina
cd statina
pip install -r requirements.txt -e .
```

## Usage

### Demo

**The CLI is intended for development/testing purpose only. To run in a production setting please refer to documentation
for suggestions how.**

Once installed, you can set up Statina by running a few commands using the included command line interface. 
Given you have a MongoDB server listening on the default port (27017), this is how you would set up a fully working 
Statina demo:

```bash
statina load batch --result-file statina/tests/fixtures/valid_fluffy.csv
```

Settings can be used by exporting the environment variables: `DB_NAME`, `DB_URI`, `HOST`, `PORT`
This will set up an instance of Statina with a database called `statina-demo`. Now run

```bash
statina serve --reload
```
 and play around with the interface.

### Docker image

Statina can also run as a container. The image is available [on Docker Hub][docker-hub] or can be build using the 
Dockerfile provided in this repository.

To build a new image from the Dockerfile use the commands: `docker build -t statina .`

To run the image use the following command: `docker run --name statina statina statina `

To remove the container, type: `docker rm statina`

## Release model
Statina is using github flow release model as described in our development manual.


### Steps to make a new release:

1) Get you PR approved.
2) Append the version bump to PR title. Eg. __Update README__ becomes __Update Readme (patch)__
3) Select __squash and merge__
4) Write a change log comment.
5) Merge.

	
### Deploying to staging

Opening pull requests in Statina repository will enable a Github Action to build containers and publish to 
[statina-stage dockerhub](https://hub.docker.com/repository/docker/clinicalgenomics/statina-stage) with each commit.

Two tags will be published: one with the name of the branch and another tagged "latest".


Steps to test current branch on staging:

`ssh firstname.lastname@cg-vm1.scilifelab.se`

`sudo -iu hiseq.clinical`

`ssh localhost`
  
If you made changes to internal app : `systemctl --user restart statina.target` 

Your branch should be deployed to staging at https://statina-stage.scilifelab.se 

If for some reason you cannot access the application at given address, check status of the container: `systemctl --user status statinaApp.service`

### Deploying to production

Use `update-statina.sh` script to update production both on Hasta and CGVS. 
**Please follow the development guide and `servers` repo when doing so. It is also important to keep those involved informed.**

## Back End
The Statina database is a Mongo database consisting of following collections:

- **batch** - holds batch level information.
- **sample** - holds sample level information.
- **user** - holds user names, emails and roles.

The database is loaded through the CLI with data generated by the [FluFFyPipe][Fluffy]


[Fluffy]: https://github.com/Clinical-Genomics/fluffy
[WisecondorX]: https://github.com/CenterForMedicalGeneticsGhent/WisecondorX
[docker-hub]: https://hub.docker.com/repository/docker/clinicalgenomics/statina
