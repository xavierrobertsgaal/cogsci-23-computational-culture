# Runs the agent-based simulation and saves results to file.

##### Imports
import pandas as pd
import numpy as np
from scipy.special import softmax
from joblib import Parallel, delayed
from joblib_progress import joblib_progress
import argparse
import sys
import os

##### Functions and classes

class Agent:
    def __init__(self, id: int, strategy: str, env, rng, **kwargs) -> None:
        self.id = id
        self.strategy = strategy
        self.Lambda = env.mb_learn_cost
        self.Kappa = env.ind_learn_cost
        self.observed = [None, None]
        self.action = kwargs.get('action', rng.choice(env.actions))
        self.outcome = kwargs.get('outcome', env.current_outcomes[self.action])
        self.payoff = 0
        self.parent = kwargs.get('parent', None)

    def observe(self, other):
        self.observed = [other.action, other.outcome]
    
    def act(self, env) -> None:
        if self.strategy == 'MF':
            self.action = self.observed[0]
            self.outcome = env.current_outcomes[self.action]
            self.payoff = env.payoffs[self.outcome]
        elif self.strategy == 'MB':
            self.outcome = self.observed[1]
            # Find the fish that would have led to this outcome
            if env.current_outcomes["Grub"] == self.outcome:
                self.action = "Grub"
            else:
                self.action = "Worm" 
            self.payoff = env.payoffs[self.outcome] - self.Lambda
        elif self.strategy == 'IL':
            self.action = env.best_action
            self.outcome = env.current_outcomes[self.action]
            self.payoff = env.payoffs[self.outcome] - self.Kappa
        else:
            raise ValueError('Invalid strategy. Can only be one of "MF", "MB", "IL"')
    
    def get_id(self) -> int:
        return self.id

    def get_strategy(self) -> str:
        return self.strategy
    
    def get_action(self) -> str:
        return self.action
    
    def get_outcome(self) -> str:
        return self.outcome
    
    def get_payoff(self) -> int:
        return self.payoff
    
    def get_parent(self) -> int:
        return self.parent
    
    def set_parent(self, parent) -> None:
        self.parent = parent


