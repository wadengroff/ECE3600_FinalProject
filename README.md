# Monte Carlo Simulation for Data Center Redundancy Models

Uses realistic probabilities of failure, capacities, UPS efficiencies, and more to create a working simulation of a specified number of hours. Also generates plots to easily visualize the data.

Input load data comes from a trace provided by google. Google's trace provided percent capacity of the load over every 5 minutes, but a python script converts this csv file into the wattage required each hour.


## Redundancy models
- N redundancy
    - Minimum protection, consisting of a single UPS
- Isolated N+1 Redundancy
    - Static bypass of one UPS supplied by a secondary
- N+1 Redundancy
    - Two separate UPS modules connected in parallel, sharing the load
- Catcher Redundancy
    - 2 main UPS modules, with a third that picks up the slack in the event of any errors with the main two


## Running the simulation
Step 1: Open the python directory in a terminal
Step 2: if not installed, run pip install matplotlib numpy
Step 3: Change any simulation parameters you want
Step 4: python simulation.py
Step 5: View the graphs produced