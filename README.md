# GESI_DE 

## Introduction
----- <br>
<br>
This project is powered by Green Energy Strategy Institute(GESI) <br>

## Package Structure
`examples/`: Contains example codes for running Gesi Model<br>
`gesi_model/`: Main source directory for Gesi Model Project <br>

## Setting up Environment
- Create Virtual Environment

You can use any python virtual environment.

```
# Create conda environment
# python version must be 3.7 or 3.8
$ conda create -n [env name] python=[python version]

# Create virtualenv
$ python3 -m venv [virtualenv path] --python=[python path]
```

- Install Packages
```
# Install packages via requirements.txt
$ pip install -r requirements.txt

# Direct Installation
$ pip install conda-forge pyomo cplex pandas openpyxl jupyter

# Installation using conda
$ conda install -c conda-forge pyomo cplex 
$ conda install pandas openpyxl jupyter
```

## Running Gesi Model
It is possible to look up example code for running default Gesi Model using GESI_DE.xlsx data in `examples/` directory.<br>
The code below is `examples/gesi.py`.

```
"""
    Default Gesi Model Example
"""
import os
import sys

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

web_model_dir = os.path.join(parent_dir, 'gesi_model_web')
sys.path.append(web_model_dir)

from gesi_model_web.run import ModelExecutor

data_path = 'GESI_DE.xlsx'
name = 'gesi_web_jupyter'

executor = ModelExecutor(data_path, name=name, save_result=True, solver='cplex', verbose=1)
solver = executor.run_once()