class World:
    def __init__(self, rng, Lambda: float = 0.2, Kappa: float = 0.5, Delta: float = 0.2) -> None:
        self.agents = []
        self.gen = 0
        self.rng = rng
        self.shock_prob = Delta
        self.shock = False
        self.mb_learn_cost = Lambda
        self.ind_learn_cost = Kappa
        self.states = ["Heads", "Tails"]
        self.current_state = "Heads"
        self.possible_outcomes = {"Heads": {"Grub" : "Shep", "Worm" : "Heth"}, "Tails": {"Grub" : "Heth", "Worm" : "Shep"}}
        self.current_outcomes = self.possible_outcomes[self.current_state]
        self.actions = ["Grub", "Worm"]
        self.payoffs = {"Shep" : 1, "Heth" : -1}
        self.best_action = "Grub"
    
    def add_agent(self, id: int, **kwargs) -> None:
        kwargs.setdefault('strategy', self.rng.choice(['MF', 'MB', 'IL']))
        self.agents.append(
            Agent(id = id, env = self, rng = self.rng, **kwargs)
            )
    
    def set_shock_prob(self, shock_prob: float) -> None: # Needed to change the shock probability dynamically
        self.shock_prob = shock_prob

    def set_possible_outcomes(self, possible_outcomes: dict) -> None:
        self.possible_outcomes = possible_outcomes

    def set_actions(self, actions: list) -> None:
        self.actions = actions

    def set_payoffs(self, payoffs: dict) -> None:
        self.payoffs = payoffs
    
    def set_best_action(self, best_action: str) -> None:
        self.best_action = best_action

    def set_gen(self, gen: int) -> None:
        self.gen = gen
    
    def get_agent(self, id: int) -> Agent:
        return self.agents[id]
    
    def get_agents(self) -> list:
        return self.agents
    
    def get_gen(self) -> int:
        return self.gen
    
    def get_best_action(self) -> str:
        return self.best_action
    
    def get_shock_prob(self) -> float:
        return self.shock_prob
    
    def get_mb_learn_cost(self) -> float:
        return self.mb_learn_cost
    
    def get_ind_learn_cost(self) -> float:
        return self.ind_learn_cost

    def get_actions(self) -> list:
        return self.actions

    def get_possible_outcomes(self) -> dict:
        return self.possible_outcomes

    def get_payoffs(self) -> dict:
        return self.payoffs
    
    def get_agent_count(self) -> int:
        return len(self.agents)
    
    def get_agent_ids(self) -> list:
        return [agent.id for agent in self.agents]
    
    def get_agent_strategies(self) -> list:
        return [agent.strategy for agent in self.agents]
    
    def get_agent_actions(self) -> list:
        return [agent.action for agent in self.agents]
    
    def get_agent_outcomes(self) -> list:
        return [agent.outcome for agent in self.agents]
    
    def get_agent_payoffs(self) -> list:
        return [agent.payoff for agent in self.agents]
    
    def get_agent_observed(self) -> list:
        return [agent.observed for agent in self.agents]
    
    def get_agent_observed_actions(self) -> list:
        return [agent.observed[0] for agent in self.agents]
    
    def get_agent_observed_outcomes(self) -> list:
        return [agent.observed[1] for agent in self.agents]
    
    def assign_observations(self) -> None:
        for agent in self.agents:
            observed_agent = self.rng.choice([a for a in self.agents if a != agent])
            agent.observe(observed_agent)

    def get_agent_parents(self) -> list:
        return [agent.parent for agent in self.agents]

    def step(self) -> None:
        # Kill one agent at random
        self.agents.pop(self.rng.integers(0, len(self.agents)))
        
        # Calculate whether a shock occurred
        self.shock = self.rng.choice([True, False], p=[self.shock_prob, 1 - self.shock_prob]) # Change to sampling whether number is less than
        # If a shock occurred, randomly select the action-outcome mappings
        if self.shock:
            self.current_state = self.rng.choice(self.states) 
            self.current_outcomes = self.possible_outcomes[self.current_state]
            # Set the best action to the one that catches the Shep fish
            self.best_action = "Grub" if self.current_outcomes["Grub"] == "Shep" else "Worm"
        
        # Assign observations
        self.assign_observations()

        # Update agents
        for agent in self.agents:
            agent.act(self)
        
        # Choose one agent to reproduce using a softmax proportional to payoffs
        payoffs = softmax(np.array(self.get_agent_payoffs(), dtype="float"))

        # With probability 0.95 choose the agents in proportion to their payoffs. With probability 0.05 choose a type at random
        if self.rng.choice([True, False], p=[0.95, 0.05]):
            parent = self.rng.choice(self.agents, p=payoffs)
            # Add a new agent with the same strategy as the parent, but with a new id and parent
            self.add_agent(id = self.get_agent_count() + self.gen + 1, 
                       strategy = parent.get_strategy(), 
                       action = parent.get_action(), 
                       outcome = parent.get_outcome(),
                       parent = parent.get_id())
        else:
            # Add a new agent with a random strategy
            self.add_agent(id = self.get_agent_count() + self.gen + 1,
                            strategy = self.rng.choice(['MF', 'MB', 'IL']))

        # Advance the generation
        self.gen += 1

    def run(self, gens) -> pd.DataFrame:
        df = pd.DataFrame([])
        for i in range(gens):
            df = pd.concat([df, pd.DataFrame({
                'gen': self.gen,
                'agent_id': self.get_agent_ids(),
                'strategy': self.get_agent_strategies(),
                'action': self.get_agent_actions(),
                'outcome': self.get_agent_outcomes(),
                'payoff': self.get_agent_payoffs(),
                'observed_action': self.get_agent_observed_actions(),
                'observed_outcome': self.get_agent_observed_outcomes(),
                'parent': self.get_agent_parents(),
                'shock': self.shock,
                'state': self.current_state,
                'best_action': self.best_action,
                'delta': self.get_shock_prob(),
                'lambda': self.get_mb_learn_cost(),
                'kappa': self.get_ind_learn_cost()
            })], ignore_index=True)
            
            self.step()
        return df
    

