"""
@fiete
November 12, 2020
"""

#####

# import packages
import argparse
import pandas as pd
import os
import random
import numpy as np
# from scipy.stats import expon

# AUXILIARY FUNCTIONS

def generate_locations_and_docks_data(number_locations):
	"""Generate locations and docks"""
	safe_locations = pd.DataFrame({
		'Location': pd.Series([], dtype = 'str'), # Location name
		'Docks': pd.Series([], dtype = 'str'), # comma separated list of docks at the location
		'Type': pd.Series([], dtype = 'str') # type of either "Evacuation" or "Safe"
		})
	evac_locations = pd.DataFrame({
		'Location': pd.Series([], dtype = 'str'), # Location name
		'Docks': pd.Series([], dtype = 'str'), # comma separated list of docks at the location
		'Type': pd.Series([], dtype = 'str') # type of either "Evacuation" or "Safe"
		}) # make a copy

	safe_docks = pd.DataFrame({
		'Dock': pd.Series([], dtype = 'str'), # dock name
		'Location': pd.Series([], dtype = 'str'), # location the dock is allocated to
		'Type': pd.Series([], dtype = 'str'), # type of dock, either 'Evaucation' or 'Safe'
		})
	evac_docks = pd.DataFrame({
		'Dock': pd.Series([], dtype = 'str'), # dock name
		'Location': pd.Series([], dtype = 'str'), # location the dock is allocated to
		'Type': pd.Series([], dtype = 'str'), # type of dock, either 'Evaucation' or 'Safe'
		}) # make a copy

	# discrete values
	types = ['Evacuation', 'Safe']

	part_a = random.randint(1,number_locations-1)
	# print(part_a)
	part_b = number_locations - part_a
	# print(part_b)

	num_safe_locations = part_a #np.random.poisson(part_a, 1)[0]
	num_evac_locations = part_b # np.random.poisson(part_b, 1)[0]

	# for each save location, generate docks
	for location_index in range(num_safe_locations):
		location_name = 'Safe Location ' + str(location_index)
		num_docks = np.random.poisson(2, 1)[0] + 1
		dock_names = ''
		for dock_index in range(num_docks):
			dock_name = 'Safe dock ' + str(location_index) + str(dock_index)
			safe_docks = safe_docks.append({'Dock': dock_name,
								  'Location': location_name,
								  'Type': 'Safe'}, ignore_index = True)
			if dock_names == '':
				dock_names = dock_name
			else:
				dock_names = dock_names + ', ' + dock_name

		safe_locations = safe_locations.append({'Location': location_name,
							  'Docks': dock_names,
							  'Type': 'Safe'}, ignore_index = True)

	# for each save location, generate docks
	for location_index in range(num_evac_locations):
		location_name = 'Evac Location ' + str(location_index)
		num_docks = np.random.poisson(2, 1)[0] + 1
		dock_names = ''
		for dock_index in range(num_docks):
			dock_name = 'Evac dock ' + str(location_index) + str(dock_index)
			evac_docks = evac_docks.append({'Dock': dock_name,
							  'Location': location_name,
							  'Type': 'Evacuation'}, ignore_index = True)
			if dock_names == '':
				dock_names = dock_name
			else:
				dock_names = dock_names + ', ' + dock_name

		evac_locations = evac_locations.append({'Location': location_name,
							  'Docks': dock_names,
							  'Type': 'Evacuation'}, ignore_index = True)

	return(safe_locations, evac_locations, safe_docks, evac_docks)


def generate_initial_docks(safe_docks, evac_docks, num_resources):
	"""A function to generate the initial docks, some of which may be in the evac and safe docks, some may not"""
	
	# at first stack the two dock lists
	all_docks = pd.concat([safe_docks,evac_docks],ignore_index=True)
	# all_docks = safe_docks

	# now append some for initial locations that are randomly sampled
	# for dock_index in range(np.random.poisson(num_resources/2)):
	# 	dock_name = 'Initial dock ' + str(dock_index)
	# 	all_docks = all_docks.append({'Dock': dock_name,
	# 					 'Location': 'Other ' + str(dock_index),
	# 					 'Type': 'Initial'}, ignore_index = True)

	return(all_docks)


