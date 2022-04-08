#####

# @fiete
# November 12, 2020

# run like python3.9 main_complete.py -c config.conf -s 2700001 -r Generations -a 10 -t 60 -p True -i instances/test_1_heuristic -pe 5000 -u 1000

#####

"""
Usage:
  main_complete.py -c <config_file> -s <seed> -r <stop_rule> \
-a <stop_arg> -t <max_time> -p <pre_solve> -i <instance_file> \
-q <penalty> -u <upper_t_limit> [--no_evolution]
  main_complete.py (-h | --help)
Options:
  -c --config_file <arg>    Text file with the BRKGA-MP-IPR parameters.
  -s --seed <arg>           Seed for the random number generator.
  -r --stop_rule <arg>      Stop rule where:
                            - (G)enerations: number of evolutionary
                              generations.
                            - (I)terations: maximum number of generations
                              without improvement in the solutions.
                            - (T)arget: runs until obtains the target value.
  -a --stop_arg <arg>       Argument value for '-r'.
  -t --max_time <arg>       Maximum time in seconds.
  -p --pre_solve <arg>      Choose whether warm start should be enabled or not (True / False)
  -i --instance_file <arg>  Instance file.
  -q --penalty <arg>       Penalty value for leaving a person behind
  -u --upper_t_limit <arg>  Upper time limit 
  --no_evolution      If supplied, no evolutionary operators are applied. So,
                      the algorithm becomes a simple multi-start algorithm.
  -h --help           Produce help message.
"""

from copy import deepcopy
from datetime import datetime
from os.path import basename
import os
import random
import time
# import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import docopt

from brkga_mp_ipr.algorithm import BrkgaMpIpr
from brkga_mp_ipr.enums import ParsingEnum, Sense
from brkga_mp_ipr.types_io import load_configuration

from S_ICEP_instance import SICEPInstance
# from S_ICEP_decoder_experimental import SICEPDecoder
from S_ICEP_decoder import SICEPDecoder
from generate_outputs import generate_results_table

###############################################################################
# Enumerations and constants
###############################################################################

class StopRule(ParsingEnum):
    """
    Controls stop criteria. Stops either when:
    - a given number of `GENERATIONS` is given;
    - or a `TARGET` value is found;
    - or no `IMPROVEMENT` is found in a given number of iterations.
    """
    GENERATIONS = 0
    TARGET = 1
    IMPROVEMENT = 2


###############################################################################

