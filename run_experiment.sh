#!/bin/bash

# run this here first
# chmod +x ./run_experiment.sh

# run like
# ./run_experiment.sh 123 5 5 2 auto_generated_2 100 600 1000 5000

# This is a bash file to run an analysis of the added value of considering 
# cruising data in the travel distance matrix in a commercial vehicle route

seed=$1 # argument setting the seed for the simulation
resources=$2 # number of resources to be generated in artifical data
locations=$3 # number of locations to be randomly generated in artificial data
scenarios=$4 # number of randomly generated evacuation scenarios in artificial data
name=$5 # name for the randomly generated data
argument=$6 # argument setting the number of generations to evolve in BRKGA
run_time_limit=$7 # argument setting the maximum time length for the algorithms to run in seconds
plan_length_limit=$8 # argument setting the maximum length of the evacuation plan in minutes
penalty=$9 # penalty for not evacuating a single person
# instance=$4 # argument setting the instance file path

file_path='/instances/$name'

# generate an artifical data set
# python generate_test_data.py -s $seed -r $resources -l $locations -sc $scenarios -n $name

# run the experiment with Gurobi
python pyomo_ICEP_model_run.py -path $name -penalty $penalty -route_time_limit $plan_length_limit -run_time_limit $run_time_limit
# 
# run the experiment in the BRKGA with presolve
python main_complete.py -c config.conf -s $seed -r IMPROVEMENT -a $argument -t $run_time_limit -p True -i $name -q $penalty -u $plan_length_limit

# run the experiment in the constructive heuristic
# python greedy_simple_stochastic_search.py -path $name -time_limit $time_limit -penalty $penalty

# analyze the difference in the route times and save into a reporting files
# python analyze_route_differences.py -s $seed -a $argument -t $time_limit -i $instance

