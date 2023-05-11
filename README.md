# Computational principles underlying the evolution of cultural learning mechanisms

Code and data to reproduce simulation results from the paper, "Computational principles underlying the evolution of cultural learning mechanisms", accepted at CogSci 2023.

## Figures and data:
- Figures (.eps and .png versions) can be found in `plots/`.
- Underlying data from the figures can be found in `data/`.
- Simulation results from the paper (generated using default settings) can be downloaded from [this link](https://drive.google.com/drive/folders/1aHKY3w87sThStZ6kIuN17yP0NG2Yyx7I?usp=share_link).

## Key files for reproducing simulation and analyses:
- `create_charts.R` generates the figures used in the paper. It requires that analyzed simulation data is present in `data/`, and it outputs figures to `plots/`.
- `data_cleaning.ipynb` contains functionality to clean and analyze simulation results. It requires simulation results in `sims/` or `sims_gn/` and it saves prepared simulation data to `data/`.
- `run_simulation_gn.py` launches the Model 1 simulation. It can be used from the command line. Documentation is below.
- `run_simulation.py` generates the Model 2 simulation from the command line, as below.
- `theme_mprl_ggplot.R` contains a `ggplot` theme for recreating figures.

### Guide to simulation script
1. Ensure you are using `python >= 3.11.1` and that you have cloned the git repo into the appropriate folder. This may, but is not guaranteed to, work with earlier python versions.
2. Install requirements using
```
pip install --upgrade pip
pip install -r requirements.txt
```
3. Launch the simulation by typing `python run_simulation.py` or `python run_simulation_gn.py` (this takes a while!).

*Note: The simulation scripts take the following arguments:*
  - `--path`: The path to save simulation results (defaults to `sims/` or `sims_gn/` depending on the script)
  - `--size`: Initial population size (default `120`)
  - `--gens`: Number of generations to simulate (default `5000`)
  - `--lo`: Lower bound of parameter space (default `0.0`)
  - `--hi`: Upper bound of parameter space (default `1.0`)
  - `--ns`: Number of steps; how many values to interpolate between `lo` and `hi` (default `11`)
  - `--seed`: Random number generator seed (default `42`)
  - `--ncores`: Number of CPU cores to use **(defaults to a single core, which is *extremely* slow. Suggest using a multiple of `ns`)**
  - `--params_path`: Optional argument containing a **.csv file** with the parameters to run in columns named `Delta`, `Lambda`, and `Kappa`. If used, this overrides `lo`, `hi`, and `ns`. This will throw an error if the file is not a .csv formatted correctly.

Please create an issue here or email the corresponding author (Xavier Roberts-Gaal) if you have any questions.
