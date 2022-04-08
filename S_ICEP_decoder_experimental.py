###############################################################################
"""
@fiete
November 12, 2020
"""
###############################################################################

# import packages
import pandas as pd 
import numpy as np  
import itertools
import time
from multiprocessing import Process

# import modules
from brkga_mp_ipr.types import BaseChromosome
from S_ICEP_instance import SICEPInstance
from location import Location
from evacLocation import EvacLocation
from dock import Dock
from evacRes import EvacRes
from generate_outputs import generate_results_table

class SICEPDecoder():
    """
    S-ICEP decoder. It creates a permutation of
    nodes induced by the chromosome and computes the cost of the tour.
    """

    def __init__(self, instance: SICEPInstance):

        self.instance = instance        
        self.objective_values_record = []

    ###########################################################################

    def sequence_checker(self, sequence, key):
        """
        An auxiliary function to test in which position range of a sequence a key falls
        """
        # position = 0
        # for i in range(1, len(sequence)):
        #     if key >= sequence[i]:
        #         position += 1
        # return position
        return(np.where((sequence - key) > 0, (sequence - key), np.inf).argmin() - 1)


    def route_assign_scenario(self, instance, chromosome, scenario_objectives, probability_scenario_objectives):
        """
        An auxiliary function that calculates the route allocation for a specific scenario
        """

        for scenario in range(len(chromosome)):
            # print("#########################")
            # print("Scenario:", scenario + 1)
            # split the chromosome into segments for each resource
            resource_split = np.array_split(chromosome, instance.num_resources)

            # perform further splits for each resource
            for resource in range(len(resource_split)): 
                # print("-------------------------")
                # print("Resource:", resource + 1)

                # assign the route for each resource segment
                for index in range(len(resource_split[resource])):

                    # assing nodes tour
                    print("Key value:", resource_split[resource][index])
                    print("boundaries:", instance.dock_boundaries[resource])
                    choose_dock_number = self.sequence_checker(instance.dock_boundaries[resource], resource_split[resource][index])

                    if choose_dock_number == 0:
                        # if pick-up number is 0, don't do anything
                        # print("Keep resource", self.instance.resources[scenario][resource].name, "where it is.")
                        pass

                    elif instance.resources[scenario][resource].current_dock.name == instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name:
                        # print("same dock")
                        pass

                    # THIS CHECK IS WAYYY TO EXPENSIVE COMPUTATIONALLY, FIND A BETTER WAY OR PENALIZE VIOLATION
                    # elif self.instance.resources[scenario][resource].current_route_time + (self.instance.resources[scenario][resource].loading_time + (self.instance.resources[scenario][resource].current_dock.distances['Distance'][self.instance.resources[scenario][resource].current_dock.distances['Destination'] == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name]/self.instance.resources[scenario][resource].vmax * 60)).values[0] >= self.instance.upper_time_limit:
                    #     # print("Adding this stop would violate the upper time limit")
                    #     pass

                    else:
                        if instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Evacuation':
                            # print("Send resource", self.instance.resources[scenario][resource].name, 
                            #     "from", self.instance.resources[scenario][resource].current_dock.name, 
                            #     "to pick-up node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
                            # append leg to resource route
                            # print(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
                            instance.resources[scenario][resource].route.append(instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
                            # print(self.instance.resources[scenario][resource].route)
                            # self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
                            # load passengers
                            # related_island_location = next((x for x in self.instance.island_locations[scenario] if (x.name == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].location)), None)
                            # print("Location that this relates to:", related_island_location.name)
                            # print("This area currently has:", related_island_location.current_evacuees, "evacuees")
                            # if related_island_location.current_evacuees > (self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers):#self.instance.resources[scenario][resource].max_cap:
                            #     load = self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers
                            #     self.instance.resources[scenario][resource].current_passengers = self.instance.resources[scenario][resource].current_passengers + load
                            #     related_island_location.current_evacuees = related_island_location.current_evacuees - load
                            # else:
                            #     load = int(related_island_location.current_evacuees)
                            #     self.instance.resources[scenario][resource].current_passengers += load
                            #     related_island_location.current_evacuees = 0
                            # update current dock of resource
                            instance.resources[scenario][resource].current_dock = instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1]
                            # print(load, "evacuees loaded") 

                        elif instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Safe':
                            # print("Send resource", self.instance.resources[scenario][resource].name, 
                            #     "from", self.instance.resources[scenario][resource].current_dock.name, 
                            #     "to drop-off node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
                            # append leg to resource route
                            # print(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
                            instance.resources[scenario][resource].route.append(instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
                            # print(self.instance.resources[scenario][resource].route)
                            # self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
                            # unload passengers
                            # unload = self.instance.resources[scenario][resource].current_passengers
                            # self.instance.resources[scenario][resource].current_passengers = 0
                            # update current dock of resource
                            instance.resources[scenario][resource].current_dock = instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1]
                            # print(unload, "evacuees unloaded")

                # update the route time of the resource
                instance.resources[scenario][resource].update_route_time(instance.island_docks[scenario], instance.mainland_docks[scenario])
                # print("Current route time:", self.instance.resources[scenario][resource].current_route_time)

            # allocate passengers

            # create a list of all visits that are part of the generated route plan for the given scenario
            all_visits = []
            for location in instance.locations[scenario]:
                # print("Location", location.name, location)
                # find all related docks and append every one of their visits to the data all visits data frame
                for dock in location.dock_objects:
                    # print("Dock name", dock.name)
                    all_visits.extend(dock.resource_visits)

            # sort the list in sequence of arrivals
            all_visits.sort(key=lambda a: a[0])
            # for each visit, allocate passengers until no evacuees are left at each location
            for visit in all_visits:
                # print(visit)
                # allocate the load based on how much space is available on the resource
                location = next((x for x in instance.locations[scenario] if (x.name == visit[4])), None)
                # print("Vessel", visit[2].name, "is visiting", location.name)
                if location.type == 'Evacuation':
                    # print("Current passengers on ", visit[2].name, ":", visit[2].current_passengers) 
                    # print("Current evacuees at", location.name, ":", location.current_evacuees)
                    if location.current_evacuees > (visit[2].max_cap - visit[2].current_passengers):#self.instance.resources[scenario][resource].max_cap:
                        load = visit[2].max_cap - visit[2].current_passengers
                        visit[2].current_passengers = visit[2].current_passengers + load
                        location.current_evacuees = location.current_evacuees - load
                    else:
                        load = int(location.current_evacuees)
                        visit[2].current_passengers += load
                        location.current_evacuees = location.current_evacuees - load
                    # print(visit[2].name, "is loading", load, "passengers")
                    # print("Remaining evacuees at: ", location.name, ":", location, ":", location.current_evacuees)
                    # update the passenger route on the resource
                    visit[2].passengers_route.append(visit[2].current_passengers)
                    
                else:
                    unload = visit[2].current_passengers
                    visit[2].current_passengers = 0
                    # update the passenger route on the resource
                    visit[2].passengers_route.append(visit[2].current_passengers) 
                # print(visit[2].passengers_route)

            # for i in self.instance.resources[scenario]:
            #     print(i.name, ":", i.passengers_route)

            # remove all route legs after the last trip
            for resource in range(len(instance.resources[scenario])):
                # print("Resource:", self.instance.resources[scenario][resource].name)
                if len(instance.resources[scenario][resource].passengers_route) > 0:
                    counter = len(instance.resources[scenario][resource].passengers_route) - 1
                    while instance.resources[scenario][resource].passengers_route[counter] == 0 and counter != 0:
                        # print(self.instance.resources[scenario][resource].passengers_route[0:counter])
                        counter -= 1
                    if counter != 0:
                        instance.resources[scenario][resource].passengers_route = instance.resources[scenario][resource].passengers_route[:counter+1]
                        instance.resources[scenario][resource].route = instance.resources[scenario][resource].route[:counter+2]
                    else:
                        instance.resources[scenario][resource].passengers_route = []
                        instance.resources[scenario][resource].route = []
                    # print('passenger route:', self.instance.resources[scenario][resource].passengers_route)
                    # print('route:', resource.route)
                # update the route time of the resource
                instance.resources[scenario][resource].update_route_time_no_visit_add(instance.island_docks[scenario], instance.mainland_docks[scenario])
                # print("Current route time:", self.instance.resources[scenario][resource].current_route_time)

            # for i in self.instance.resources[scenario]:
            #     print(i.name, ":", i.passengers_route)

            # calculate the scenario metrics
            # calculate max route time and variable cost
            scenario_max_route_time = 0.0
            scenario_variable_cost = 0.0
            for i in instance.resources[scenario]: 
                # i.update_route_time(island_docks, mainland_docks)
                scenario_variable_cost += i.current_operating_cost # update the operating cost
                if (i.current_route_time > scenario_max_route_time) and (i.current_number_movements > 0): # only count resources that are actually used
                    scenario_max_route_time = i.current_route_time
            # print('Max route time:', scenario_max_route_time)

            # calculate the number of remaining evacuees
            scenario_remaining_evacuees = 0
            for i in instance.locations[scenario]:
                if i.type == "Evacuation":
                    scenario_remaining_evacuees += i.current_evacuees
                    # print(i.name, ':', i, ":", i.current_evacuees)

            # generate the final route plan
            # route_details = generate_results_table(self.instance.resources[scenario]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY

            # calculate the cost multiplied by the probability and penalized by the non-dominant term
            scenario_objective_value = scenario_max_route_time + (1/instance.objective_discriminator) * scenario_variable_cost + scenario_remaining_evacuees * self.instance.penalty
            # append to all recording lists
            scenario_objectives.append(scenario_objective_value)
            probability_scenario_objectives.append(self.instance.scenario_probabilities[scenario] * scenario_objective_value)
            # self.route_detail_frame.append(route_details)
            # print(route_details.loc[0:40,:]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY
            # print("Scenario objective value:", scenario_objective_value)

        return instance, scenario_objectives, probability_scenario_objectives



    def decode(self, chromosome: BaseChromosome, rewrite: bool) -> float:
        """
        Given a chromossome, build a routing plan.
        Note that in this example, ``rewrite`` has not been used.
        """

        # TO DO:
        # - implement free link instead of distinguishing between dock types # DONE
        # - implement to only sample from compatible docks # DONE
        # - implement to allocate passenger allocation later based on time not on vessel list order, when routing is completed. # DONE
        # - implement the discarsion of all elements of the route that do not have passengers anymore # DONE
        # - find a way to incorporate upper time limit efficiently
        # - CLEAN UP ALL FILES

        start_time = time.time()

        # at first reset the problem to the initial situation
        self.instance.return_to_initial_settings()

        # a list to hold scenario objective values
        self.scenario_objectives = []
        self.probability_scenario_objectives = []
        self.route_detail_frame = []

        # split the chromosome into segments for each scenario
        scenario_split_chromosome = np.array_split(chromosome, self.instance.num_scenarios)

        # perform actions for each scenario

        my_process = Process(target=self.route_assign_scenario, args=(self.instance, scenario_split_chromosome, self.scenario_objectives, self.probability_scenario_objectives))
        my_process.start()
        my_process.join()
        print('Done')

            # self.instance, self.scenario_objectives, self.probability_scenario_objectives = self.route_assign_scenario(self.instance, scenario_split_chromosome[scenario], self.scenario_objectives, self.probability_scenario_objectives)

            # # split the chromosome into segments for each resource
            # resource_split = np.array_split(scenario_split_chromosome[scenario], self.instance.num_resources)

            # # perform further splits for each resource
            # for resource in range(len(resource_split)): 
            #     # print("-------------------------")
            #     # print("Resource:", resource + 1)

            #     # assign the route for each resource segment
            #     for index in range(len(resource_split[resource])):

            #         # assing nodes tour
            #         # print("Key value:", resource_split[resource][index])
            #         choose_dock_number = self.sequence_checker(self.instance.dock_boundaries[resource], resource_split[resource][index])

            #         if choose_dock_number == 0:
            #             # if pick-up number is 0, don't do anything
            #             # print("Keep resource", self.instance.resources[scenario][resource].name, "where it is.")
            #             pass

            #         elif self.instance.resources[scenario][resource].current_dock.name == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name:
            #             # print("same dock")
            #             pass

            #         # THIS CHECK IS WAYYY TO EXPENSIVE COMPUTATIONALLY, FIND A BETTER WAY OR PENALIZE VIOLATION
            #         # elif self.instance.resources[scenario][resource].current_route_time + (self.instance.resources[scenario][resource].loading_time + (self.instance.resources[scenario][resource].current_dock.distances['Distance'][self.instance.resources[scenario][resource].current_dock.distances['Destination'] == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name]/self.instance.resources[scenario][resource].vmax * 60)).values[0] >= self.instance.upper_time_limit:
            #         #     # print("Adding this stop would violate the upper time limit")
            #         #     pass

            #         else:
            #             if self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Evacuation':
            #                 # print("Send resource", self.instance.resources[scenario][resource].name, 
            #                 #     "from", self.instance.resources[scenario][resource].current_dock.name, 
            #                 #     "to pick-up node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
            #                 # append leg to resource route
            #                 # print(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
            #                 self.instance.resources[scenario][resource].route.append(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
            #                 # print(self.instance.resources[scenario][resource].route)
            #                 # self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
            #                 # load passengers
            #                 # related_island_location = next((x for x in self.instance.island_locations[scenario] if (x.name == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].location)), None)
            #                 # print("Location that this relates to:", related_island_location.name)
            #                 # print("This area currently has:", related_island_location.current_evacuees, "evacuees")
            #                 # if related_island_location.current_evacuees > (self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers):#self.instance.resources[scenario][resource].max_cap:
            #                 #     load = self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers
            #                 #     self.instance.resources[scenario][resource].current_passengers = self.instance.resources[scenario][resource].current_passengers + load
            #                 #     related_island_location.current_evacuees = related_island_location.current_evacuees - load
            #                 # else:
            #                 #     load = int(related_island_location.current_evacuees)
            #                 #     self.instance.resources[scenario][resource].current_passengers += load
            #                 #     related_island_location.current_evacuees = 0
            #                 # update current dock of resource
            #                 self.instance.resources[scenario][resource].current_dock = self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1]
            #                 # print(load, "evacuees loaded") 

            #             elif self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Safe':
            #                 # print("Send resource", self.instance.resources[scenario][resource].name, 
            #                 #     "from", self.instance.resources[scenario][resource].current_dock.name, 
            #                 #     "to drop-off node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
            #                 # append leg to resource route
            #                 # print(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
            #                 self.instance.resources[scenario][resource].route.append(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
            #                 # print(self.instance.resources[scenario][resource].route)
            #                 # self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
            #                 # unload passengers
            #                 # unload = self.instance.resources[scenario][resource].current_passengers
            #                 # self.instance.resources[scenario][resource].current_passengers = 0
            #                 # update current dock of resource
            #                 self.instance.resources[scenario][resource].current_dock = self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1]
            #                 # print(unload, "evacuees unloaded")

            #     # update the route time of the resource
            #     self.instance.resources[scenario][resource].update_route_time(self.instance.island_docks[scenario], self.instance.mainland_docks[scenario])
            #     # print("Current route time:", self.instance.resources[scenario][resource].current_route_time)

            # # allocate passengers

            # # create a list of all visits that are part of the generated route plan for the given scenario
            # all_visits = []
            # for location in self.instance.locations[scenario]:
            #     # print("Location", location.name, location)
            #     # find all related docks and append every one of their visits to the data all visits data frame
            #     for dock in location.dock_objects:
            #         # print("Dock name", dock.name)
            #         all_visits.extend(dock.resource_visits)

            # # sort the list in sequence of arrivals
            # all_visits.sort(key=lambda a: a[0])
            # # for each visit, allocate passengers until no evacuees are left at each location
            # for visit in all_visits:
            #     # print(visit)
            #     # allocate the load based on how much space is available on the resource
            #     location = next((x for x in self.instance.locations[scenario] if (x.name == visit[4])), None)
            #     # print("Vessel", visit[2].name, "is visiting", location.name)
            #     if location.type == 'Evacuation':
            #         # print("Current passengers on ", visit[2].name, ":", visit[2].current_passengers) 
            #         # print("Current evacuees at", location.name, ":", location.current_evacuees)
            #         if location.current_evacuees > (visit[2].max_cap - visit[2].current_passengers):#self.instance.resources[scenario][resource].max_cap:
            #             load = visit[2].max_cap - visit[2].current_passengers
            #             visit[2].current_passengers = visit[2].current_passengers + load
            #             location.current_evacuees = location.current_evacuees - load
            #         else:
            #             load = int(location.current_evacuees)
            #             visit[2].current_passengers += load
            #             location.current_evacuees = location.current_evacuees - load
            #         # print(visit[2].name, "is loading", load, "passengers")
            #         # print("Remaining evacuees at: ", location.name, ":", location, ":", location.current_evacuees)
            #         # update the passenger route on the resource
            #         visit[2].passengers_route.append(visit[2].current_passengers)
                    
            #     else:
            #         unload = visit[2].current_passengers
            #         visit[2].current_passengers = 0
            #         # update the passenger route on the resource
            #         visit[2].passengers_route.append(visit[2].current_passengers) 
            #     # print(visit[2].passengers_route)

            # # for i in self.instance.resources[scenario]:
            # #     print(i.name, ":", i.passengers_route)

            # # remove all route legs after the last trip
            # for resource in range(len(self.instance.resources[scenario])):
            #     # print("Resource:", self.instance.resources[scenario][resource].name)
            #     if len(self.instance.resources[scenario][resource].passengers_route) > 0:
            #         counter = len(self.instance.resources[scenario][resource].passengers_route) - 1
            #         while self.instance.resources[scenario][resource].passengers_route[counter] == 0 and counter != 0:
            #             # print(self.instance.resources[scenario][resource].passengers_route[0:counter])
            #             counter -= 1
            #         if counter != 0:
            #             self.instance.resources[scenario][resource].passengers_route = self.instance.resources[scenario][resource].passengers_route[:counter+1]
            #             self.instance.resources[scenario][resource].route = self.instance.resources[scenario][resource].route[:counter+2]
            #         else:
            #             self.instance.resources[scenario][resource].passengers_route = []
            #             self.instance.resources[scenario][resource].route = []
            #         # print('passenger route:', self.instance.resources[scenario][resource].passengers_route)
            #         # print('route:', resource.route)
            #     # update the route time of the resource
            #     self.instance.resources[scenario][resource].update_route_time_no_visit_add(self.instance.island_docks[scenario], self.instance.mainland_docks[scenario])
            #     # print("Current route time:", self.instance.resources[scenario][resource].current_route_time)

            # # for i in self.instance.resources[scenario]:
            # #     print(i.name, ":", i.passengers_route)

            # # calculate the scenario metrics
            # # calculate max route time and variable cost
            # scenario_max_route_time = 0.0
            # scenario_variable_cost = 0.0
            # for i in self.instance.resources[scenario]: 
            #     # i.update_route_time(island_docks, mainland_docks)
            #     scenario_variable_cost += i.current_operating_cost # update the operating cost
            #     if (i.current_route_time > scenario_max_route_time) and (i.current_number_movements > 0): # only count resources that are actually used
            #         scenario_max_route_time = i.current_route_time
            # # print('Max route time:', scenario_max_route_time)

            # # calculate the number of remaining evacuees
            # scenario_remaining_evacuees = 0
            # for i in self.instance.locations[scenario]:
            #     if i.type == "Evacuation":
            #         scenario_remaining_evacuees += i.current_evacuees
            #         # print(i.name, ':', i, ":", i.current_evacuees)

            # # generate the final route plan
            # # route_details = generate_results_table(self.instance.resources[scenario]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY

            # # calculate the cost multiplied by the probability and penalized by the non-dominant term
            # scenario_objective_value = scenario_max_route_time + (1/self.instance.objective_discriminator) * scenario_variable_cost + scenario_remaining_evacuees * self.instance.penalty
            # # append to all recording lists
            # self.scenario_objectives.append(scenario_objective_value)
            # self.probability_scenario_objectives.append(self.instance.scenario_probabilities[scenario] * scenario_objective_value)
            # # self.route_detail_frame.append(route_details)
            # # print(route_details.loc[0:40,:]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY
            # # print("Scenario objective value:", scenario_objective_value)

        # calculate the fixed cost parameter
        total_contract_cost = 0.0
        check_list = [0 for i in range(len(self.instance.resource_names))] # create a check list to make sure that resources aren't counted multiple times
        # print("Checklist:", check_list)
        for scenario in range(len(self.instance.scenario_names)):
            # print("Found in Scenario:", scenario)
            for resource_index in range(len(self.instance.resources[scenario])):
                if (self.instance.resources[scenario][resource_index].current_route_time != self.instance.resources[scenario][resource_index].time_to_availability) and (check_list[resource_index] == 0):
                    # print("Resource:", self.instance.resources[scenario][resource_index].name)
                    # print("Cost added:", self.instance.resources[scenario][resource_index].contract_cost)
                    total_contract_cost += self.instance.resources[scenario][resource_index].contract_cost # add to the total contract cost
                    # print("New contract cost:", total_contract_cost)
                    check_list[resource_index] = 1 # mark that the resource contract cost has been counted
                    # print(check_list)
        # print("Checklist after:", check_list)
        # print(self.route_detail_frame)

        # calculate the total cost and append to record
        cost = float((1/self.instance.objective_discriminator) * total_contract_cost + sum(self.probability_scenario_objectives))
        self.objective_values_record.append(cost) # append the evolution of objective values
        # print('Total objective value', cost)

        # print('---------------------')

        end_time = time.time()
        total_time = end_time - start_time

        print('Time of iteration:', total_time)

        return cost


    # def decode(self, chromosome: BaseChromosome, rewrite: bool) -> float:
    #     """
    #     Given a chromossome, build a routing plan.
    #     Note that in this example, ``rewrite`` has not been used.
    #     """

    #     # TO DO:
    #     # - implement free link instead of distinguishing between dock types # DONE
    #     # - implement to only sample from compatible docks # DONE
    #     # - implement to allocate passenger allocation later based on time not on vessel list order, when routing is completed. 
    #     # - find a way to incorporate upper time limit efficiently
    #     # - CLEAN UP ALL FILES

    #     # at first reset the problem to the initial situation
    #     self.instance.return_to_initial_settings()

    #     # a list to hold scenario objective values
    #     self.scenario_objectives = []
    #     self.probability_scenario_objectives = []
    #     self.route_detail_frame = []

    #     # split the chromosome into segments for each scenario
    #     scenario_split_chromosome = np.array_split(chromosome, self.instance.num_scenarios)

    #     # perform actions for each scenario
    #     for scenario in range(len(scenario_split_chromosome)):
    #         # print("#########################")
    #         # print("Scenario:", scenario + 1)

    #         # split the chromosome into segments for each resource
    #         resource_split = np.array_split(scenario_split_chromosome[scenario], self.instance.num_resources)

    #         # perform further splits for each resource
    #         for resource in range(len(resource_split)): 
    #             # print("-------------------------")
    #             # print("Resource:", resource + 1)

    #             # assign the route for each resource segment
    #             for index in range(len(resource_split[resource])):

    #                 # assing nodes tour
    #                 # print("Key value:", resource_split[resource][index])
    #                 choose_dock_number = self.sequence_checker(self.instance.dock_boundaries[resource], resource_split[resource][index])

    #                 if choose_dock_number == 0:
    #                     # if pick-up number is 0, don't do anything
    #                     # print("Keep resource", self.instance.resources[scenario][resource].name, "where it is.")
    #                     pass

    #                 elif self.instance.resources[scenario][resource].current_dock.name == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name:
    #                     # print("same dock")
    #                     pass

    #                 # THIS CHECK IS WAYYY TO EXPENSIVE COMPUTATIONALLY, FIND A BETTER WAY OR PENALIZE VIOLATION
    #                 # elif self.instance.resources[scenario][resource].current_route_time + (self.instance.resources[scenario][resource].loading_time + (self.instance.resources[scenario][resource].current_dock.distances['Distance'][self.instance.resources[scenario][resource].current_dock.distances['Destination'] == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name]/self.instance.resources[scenario][resource].vmax * 60)).values[0] >= self.instance.upper_time_limit:
    #                 #     # print("Adding this stop would violate the upper time limit")
    #                 #     pass

    #                 else:
    #                     if self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Evacuation':
    #                         # print("Send resource", self.instance.resources[scenario][resource].name, 
    #                         #     "from", self.instance.resources[scenario][resource].current_dock.name, 
    #                         #     "to pick-up node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
    #                         # append leg to resource route
    #                         self.instance.resources[scenario][resource].route.append(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
    #                         self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
    #                         # load passengers
    #                         related_island_location = next((x for x in self.instance.island_locations[scenario] if (x.name == self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].location)), None)
    #                         # print("Location that this relates to:", related_island_location.name)
    #                         # print("This area currently has:", related_island_location.current_evacuees, "evacuees")
    #                         if related_island_location.current_evacuees > (self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers):#self.instance.resources[scenario][resource].max_cap:
    #                             load = self.instance.resources[scenario][resource].max_cap - self.instance.resources[scenario][resource].current_passengers
    #                             self.instance.resources[scenario][resource].current_passengers = self.instance.resources[scenario][resource].current_passengers + load
    #                             related_island_location.current_evacuees = related_island_location.current_evacuees - load
    #                         else:
    #                             load = int(related_island_location.current_evacuees)
    #                             self.instance.resources[scenario][resource].current_passengers += load
    #                             related_island_location.current_evacuees = 0
    #                         # update current dock of resource
    #                         self.instance.resources[scenario][resource].current_dock = self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1] 
    #                         # print(load, "evacuees loaded") 

    #                     elif self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].type == 'Safe':
    #                         # print("Send resource", self.instance.resources[scenario][resource].name, 
    #                         #     "from", self.instance.resources[scenario][resource].current_dock.name, 
    #                         #     "to drop-off node", self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1].name)
    #                         # append leg to resource route
    #                         self.instance.resources[scenario][resource].route.append(self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1])
    #                         self.instance.resources[scenario][resource].passengers_route.append(self.instance.resources[scenario][resource].current_passengers) 
    #                         # unload passengers
    #                         unload = self.instance.resources[scenario][resource].current_passengers
    #                         self.instance.resources[scenario][resource].current_passengers = 0
    #                         # update current dock of resource
    #                         self.instance.resources[scenario][resource].current_dock = self.instance.dock_compat_cluster[scenario][resource][choose_dock_number - 1]
    #                         # print(unload, "evacuees unloaded")

    #             # update the route time of the resource
    #             self.instance.resources[scenario][resource].update_route_time(self.instance.island_docks[scenario], self.instance.mainland_docks[scenario])
    #             # print("Current route time:", self.instance.resources[scenario][resource].current_route_time)

    #         # calculate the scenario metrics
    #         # calculate max route time and variable cost
    #         scenario_max_route_time = 0.0
    #         scenario_variable_cost = 0.0
    #         for i in self.instance.resources[scenario]: 
    #             # i.update_route_time(island_docks, mainland_docks)
    #             scenario_variable_cost += i.current_operating_cost # update the operating cost
    #             if (i.current_route_time > scenario_max_route_time) and (i.current_number_movements > 0): # only count resources that are actually used
    #                 scenario_max_route_time = i.current_route_time
    #         #     print('Max route time:', max_route_time)

    #         # calculate the number of remaining evacuees
    #         scenario_remaining_evacuees = 0
    #         for i in self.instance.island_locations[scenario]:
    #             scenario_remaining_evacuees += i.current_evacuees

    #         # generate the final route plan
    #         # route_details = generate_results_table(self.instance.resources[scenario]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY

    #         # calculate the cost multiplied by the probability and penalized by the non-dominant term
    #         scenario_objective_value = scenario_max_route_time + (1/self.instance.objective_discriminator) * scenario_variable_cost + scenario_remaining_evacuees * self.instance.penalty
    #         # append to all recording lists
    #         self.scenario_objectives.append(scenario_objective_value)
    #         self.probability_scenario_objectives.append(self.instance.scenario_probabilities[scenario] * scenario_objective_value)
    #         # self.route_detail_frame.append(route_details)
    #         # print(route_details.loc[0:40,:]) # DO NOT RUN THIS REGULARLY IT IS INEFFICIENT AND FOR INSPECTION ONLY
    #         # print("Scenario objective value:", scenario_objective_value)

    #     # calculate the fixed cost parameter
    #     total_contract_cost = 0.0
    #     check_list = [0 for i in range(len(self.instance.resource_names))] # create a check list to make sure that resources aren't counted multiple times
    #     # print("Checklist:", check_list)
    #     for scenario in range(len(self.instance.scenario_names)):
    #         # print("Found in Scenario:", scenario)
    #         for resource_index in range(len(self.instance.resources[scenario])):
    #             if (self.instance.resources[scenario][resource_index].current_route_time != self.instance.resources[scenario][resource_index].time_to_availability) and (check_list[resource_index] == 0):
    #                 # print("Resource:", self.instance.resources[scenario][resource_index].name)
    #                 # print("Cost added:", self.instance.resources[scenario][resource_index].contract_cost)
    #                 total_contract_cost += self.instance.resources[scenario][resource_index].contract_cost # add to the total contract cost
    #                 # print("New contract cost:", total_contract_cost)
    #                 check_list[resource_index] = 1 # mark that the resource contract cost has been counted
    #                 # print(check_list)
    #     # print("Checklist after:", check_list)
    #     # print(self.route_detail_frame)

    #     # calculate the total cost and append to record
    #     cost = float((1/self.instance.objective_discriminator) * total_contract_cost + sum(self.probability_scenario_objectives))
    #     self.objective_values_record.append(cost) # append the evolution of objective values
    #     # print('Total objective value', cost)

    #     # print('---------------------')

    #     return cost#, self.route_detail_frame


    def return_objective_evolution(self):
        """
        Return the list of objective values
        """
        return self.objective_values_record