def generate_sources():
	"""A simple function to generate the source files"""
	island_source = pd.DataFrame({'Location': pd.Series([], dtype = 'str')})
	island_source = island_source.append({'Location': 'Island'}, ignore_index = True)

	return(island_source)


def generate_resource_data(number_resources, all_docks):
    """ A function to generate resource data """

    # create an empty template
    resources = pd.DataFrame({
    	'Vessel_name': pd.Series([], dtype = 'str'), # name of the vessel that is used
    	'Vessel_type': pd.Series([], dtype = 'str'), # type of the resource that is used
    	'contract_cost': pd.Series([], dtype = 'float'), # contract cost of the resource in dollar
    	'operating_cost': pd.Series([], dtype = 'float'), # the operating cost of the resource in dollars/hour
    	'Regular_origin': pd.Series([], dtype = 'str'), # the regular origin dock of the resource
    	'max_cap': pd.Series([], dtype = 'int'), # maximum capacity of resource
    	'vmax': pd.Series([], dtype = 'float'), # reaource speed when unloaded
    	'v_loaded': pd.Series([], dtype = 'float'), # resource speed when loaded
    	'loading time': pd.Series([], dtype = 'float'), # loading time of resource
    	'time to availability': pd.Series([], dtype = 'float'), # time it takes until a resource is available and crewed
    	'information': pd.Series([], dtype = 'str') # additional information
    })

    initial_dock_frame = pd.DataFrame({
    	'Dock': pd.Series([], dtype = 'str'), # dock name
		'Location': pd.Series([], dtype = 'str'), # location the dock is allocated to
		'Type': pd.Series([], dtype = 'str'), # type of dock, either 'Evaucation' or 'Safe'
		'Vessel': pd.Series([], dtype = 'str')
    	})

    # data values to select from
    vessel_types = ['ferry', 'SAR vessel', 'water taxi', 'tourist boat', 'sailing yacht', 'barge', 'power boat', 'military']
    candidates = list(all_docks['Dock'][all_docks['Type'] == 'Safe'])
    # print(candidates)

    for i in range(number_resources):
    	# print(len(initial_docks))
    	origin_index = random.randint(0,len(all_docks)-1)
    	vmax = random.randint(8,30)
    	dock_choice = random.choice(candidates)
    	resources = resources.append({'Vessel_name': 'Vessel ' + str(i + 1),
    					 'Vessel_type': random.choice(vessel_types),
    					 'contract_cost': random.randint(1,10) * 1000,
    					 'operating_cost': random.randint(1,10) * 50,
    					 'Regular_origin': dock_choice,
    					 'max_cap': np.random.poisson(30),
    					 'vmax': vmax,
    					 'v_loaded': vmax,#* 0.8,
    					 'loading time': random.randint(3,10),
    					 'time to availability': np.random.gamma(3, 15, 1)[0],
    					 'information': ''}, ignore_index = True
    					)
    	initial_dock_frame = initial_dock_frame.append({'Dock': dock_choice,
    							  'Location': all_docks['Location'][all_docks['Dock'] == dock_choice].values[0],
    							  'Type': all_docks['Type'][all_docks['Dock'] == dock_choice].values[0],
    							  'Vessel': 'Vessel ' + str(i + 1)
    							  }, ignore_index = True)

    return(resources, initial_dock_frame)