def main() -> None:
    """
    Proceeds with the optimization. Create to avoid spread `global` keywords
    around the code.
    """

    args = docopt.docopt(__doc__)
    # print(args)

    configuration_file = args["--config_file"]
    instance_file = args["--instance_file"]
    seed = int(args["--seed"])
    stop_rule = StopRule(args["--stop_rule"])

    if stop_rule == StopRule.TARGET:
        stop_argument = float(args["--stop_arg"])
    else:
        stop_argument = int(args["--stop_arg"])

    maximum_time = float(args["--max_time"])

    if str(args["--pre_solve"]) == 'True':
        warm_start = True 
    else:
        warm_start = False

    if maximum_time <= 0.0:
        raise RuntimeError(f"Maximum time must be larger than 0.0. "
                           f"Given {maximum_time}.")

    penalty = float(args["--penalty"])
    upper_time_limit = float(args["--upper_t_limit"])

    perform_evolution = not args["--no_evolution"]

    ########################################
    # Load config file and show basic info.
    ########################################

    brkga_params, control_params = load_configuration(configuration_file)

    print(f"""------------------------------------------------------
> Experiment started at {datetime.now()}
> Instance: {instance_file}
> Configuration: {configuration_file}
> Algorithm Parameters:""", end="")

    if not perform_evolution:
        print(">    - Simple multi-start: on (no evolutionary operators)")
    else:
        output_string = ""
        for name, value in vars(brkga_params).items():
            output_string += f"\n>  -{name} {value}"
        for name, value in vars(control_params).items():
            output_string += f"\n>  -{name} {value}"

        print(output_string)
        print(f"""> Seed: {seed}
> Stop rule: {stop_rule}
> Stop argument: {stop_argument}
> Maximum time (s): {maximum_time}
------------------------------------------------------""")

    ########################################
    # Load instance and adjust BRKGA parameters
    ########################################

    print(f"\n[{datetime.now()}] Reading S-ICEP data...")

    # generate an initial S-ICEP instance
    instance = SICEPInstance(os.path.join('instances', instance_file), penalty, upper_time_limit)
    print(f"Number of scenarios: {instance.num_scenarios}")
    print(f"Number of resources: {instance.num_resources}")
    print(f"Maximum number of trips: {instance.max_trips}")

    print(f"\n[{datetime.now()}] Generating initial solution...")

    # Generate a greedy solution to be used as warm start for BRKGA using the heuristic from chapter 3 of the dissertation

    if warm_start == True:
        initial_cost, initial_route_plan = instance.initialize_route_plan_heuristic()
    else:
        initial_cost = 10000 # keep this for now for cold start

    print(f"Initial cost: {initial_cost}")

    ########################################
    # Build the BRKGA data structures and initialize
    ########################################

    print(f"\n[{datetime.now()}] Building BRKGA data...")

    # Usually, it is a good idea to set the population size
    # proportional to the instance size.
    brkga_params.population_size = min(brkga_params.population_size,
                                       instance.num_resources * instance.max_trips * instance.num_scenarios)#int(np.floor(instance.num_resources * instance.num_scenarios * instance.max_trips)/4))# * 10 instance.num_resources * instance.max_trips * instance.num_scenarios) # CHANGE THIS BACK TO A REASONABLE SIZE
    print(f"New population size: {brkga_params.population_size}")

    # Build a decoder object.
    decoder = SICEPDecoder(instance)

    chromosome_size = instance.max_trips * instance.num_scenarios * 2 * instance.num_resources

    # Chromosome size is the number of nodes.
    # Each chromosome represents a permutation of nodes.
    brkga = BrkgaMpIpr(
        decoder=decoder,
        sense=Sense.MINIMIZE,
        seed=seed,
        chromosome_size=chromosome_size,
        params=brkga_params,
        evolutionary_mechanism_on=perform_evolution
    )

    # To inject the initial tour, we need to create chromosome representing that solution.
    random.seed(seed)

    if warm_start == True:
        initial_chromosome = instance.convert_initial_route_plan_to_chromosome(chromosome_size)
    else:
        initial_chromosome = [0] * chromosome_size
    

    # Inject the warm start solution in the initial population.
    brkga.set_initial_population([initial_chromosome])

    # NOTE: don't forget to initialize the algorithm.
    print(f"\n[{datetime.now()}] Initializing BRKGA data...")
    brkga.initialize()

    ########################################
    # Warm up the script/code
    ########################################

    # To make sure we are timing the runs correctly, we run some warmup
    # iterations with bogus data. Warmup is always recommended for script
    # languages. Here, we call the most used methods.
    print(f"\n[{datetime.now()}] Warming up...")

    bogus_alg = deepcopy(brkga)
    bogus_alg.evolve(2)
    # TODO (ceandrade): warm up path relink functions.
    # bogus_alg.path_relink(brkga_params.pr_type, brkga_params.pr_selection,
    #              (x, y) -> 1.0, (x, y) -> true, 0, 0.5, 1, 10.0, 1.0)
    bogus_alg.get_best_fitness()
    bogus_alg.get_best_chromosome()
    bogus_alg = None

    ########################################
    # Evolving
    ########################################

    print(f"\n[{datetime.now()}] Evolving...")
    print("* Iteration | Cost | CurrentTime")

    best_cost = initial_cost * 2
    best_cost_evolution = []
    best_chromosome = initial_chromosome

    iteration = 0
    last_update_time = 0.0
    last_update_iteration = 0
    large_offset = 0
    # TODO (ceandrade): enable the following when path relink is ready.
    # path_relink_time = 0.0
    # num_path_relink_calls = 0
    # num_homogenities = 0
    # num_best_improvements = 0
    # num_elite_improvements = 0
    run = True

    # Main optimization loop. We evolve one generation at time,
    # keeping track of all changes during such process.
    start_time = time.time()
    while run:
        iteration += 1
        # print('Performing iteration:', iteration)

        # Evolves one iteration.
        brkga.evolve()

        # Checks the current results and holds the best.
        fitness = brkga.get_best_fitness()
        if fitness < best_cost:
            last_update_time = time.time() - start_time
            update_offset = iteration - last_update_iteration

            if large_offset < update_offset:
                large_offset = update_offset

            last_update_iteration = iteration
            best_cost = fitness
            best_chromosome = brkga.get_best_chromosome()
            best_cost_evolution.append(best_cost)

            # print(f"* {iteration} | {best_cost:.0f} | {last_update_time:.2f}")
            print(f"* {iteration} | {best_cost} | {last_update_time}")

        # end if

        # TODO (ceandrade): implement path relink calls here.
        # Please, see Julia version for that.

        iter_without_improvement = iteration - last_update_iteration

        # Check stop criteria.
        run = not (
            (time.time() - start_time > maximum_time)
            or
            (stop_rule == StopRule.GENERATIONS and iteration == stop_argument)
            or
            (stop_rule == StopRule.IMPROVEMENT and
             iter_without_improvement >= stop_argument)
            or
            (stop_rule == StopRule.TARGET and best_cost <= stop_argument)
        )
    # end while
    total_elapsed_time = time.time() - start_time
    total_num_iterations = iteration

    print(f"[{datetime.now()}] End of optimization\n")

    print(f"Total number of iterations: {total_num_iterations}")
    print(f"Last update iteration: {last_update_iteration}")
    print(f"Total optimization time: {total_elapsed_time:.2f}")
    print(f"Last update time: {last_update_time:.2f}")
    print(f"Large number of iterations between improvements: {large_offset}")

    # TODO (ceandrade): enable when path relink is ready.
    # print(f"\nTotal path relink time: {path_relink_time:.2f}")
    # print(f"\nTotal path relink calls: {num_path_relink_calls}")
    # print(f"\nNumber of homogenities: {num_homogenities}")
    # print(f"\nImprovements in the elite set: {num_elite_improvements}")
    # print(f"\nBest individual improvements: {num_best_improvements}")

    ########################################
    # Extracting the best tour
    ########################################

    final_cost= decoder.decode(best_chromosome, True)
    final_plan = []

    # create target directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATA_DIR = os.path.join(BASE_DIR, 'core_code/instances', instance_file)
    SOL_DIR = os.path.join(DATA_DIR, 'Solutions')

    # create new folders if they do not exist
    if os.path.exists(SOL_DIR):
        pass
    else:
        os.makedirs(SOL_DIR)

    # change working directory and set seed
    os.chdir(SOL_DIR)

    for scenario in range(len(instance.scenario_names)):
        final_plan.append(generate_results_table(instance.resources[scenario]))
        generate_results_table(instance.resources[scenario]).to_csv(os.path.join(SOL_DIR, 'route_plan_scenario_' + str(scenario + 1) + '_BRKGA.csv'))

    # print(f"\n% Best plan cost: {best_cost:.2f}")
    print(f"\n% Best plan cost: {best_cost}")
    print("% Best plan: ", end="")
    print(final_plan)
    print("Best chromosome:")
    print(best_chromosome)
    

    print("\n\nInstance,Seed,NumScenarios,NumResources,NumMaxTrips,TotalIterations,TotalTime,"
          #"TotalPRTime,PRCalls,NumHomogenities,NumPRImprovElite,"
          #"NumPrImprovBest,"
          "LargeOffset,LastUpdateIteration,LastUpdateTime,"
          "Cost")
    print(f"{basename(str(instance_file))},"
          f"{seed},{instance.num_scenarios},{instance.num_resources},{instance.max_trips},{total_num_iterations},"
          f"{total_elapsed_time:.2f},"
          # f"{path_relink_time:.2f},{num_path_relink_calls},"
          # f"{num_homogenities},{num_elite_improvements},{num_best_improvements},"
          f"{large_offset},{last_update_iteration},"
          f"{last_update_time:.2f},{best_cost:.0f}")

    with open(os.path.join(SOL_DIR, 'performance_statistics_BRKGA.txt'), 'w') as f:
        f.write("\n\nInstance,Seed,NumScenarios,NumResources,NumMaxTrips,TotalIterations,TotalTime,"
          #"TotalPRTime,PRCalls,NumHomogenities,NumPRImprovElite,"
          #"NumPrImprovBest,"
          "LargeOffset,LastUpdateIteration,LastUpdateTime,"
          "Cost")
        f.write(f"{basename(str(instance_file))},"
          f"{seed},{instance.num_scenarios},{instance.num_resources},{instance.max_trips},{total_num_iterations},"
          f"{total_elapsed_time:.2f},"
          # f"{path_relink_time:.2f},{num_path_relink_calls},"
          # f"{num_homogenities},{num_elite_improvements},{num_best_improvements},"
          f"{large_offset},{last_update_iteration},"
          f"{last_update_time:.2f},{best_cost}")
        f.close()

    print("******")
    print("Evolution of objective values")
    # print(decoder.return_objective_evolution())

    # create a plot with objective evolution

    x = np.linspace(0, len(best_cost_evolution), len(best_cost_evolution))
    y = best_cost_evolution

    plt.plot(x, y)
    plt.yscale('log') # change to logarithmic scale
    plt.savefig(os.path.join(SOL_DIR, 'best_objective_evolution_BRKGA.png'))
    # plt.show()

###############################################################################

if __name__ == "__main__":
    main()