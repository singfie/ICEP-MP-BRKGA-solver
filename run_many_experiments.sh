#!/bin/bash

# run this here first
# chmod +x ./run_many_experiment.sh

# run like
# ./run_many_experiments.sh

# This is a bash file to run a series of experiments benchmarking the BRKGA against Gurobi

for VARIABLE in 1 2 3 4 5
do
	RESOURCES=$(( $VARIABLE * 2 ))
	echo "$RESOURCES"
	LOCATIONS=$(( $VARIABLE * 2 ))
	echo "$LOCATIONS"
	SCENARIOS=$VARIABLE
	echo "$SCENARIOS"
	NAME='auto_generated_'${VARIABLE}
	echo "$NAME"
	./run_experiment.sh ${VARIABLE} ${RESOURCES} ${LOCATIONS} ${SCENARIOS} "$NAME" 10 7200 1000 5000
done