def generate_compatibility_file(all_docks, initial_docks, resources):#(safe_docks, evac_docks, initial_docks, resources):
	"""A function to generate a random compatibility file between resources and docks"""

	compat_frame = pd.DataFrame({
    	'Dock': pd.Series([], dtype = 'str'), # dock name
		'Resource': pd.Series([], dtype = 'str'), # Resource name
		'Compatibility': pd.Series([], dtype = 'int')
    	})

	# initial_docks_red = initial_docks[['Dock', 'Location', 'Type']]
	# main_docks = pd.concat([safe_docks,evac_docks], ignore_index=True)
	all_dock_names = all_docks['Dock']

	# print(all_dock_names)

	for i in all_dock_names:
		# print(i)
		for j in resources['Vessel_name']:
			if (j in initial_docks['Vessel'][initial_docks['Dock'] == i]) or (j not in compat_frame['Resource'][compat_frame['Compatibility'] == 1]):
				compat_frame = compat_frame.append({'Dock': i,
									'Resource': j,
									'Compatibility': 1}, ignore_index = True)
			else:
				compat_frame = compat_frame.append({'Dock': i,
							'Resource': j,
							'Compatibility': random.randint(0,1)}, ignore_index = True)

	# for i in np.unique(compat_frame['Resource']):
	# 	counter = 0
	# 	for j in all_docks['Dock'][all_docks['Type'] == "Evacuation"]:
	# 		# print(compat_frame['Compatibility'][(compat_frame['Dock'] == j) & (compat_frame['Resource'] == i)])
	# 		if compat_frame['Compatibility'][(compat_frame['Dock'] == j) & (compat_frame['Resource'] == i)].values == 1:
	# 			counter += 1
	# 	if counter < 1:
	# 		compat_frame['Compatibility'][(compat_frame['Resource'] == i) & (compat_frame['Dock'] == j)] = 1
	# 	counter = 0
	# 	for j in all_docks['Dock'][all_docks['Type'] == "Safe"]:
	# 		if compat_frame['Compatibility'][(compat_frame['Dock'] == j) & (compat_frame['Resource'] == i)].values == 1:
	# 			counter += 1
	# 	if counter < 1:
	# 		compat_frame['Compatibility'][(compat_frame['Resource'] == i) & (compat_frame['Dock'] == j)] = 1
						
					#### MODIFY THE ABOVE COMMENTED

	# for i in range(len(np.unique(initial_docks['Dock']))):
	# 	for j in resources['Vessel_name']:
	# 		if j == np.unique(all_docks['Vessel'])[i]:
	# 			compat_frame = compat_frame.append({'Dock': np.unique(initial_docks['Dock'])[i],
	# 								'Resource': j,
	# 								'Compatibility': 1}, ignore_index = True)
	# 		else:
	# 			compat_frame = compat_frame.append({'Dock': np.unique(initial_docks['Dock'])[i],
	# 								'Resource': j,
	# 								'Compatibility': random.randint(0,1)}, ignore_index = True)

	# for i in range(len(main_dock_names)):
	# 	for j in resources['Vessel_name']:
	# 		# print(j)
	# 		if i not in initial_docks['Dock']:
	# 			# print()
	# 		# 	if j in main_docks['Vessel'][main_docks['Dock'] == main_dock_names[i]]:
	# 		# 		compat_frame = compat_frame.append({'Dock': i,
	# 		# 							'Resource': j,
	# 		# 							'Compatibility': 1}, ignore_index = True)
	# 		# else:
	# 			compat_frame = compat_frame.append({'Dock': main_dock_names[i],
	# 								'Resource': j,
	# 								'Compatibility': random.randint(0,1)}, ignore_index = True)
	# 		# else:
	# 		# 	compat_frame = compat_frame.append({'Dock': main_dock_names[i],
	# 		# 						'Resource': j,
	# 		# 						'Compatibility': 1}, ignore_index = True)

	return(compat_frame)


