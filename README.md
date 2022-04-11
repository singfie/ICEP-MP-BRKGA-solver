# ICEP-MP-BRKGA-solver
A solution approach for the Isolated Community Evacuation Problem (ICEP) using the Multi-Parent Biased Random Key Genetic Algorithm (MP-BRKGA).

The Isolated Community Evacuation Problem (ICEP) presented by Krutein and Goodchild (2022), is an evacuation routing problem for communities without permanent road connections that can be used to evacuate a population. As the paper highlights, the problem is complex and for large instances difficult to solve for a commercial solver. Exact implementations presented in package https://github.com/singfie/ICEP-exact-implementation struggled to solve the problem as quickly as desired in an emergency evacuation. While attempts were made to solve the problem more efficiently through a structure-based greedy heuristic in package https://github.com/singfie/ICEP-structured-greedy-heuristics, these heuristics were not reliably capable to reach a high solution quality. This package aims to approximately solve the problem with the MP-BRKGA meta-heuristic. The original MP-BRKGA framework can be found under https://github.com/ceandrade/brkga_mp_ipr_python. 

The corresponding paper was submitted to the Proceedings of the Winter Simulation Conference 2022 for presentation and publication. 

# File descriptions

# dock.py
This file implements an instance of an evacuation dock (evacuation pick-up and drop-off points)

# location.py
This file implements an instance of a location

# evacLocation.py
This file implements an instance of an evacuation location, and forms a sub-class of "location.py"

# evacRes.py
This file implements an evacuation resource. 

# config.conf
This configuration file controls the parameters of the MP-BRKGA that can be controlled. 

# main_complete.py
This file is the interface to the MP-BRKGA algorithm environment and houses the genetic algorithm process

# S-ICEP_decoder.py
This file contains the custom decoder developed for the S-ICEP, that was presented in the paper mentined above. 

# S-ICEP_decoder_experimental.py
This file contains a revised version of the "S_ICEP_decoder.py" for parallel processing. This is particularly useful for larger problem instances. 

# run_experiment.sh 
This file implements the run of a single experiment, benchmarking the MP-BRKGA implementation against using the Gurobi solver, as implemented in code repository https://github.com/singfie/ICEP-exact-implementation

# run_many_experiments.sh
This file implements the runs of an entire list of experiments. 

# generate_test_data.py
This file generates an artifical set of simulation data.

# generate_outputs.py
This file prints outputs from the best solution of the MP-BRKGA, in the form of a route plan. 

