# Control Plane Project

## Overview
The Control Plane project is designed to manage and schedule tasks based on input data. It processes input files, formats the data, and generates output schedules.

## Directory Structure
- `control_plane/`
  - `Makefile`: Contains build instructions and commands for the project.
  - `inputs/`: Directory containing input files for the project.
  - `outputs/`: Directory where output files are stored. file names are timestamped.
    -`schedule_20251201_102202.csv`: Output schedule generated on December 1, 2025, at 10:22:02.
  - `src/`: Source code for the project.
    - `formatter.py`: Contains functions for formatting data.
    - `main.py`: The main entry point for the application.
    - `models.py`: Defines data models used in the project.
    - `parser.py`: Contains functions for parsing input data.
    - `scheduler.py`: Implements scheduling logic.
  - `tests/`: Directory containing test files.
    - `e2e.py`: End-to-end tests for the project.
    - `test_parser.py`: Unit tests for the parser module.
    - `test_scheduler.py`: Unit tests for the scheduler module.
    - `data/`: Directory containing test data.
      - `e2e_ground_truth.csv`: Ground truth data for end-to-end tests.
      - `e2e_input.csv`: Input data for end-to-end tests.

## Starting
To install the project requirements, run:
```
pip install -r requirements.txt
```
in the control_plane dir. We recommend creating a virtual env to isolate the dependencies.

## Usage
To run the project, use the following command:
```bash
make run INPUT=path/to/input/file
```
In addition, you can specify these optional arguments:
```UTIL```: value between 0.01 and 1 that indicate the efficiency of the agent. The default is 1.
```FORMAT```: one of ```[text, json, csv]```. Default is text. `csv` flag produced timestamped csv file to outputs folder.


## Testing
To run the unit tests, execute:
```bash
make unit_tests
```

To run the E2E test, execute:
```bash
make e2e_tests
```

## Viz
To run the viz tool, execute,
```bash
make viz
```
This will start web server on port 8000. Go to http://[::]:8000/ on your local machine and upload the csv file to visualize.