def generate_scenarios(number_scenarios, evac_locations):
	"""A function to generate random scenarios"""

	scenario_frame = pd.DataFrame({
    	'Scenario': pd.Series([], dtype = 'str'), # scenario name
		'Location': pd.Series([], dtype = 'str'), # Evacuation location name
		'private_evac': pd.Series([], dtype = 'int'),
		'Demand': pd.Series([], dtype = 'int'),
		'Probability': pd.Series([], dtype = 'float')
    	})

	probabilities = [random.uniform(0, 1) for i in range(number_scenarios)]
	normed_probabilities = [x / sum(probabilities) for x in probabilities]

	for i in range(number_scenarios):
		for j in range(len(evac_locations)):
			# print(j)
			demand = int(np.floor(np.random.gamma(3, 30, 1)))# int(random.randint(0, 1500))
			private_evac = np.floor(demand * 0.1)
			scenario_frame = scenario_frame.append({'Scenario': 'Scenario ' + str(i + 1),
				                  'Location': evac_locations['Location'][j],
				                  'private_evac': private_evac,
				                  'Demand': demand,
				                  'Probability': normed_probabilities[i]}, ignore_index = True)

	return(scenario_frame)


def generate_roundtrips(largest_scenario, smallest_resource_cap):
	"""A function to generate the number of roundtrips"""

	roundtrip_frame = pd.DataFrame({
    	'Round trip': pd.Series([], dtype = 'int'), # round trip id
		'Delay cost': pd.Series([], dtype = 'float') # delay cost for gurobi implementation
    	})

	index = 1
	cost = 0
	for i in range(int(np.floor(largest_scenario/smallest_resource_cap))):
		roundtrip_frame = roundtrip_frame.append({'Round trip': index,
							   'Delay cost': cost}, ignore_index = True)
		index += 1
		cost += 0.01

	return(roundtrip_frame)


def generate_travel_distance_matrix(all_docks):
    """A function to generate a travel distance matrix"""

    # print(all_docks)

    distance_matrix = pd.DataFrame({
        'Origin': pd.Series([], dtype = 'str'),
        'Destination': pd.Series([], dtype = 'str'),
        'Distance': pd.Series([], dtype = 'float')
        })

    for i in range(len(all_docks)):
        for j in range(len(all_docks)):
            if all_docks['Location'].iloc[i] == all_docks['Location'].iloc[j]:
                distance = 0
            else:
                distance = np.random.uniform(0,40) # how to check for triangle inequality?
            distance_matrix = distance_matrix.append({'Origin': all_docks['Dock'].iloc[i], 
            										  'Destination': all_docks['Dock'].iloc[j], 
            										  'Distance': distance}, ignore_index = True)
    # print(distance_matrix)

    # test for triangular inequality
    for i in range(len(distance_matrix)):
        for k in range(len(all_docks)):
        	if distance_matrix['Origin'].iloc[i] != distance_matrix['Destination'].iloc[i]:
	            # print(distance_matrix['Origin'].iloc[i])
	            # print(distance_matrix[(distance_matrix['Origin'] == distance_matrix['Origin'].iloc[i]) & (distance_matrix['Destination'] == all_docks['Dock'].iloc[k])])
	            first_leg = distance_matrix[(distance_matrix['Origin'] == distance_matrix['Origin'].iloc[i]) & (distance_matrix['Destination'] == all_docks['Dock'].iloc[k])]
	            # print(distance_matrix[(distance_matrix['Origin'] == all_docks['Dock'].iloc[k]) & (distance_matrix['Destination'] == distance_matrix['Destination'].iloc[i])])
	            second_leg = distance_matrix[(distance_matrix['Origin'] == all_docks['Dock'].iloc[k]) & (distance_matrix['Destination'] == distance_matrix['Destination'].iloc[i])]
	            two_leg_dist = first_leg['Distance'].values + second_leg['Distance'].values
	            # two_leg_dist = distance_matrix['Distance'][(distance_matrix['Origin'] == distance_matrix['Origin'].iloc[i]) & (distance_matrix['Destination'] == all_docks['Dock'].iloc[k])] + distance_matrix['Distance'][(distance_matrix['Origin'] == all_docks['Dock'].iloc[k]) & (distance_matrix['Destination'] == distance_matrix['Destination'].iloc[i])]
	            # print(two_leg_dist)
	            if float(two_leg_dist) < float(distance_matrix['Distance'].iloc[i]):
	                # if all_docks['Location'].iloc[k] != all_docks['Location'][all_docks['Dock'] == distance_matrix['Destination'].iloc[i]]:
	                distance_matrix['Distance'].iloc[i] = two_leg_dist #+ np.random.uniform(two_leg_dist, 40)
	                i = 0 # reset and start from beginning
	                # else:
	                	# distance_matrix['Distance'].iloc[i] = distance_matrix['Distance'][(distance_matrix['Origin'] == distance_matrix['Origin'].iloc[i]) & (distance_matrix['Destination'] == all_docks['Dock'].iloc[k])] 

    return(distance_matrix)


