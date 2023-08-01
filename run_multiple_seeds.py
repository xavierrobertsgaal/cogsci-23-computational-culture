# Helper script to run multiple simulations in sequence, varying the random seed
# Requires being in the same directory as `run_simulation.py` or `run_simulation_gn.py`

import os
import sys
import argparse
import pandas as pd
import numpy as np
from scipy.special import softmax
from joblib import Parallel, delayed
from joblib_progress import joblib_progress

parser = argparse.ArgumentParser(prog = 'run_multiple_seeds.py', description = 'Run multiple simulations in sequence, varying the random seed')
# Arguments for running multiple simulations
parser.add_argument('--seed_start', type = int, default = 42, help = 'Random seed to start at')
parser.add_argument('--seed_step', type = int, default = 1, help = 'Increment to increase the random seed by')
parser.add_argument('--num_seeds', type = int, default = 10, help = 'Number of simulations to run')
parser.add_argument('--gn', action = 'store_true', help = 'Whether to run the GN model')
# Arguments needed to run the simulation
parser.add_argument('--path', type=str, default='sims/sim', help='Path prototype for simulation results')
parser.add_argument('--size', type=int, default=120, help='Initial population size')
parser.add_argument('--gens', type=int, default=5000, help='Number of generations to simulate')
parser.add_argument('--lo', type=float, default=0.0, help='Lower bound of parameter space to vary')
parser.add_argument('--hi', type=float, default=1.0, help='Higher bound of parameter space to vary')
parser.add_argument('--ns', type=int, default=11, help='How many values to interpolate between lo and hi')
### parser.add_argument('--seed', type=int, default=42, help='Random number generator seed') # Cannot use this because it is used to vary the seed
parser.add_argument('--ncores', type=int, default=1, help='Number of cores to use')
parser.add_argument('--params_path', type=str, default=None, help='Optional path containing a .csv file with parameters to run. Overrides lo, hi, and ns if input. Parameters must contain columns named `Delta`, `Lambda`, and `Kappa`.')


# Parse the arguments
args = parser.parse_args()

# Construct the random seeds
seeds = range(args.seed_start, args.seed_start + args.seed_step * args.num_seeds, args.seed_step)

# Run the simulations
if args.gn:
    from run_simulation_gn import simulate
else:
    from run_simulation import simulate

# Create the folder to save the simulation results to if it doesn't exist.
if not os.path.exists(os.path.dirname(args.path)):
    os.makedirs(os.path.dirname(args.path))

# Run the simulation, in parallel, with the given parameters
if args.params_path is not None:
    try:
        params = pd.read_csv(args.params_path)
    except Exception as e:
        print(f"Error reading parameters from {args.params_path}. Make sure `--params_path` is a .csv. Error: {e}")
        sys.exit(1)
    if "Seed" in params.columns:
        if args.gn:
            with joblib_progress("Simulation progress", total=len(params)):
                Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Kappa=K, seed=seed) 
                                            for D, K, seed in zip(params['Delta'], params['Kappa'], params['Seed'].astype(int)))
        else:
            with joblib_progress("Simulation progress", total=len(params)):
                Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Lambda=L, Kappa=K, seed=seed) 
                                            for D, L, K, seed in zip(params['Delta'], params['Lambda'], params['Kappa'], params['Seed'].astype(int)))
    else:
        if args.gn:
            with joblib_progress("Simulation progress", total=len(params)*args.num_seeds):
                Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Kappa=K, seed=seed) 
                                            for D, K in zip(params['Delta'], params['Kappa'])
                                            for seed in seeds)
        else:
            with joblib_progress("Simulation progress", total=len(params)*args.num_seeds):
                Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Lambda=L, Kappa=K, seed=seed) 
                                            for D, L, K in zip(params['Delta'], params['Lambda'], params['Kappa'])
                                            for seed in seeds)
else:
    if args.gn:
        with joblib_progress("Simulation progress", total=args.ns**3*args.num_seeds):
            Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Kappa=K, seed=seed) 
                                        for D in np.linspace(args.lo, args.hi, args.ns) 
                                        for K in np.linspace(args.lo, args.hi, args.ns)
                                        for seed in seeds)
    else:
        with joblib_progress("Simulation progress", total=args.ns**3*args.num_seeds):
            Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Lambda=L, Kappa=K, seed=seed) 
                                        for D in np.linspace(args.lo, args.hi, args.ns) 
                                        for L in np.linspace(args.lo, args.hi, args.ns) 
                                        for K in np.linspace(args.lo, args.hi, args.ns)
                                        for seed in seeds)