def simulate(path: str, size: int, gens: int, Delta: float, Lambda: float, Kappa: float, seed: int = 42) -> pd.DataFrame:
    """
    Simulate a Moran process with the given parameters.
    
    path: Folder to save the simulation results to
    size: Initial population size
    gens: Number of generations to simulate
    Delta: Probability of shock
    Lambda: Model-based social learning cost
    Kappa: Individual learning cost
    seed: Random number generator seed

    Returns a pandas DataFrame of shape (gen * size, 10) with the following columns:
    - gen: Generation
    - agent_id: Unique id per agent
    - strategy: Agent's strategy (MB, MF, or IL)
    - action: Agent's action (Grub or Worm bait)
    - outcome: Agent's outcome (Shep or Heth fish)
    - payoff: Agent's payoff (1 or -1)
    - shock: Whether there was a shock prior to the current generation
    - state: Current state of the world (controls the transition matrix, Heads or Tails)
    - best_action: The best action given the current state of the world

    Also, saves a .csv file with the simulation results to the given path, including parameters in the filename.
    """
    # print(f"Running simulation with parameters size={size}, gens={gens}, Delta={Delta}, Lambda={Lambda}, Kappa={Kappa}, seed={seed}") 
    rng = np.random.default_rng(seed=seed) # LOOK INTO WHETHER I CAN PREGENERATE
    env = World(rng=rng, Delta=Delta, Lambda=Lambda, Kappa=Kappa)
    for i in range(size):
        env.add_agent(id = i)
    df = env.run(gens)
    df.to_csv(f"{path}_size={size}_gens={gens}_Delta={Delta}_Lambda={Lambda}_Kappa={Kappa}_seed={seed}.csv", index=False)
    return df


##### Run the simulation with the given parameters

if __name__ == '__main__':

    # Obtain the parameters from the command line

    parser = argparse.ArgumentParser(prog='agentsimulation_script.py',
                                     description='Run an agent-based Moran process simulation of the cultural evolution of social learning')
    
    parser.add_argument('--path', type=str, default='sims/sim', help='Path prototype for simulation results')
    parser.add_argument('--size', type=int, default=120, help='Initial population size')
    parser.add_argument('--gens', type=int, default=5000, help='Number of generations to simulate')
    parser.add_argument('--lo', type=float, default=0.0, help='Lower bound of parameter space to vary')
    parser.add_argument('--hi', type=float, default=1.0, help='Higher bound of parameter space to vary')
    parser.add_argument('--ns', type=int, default=11, help='How many values to interpolate between lo and hi')
    parser.add_argument('--seed', type=int, default=42, help='Random number generator seed')
    parser.add_argument('--ncores', type=int, default=1, help='Number of cores to use')
    parser.add_argument('--params_path', type=str, default=None, help='Optional path containing a .csv file with parameters to run. Overrides lo, hi, and ns if input. Parameters must contain columns named `Delta`, `Lambda`, and `Kappa`.')

    args = parser.parse_args()

    # Create the folder to save the simulation results to if it doesn't exist

    if not os.path.exists(os.path.dirname(args.path)):
        os.makedirs(os.path.dirname(args.path))

    # Run the simulation, in parallel, with the given parameters

    if args.params_path is not None:
        try:
            params = pd.read_csv(args.params_path)
        except Exception as e:
            print(f"Error reading parameters from {args.params_path}. Make sure `--params_path` is a .csv. Error: {e}")
            sys.exit(1)
        with joblib_progress("Simulation progress", total=len(params)):
            Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Lambda=L, Kappa=K, seed=args.seed) 
                                         for D, L, K in zip(params['Delta'], params['Lambda'], params['Kappa']))
    else:
        with joblib_progress("Simulation progress", total=args.ns**3):
            Parallel(n_jobs=args.ncores)(delayed(simulate)(path=args.path, size=args.size, gens=args.gens, Delta=D, Lambda=L, Kappa=K, seed=args.seed) 
                                        for D in np.linspace(args.lo, args.hi, args.ns) 
                                        for L in np.linspace(args.lo, args.hi, args.ns) 
                                        for K in np.linspace(args.lo, args.hi, args.ns))