def generate_alpha(evac_locations):
	"""A function to generate the alphas"""
	alpha = pd.DataFrame({
		'Source': pd.Series([], dtype = 'str'),
		'Island location': pd.Series([], dtype = 'str')
		})

	for i in range(len(evac_locations)):
		alpha = alpha.append({'Source': 'Island', 'Island location': evac_locations['Location'].iloc[i]}, ignore_index = True)

	return alpha


def generate_beta(evac_locations, evac_docks):
	"""A function to generate beta"""
	beta = pd.DataFrame({
		'Island location': pd.Series([], dtype = 'str'),
		'Island dock': pd.Series([], dtype = 'str')
		})

	for i in range(len(evac_locations)):
		for k in range(len(evac_docks[evac_docks['Location'] == evac_locations['Location'].iloc[i]])):
			beta = beta.append({'Island location': evac_locations['Location'].iloc[i], 'Island dock': evac_docks['Dock'][evac_docks['Location'] == evac_locations['Location'].iloc[i]].iloc[k]}, ignore_index = True)

	return beta


def generate_delta(distance_matrix, evac_docks, safe_docks):
	""" A function to generate the deltas. """
	delta = pd.DataFrame({
		'Origin': pd.Series([], dtype = 'str'),
		'Destination': pd.Series([], dtype = 'str'),
		'Distance': pd.Series([], dtype = 'float')
		})

	for i in range(len(safe_docks)):
		for j in range(len(evac_docks)):
			delta = delta.append({'Origin': safe_docks['Dock'].iloc[i], 
								  'Destination': evac_docks['Dock'].iloc[j], 
								  'Distance': distance_matrix['Distance'][(distance_matrix['Origin'] == safe_docks['Dock'].iloc[i]) & (distance_matrix['Destination'] == evac_docks['Dock'].iloc[j])].values[0]}, ignore_index = True)

	return delta


def generate_gamma(distance_matrix, evac_docks, safe_docks):
	"""A function to generate the deltas."""
	gamma = pd.DataFrame({
		'Origin': pd.Series([], dtype = 'str'),
		'Destination': pd.Series([], dtype = 'str'),
		'Distance': pd.Series([], dtype = 'float')
		})

	for i in range(len(evac_docks)):
		for j in range(len(safe_docks)):
			gamma = gamma.append({'Origin': evac_docks['Dock'].iloc[i], 
								  'Destination': safe_docks['Dock'].iloc[j], 
								  'Distance': distance_matrix['Distance'][(distance_matrix['Origin'] == evac_docks['Dock'].iloc[i]) & (distance_matrix['Destination'] == safe_docks['Dock'].iloc[j])].values[0]}, ignore_index = True)

	return gamma


def generate_epsilon(safe_docks):
	"""A function to generate the epsilons."""
	epsilons = pd.DataFrame({
		'Origin': pd.Series([], dtype = 'str'),
		'Destination': pd.Series([], dtype = 'str')
		})

	for i in range(len(safe_docks)):
		epsilons = epsilons.append({'Origin': safe_docks['Dock'].iloc[i], 'Destination': 'Mainland'}, ignore_index = True)

	return epsilons


