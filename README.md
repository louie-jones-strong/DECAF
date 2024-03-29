# Dynamic Exploration of Curated Agents Framework (DECAF)

## Status
![Unit Tests](https://github.com/louie-jones-strong/DECAF/actions/workflows/UnitTests.yml/badge.svg)
![Lint Checks](https://github.com/louie-jones-strong/DECAF/actions/workflows/LintChecks.yml/badge.svg)
![Docs Build](https://github.com/louie-jones-strong/DECAF/actions/workflows/DocsCreation.yml/badge.svg)
<!-- ![Type Hint Checks](https://github.com/louie-jones-strong/DECAF/actions/workflows/TypeHintChecks.yml/badge.svg) -->


## About
This project has been created as part of my final year dissertation at the University of London.
The project is an implementation of the reinforcement learning framework DECAF, proposed in my dissertation.
DECAF trains agents' policies to maximise the expected reward in a environment.
DECAF allows for tuning the agents' behaviours to mimic human behaviours or a custom curated behaviour.

Find the documentation [here](https://louie-jones-strong.github.io/DECAF/)

## Requirements
- [Python 3.8.10](https://www.python.org/downloads/release/python-3810/)
- [Docker](https://www.docker.com/get-started)
- WSL2 (Windows only)
- [Optional] [wandb](https://wandb.ai/site) account to track runs

## Quick Start
1. Clone the repository
2. Run the following commands in the root directory
```
Setup.bat
```
```
docker-compose build
```
```
docker-compose up
```
3. Navigate to ```localhost:5000``` in your browser

You can modify the settings in the `.env` file.



## Logging to wandb
To log runs to wandb, create a file called `secrets.env` in the root directory with the following contents:
```
WANDB_API_KEY=<your api key>
```


## Local Development
Note. The trajectory server will not work on Windows.

1. Run `Setup.bat` to create a virtual environment and install the required packages


### Running Tests
Run `RunTests.bat` in the root directory to run all tests

### Updating Documentation
Run `CreateDocs.bat` in the root directory to update the documentation