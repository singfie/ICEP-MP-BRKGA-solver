"""
@fiete
November 12, 2020
"""

# import packages
import pandas as pd

class Location:
    """
    A class defining a location.
    This is a type of node in the network.
    """
    
    def __init__(self, loc_data):
        """
        Initializes a location and its data. The type determines whether this location is connected to the 
        source or the sink node and thus the direction of the flows through this node
        """
        
        # fixed parameters
        self.name = loc_data.loc['Location'] # name of the location
        self.type = loc_data.loc['Type'] # whether this is a safe or evacuation location
        self.docks = [i for i in loc_data.loc['Docks'].split(", ")] # list of all adjacent docks
        
        # flexible parameters
        self.inflows = 0 # do we need this?
        self.outflows = 0 # do we need this?

        self.dock_objects = []

    def add_docks(self, dock_list):

        for i in dock_list:
            if i.name in self.docks:
                self.dock_objects.append(i)

        pass # return nothing