def generate_lambda(evac_locations):
	"""A function to generate the lambdas."""
	lambdas = pd.DataFrame({
		'Origin': pd.Series([], dtype = 'str'),
		'Destination': pd.Series([], dtype = 'str')
		})

	for i in range(len(evac_locations)):
		lambdas = lambdas.append({'Origin': evac_locations['Location'].iloc[i], 'Destination': 'Mainland'}, ignore_index = True)

	return lambdas


def generate_zetas(initial_docks, evac_docks, distance_matrix):
	"""A function to generate the zetas"""
	zetas = pd.DataFrame({
		'Origin': pd.Series([], dtype = 'str'),
		'Destination': pd.Series([], dtype = 'str'),
		'Distance': pd.Series([], dtype = 'float')
		})

	unique_initial_docks = np.unique(initial_docks['Dock'])
	# print(unique_initial_docks)

	for i in range(len(unique_initial_docks)):
		for j in range(len(evac_docks)):
			zetas = zetas.append({'Origin': unique_initial_docks[i], 
								  'Destination': evac_docks['Dock'].iloc[j], 
								  'Distance': distance_matrix['Distance'][(distance_matrix['Origin'] == unique_initial_docks[i]) & (distance_matrix['Destination'] == evac_docks['Dock'].iloc[j])].values[0]}, ignore_index = True)

	return zetas


