![Latest PR Test](https://github.com/zuzg/drug-screening/actions/workflows/test-pull-request.yml/badge.svg)
![Prod Deployment](https://github.com/zuzg/drug-screening/actions/workflows/prod-deploy.yml/badge.svg)
![Staging Deployment](https://github.com/zuzg/drug-screening/actions/workflows/staging-deploy.yml/badge.svg)

[![badges-are-fun](https://img.shields.io/badge/badges_are-fun-deeppink.svg)](https://tenor.com/view/excited-ron-swanson-giggle-so-much-fun-gif-14647008)
![fail](https://img.shields.io/badge/unless_they-fail-red.svg)

# drug-screening

## About

A project examining data from High Throughput Screening center in Poznan. HTS goal is to identify active compounds from hundreds of thousands.

## Setup

### Prepare repository

```
git clone https://github.com/zuzg/drug-screening.git
```

```
cd drug-screening
```

### Prepare environment

```
conda env create -f environment.yml
```

```
conda activate drug-screening
```

### Starting the dashboard

To start the dashboard enter the following command in the terminal (active in the root project directory) while the conda environment is active:

```
python -m dashboard
```
