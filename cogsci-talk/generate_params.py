# Make a CSV with the following columns: Delta, Lambda, Kappa and the parameters used in the cogsci talk
import numpy as np
import pandas as pd

deltas = np.repeat(np.linspace(0.0, 1.0, 101).round(2), 30)
lambdas = np.tile(np.linspace(0.1, 0.3, 3).round(2), 1010)
kappas = np.repeat(0.4, 3030)
seeds = np.tile(np.arange(42, 52), 303)
# cast all elements of seeds to ints so they can be random seeds
seeds = [int(s) for s in seeds]

cols = ['Delta', 'Lambda', 'Kappa', 'Seed']
df = pd.DataFrame(np.array([deltas, lambdas, kappas, seeds]).T, columns=cols)

if __name__ == '__main__':
    df.to_csv('params.csv', index=False)