def main() -> None:

    parser = argparse.ArgumentParser(description='Read in key parameters')
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help='an integer to define the seed')
    parser.add_argument('-r','--resources', type=int, default=10,
                        help='number of resources')
    parser.add_argument('-l', '--locations', type=int, default=6,
    					help='number of locations')
    parser.add_argument('-sc', '--scenarios', type=int, default=3,
    					help='number of scenarios')
    parser.add_argument('-n', '--name', type=str, help='choose name of generated data')

    # read in from parser
    args = parser.parse_args()

    # print(args)

    seed = int(args.seed)
    number_resources = int(args.resources)
    number_locations = int(args.locations)
    number_scenarios = int(args.scenarios)
    data_name = args.name

    ####################

    # create file directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print(BASE_DIR)

    # if os.path.exists(os.path.join(BASE_DIR, 'instances')):
    # 	pass
    # else:
    # 	os.makedirs(os.path.join(BASE_DIR, 'instances'))
    DATA_DIR = os.path.join(BASE_DIR, 'core_code/instances', data_name)
    INC_DIR = os.path.join(DATA_DIR, 'Incidences')
    INPUT_DIR = os.path.join(DATA_DIR, 'Input')

    # create new folders if they do not exist
    if os.path.exists(DATA_DIR) and os.path.exists(DATA_DIR) and os.path.exists(INPUT_DIR):
    	pass
    else:
    	os.makedirs(DATA_DIR)
    	os.makedirs(INC_DIR)
    	os.makedirs(INPUT_DIR)

    # CREATE INPUT FILES

    # change working directory and set seed
    os.chdir(INPUT_DIR)
    random.seed(seed)

    # CREATE LOCATIONS AND DOCKS FILES

    island_source = generate_sources()
    # print("Island source:")
    # print(island_source)
    island_source.to_csv(os.path.join(INPUT_DIR, 'island source.csv'), index = False)

    safe_locations, evac_locations, safe_docks, evac_docks = generate_locations_and_docks_data(number_locations)
    # print("Safe locations:")
    # print(safe_locations)
    # print("Evacuation locations:")
    # print(evac_locations)
    # print("Safe docks:")
    # print(safe_docks)
    # print("Evacuation docks:")
    # print(evac_docks)
    safe_locations.to_csv(os.path.join(INPUT_DIR, 'mainland locations.csv'), index = False)
    evac_locations.to_csv(os.path.join(INPUT_DIR, 'island locations.csv'), index = False)
    safe_docks.to_csv(os.path.join(INPUT_DIR, 'mainland docks.csv'), index = False)
    evac_docks.to_csv(os.path.join(INPUT_DIR, 'island docks.csv'), index = False)

    all_docks = generate_initial_docks(safe_docks, evac_docks, number_resources)
    # print("All docks:")
    # print(all_docks)

    # CREATE VESSELS FILE

    resources, initial_docks_update = generate_resource_data(number_resources, all_docks)
    # print("Resources:")
    # print(resources)
    # print("Initial docks:")
    # print(initial_docks_update)
    resources.to_csv(os.path.join(INPUT_DIR, 'vessels.csv'), index = False)
    initial_docks_update.to_csv(os.path.join(INPUT_DIR, 'initial vessel docks.csv'), index = False)

    # CREATE VESSEL COMPATIBILITY FILE

    compat_file = generate_compatibility_file(all_docks, initial_docks_update, resources)#safe_docks, evac_docks, initial_docks_update, resources)
    # print("Compatibility file")
    # print(compat_file)
    compat_file.to_csv(os.path.join(INPUT_DIR, 'vessel compatibility.csv'), index = False)

    # CREATE SCENARIOS FILE
    
    scenarios = generate_scenarios(number_scenarios, evac_locations)
    # print("Scenarios:")
    # print(scenarios)
    scenarios.to_csv(os.path.join(INPUT_DIR, 'scenarios.csv'), index = False)

    # CREATE ROUND TRIPS FILE

    largest_scenario = 0
    for i in np.unique(scenarios['Scenario']):
        scenario_size = sum(scenarios['Demand'][scenarios['Scenario'] == i])
        if scenario_size > largest_scenario:
            largest_scenario = scenario_size

    smallest_resource_cap = min(resources['max_cap'])

    roundtrips = generate_roundtrips(largest_scenario, smallest_resource_cap)
    # print("Roundtrips:")
    # print(roundtrips)
    roundtrips.to_csv(os.path.join(INPUT_DIR, 'roundtrips.csv'), index = False)

    # CREATE INCIDENCE FILES

    # change working directory and set seed
    os.chdir(INC_DIR)

    # CREATE DISTANCE MATRIX

    distance_matrix = generate_travel_distance_matrix(all_docks)
    # print("Distance matrix")
    # print(distance_matrix)
    distance_matrix.to_csv(os.path.join(INC_DIR, 'distance matrix.csv'), index = False)

    # CREATE ALPHA

    alpha = generate_alpha(evac_locations)
    # print("alpha data:")
    # print(alpha)
    alpha.to_csv(os.path.join(INC_DIR, 'alpha.csv'), index = False)

    # CREATE BETA

    beta = generate_beta(evac_locations, evac_docks)
    # print("beta data")
    # print(beta)
    beta.to_csv(os.path.join(INC_DIR, 'beta.csv'), index = False)

    # CREATE DELTA

    delta = generate_delta(distance_matrix, evac_docks, safe_docks)
    # print("delta data")
    # print(delta)
    delta.to_csv(os.path.join(INC_DIR, 'delta.csv'), index = False)

    # CREATE EPSILON

    epsilon = generate_epsilon(safe_docks)
    # print("epsilon:")
    # print(epsilon)
    epsilon.to_csv(os.path.join(INC_DIR, 'epsilon.csv'), index = False)

    # CREATE GAMMA

    gamma = generate_gamma(distance_matrix, evac_docks, safe_docks)
    # print("gamma data:")
    # print(gamma)
    gamma.to_csv(os.path.join(INC_DIR, 'gamma.csv'), index = False)

    # CREATE LAMBDA

    lambdas = generate_lambda(evac_locations)
    # print("lambda data:")
    # print(lambdas)
    lambdas.to_csv(os.path.join(INC_DIR, 'lambda.csv'), index = False)

    # CREATE ZETA

    zeta = generate_zetas(initial_docks_update, evac_docks, distance_matrix)
    # print("zeta data:")
    # print(zeta)
    zeta.to_csv(os.path.join(INC_DIR, 'zeta.csv'), index = False)


if __name__ == "__main__":
    main()