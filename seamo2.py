'''Main module which contains the SEAMO2,
the genetic operators crossover and mutation,
and some auxiliary functions and procedures'''

import initial_population_generator as ipg
import parser
from random import choice, getrandbits, randrange, random
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Class to run the SEAMO2
class SEAMO2:
    def __init__(self, instance):
        instances = ["Mandl", "Mumford0", "Mumford1", "Mumford2", "Mumford3"]
        print(f"Available benchmarking instances to use: {instances}")
        self.file_name = input("Type one of them exactly as it's written: ")
        self.transport_network = parser.TransportNetwork(self.file_name + "TravelTimes.txt")
        self.coords = parser.CoordsParser(self.file_name + "Coords.txt")
        self.demand_matrix = parser.DemandMatrixParser(self.file_name + "Demand.txt")
        self.initial_population_generator = ipg.InitialPopulationGenerator(self.transport_network)

    # Method to check routeset's connectivity
    def check_connectivity(self, routeset):
        routeset_is_connected = True
        for i in range(len(self.transport_network.graph)):
            for j in range(len(self.transport_network.graph)):
                shortest_path_travel_time = self.get_shortest_path_travel_time(routeset, i, j)
                if shortest_path_travel_time == 0:
                    routeset_is_connected = False
        
        return routeset_is_connected

    # Method to get the routeset's transfer points
    def get_transfer_points(self, routeset):

        '''A dictionary is created to store
        the number of times an access point has been used'''
        touched_points_n_times = {}
        transfer_points = set()
        for route in routeset:
            for access_point_id in route:
                if access_point_id not in touched_points_n_times.keys():
                    touched_points_n_times[access_point_id] = 1
                else:
                    touched_points_n_times[access_point_id] += 1
        
        # The transfer points are those which have been used more than once
        for access_point_id in touched_points_n_times.keys():
            if touched_points_n_times[access_point_id] > 1:
                transfer_points.add(access_point_id)
        
        return transfer_points

    # Method to compute a given path's travel time
    def compute_path_travel_time(self, path):

        # The links within the path are generated 
        path_links = list(zip(path, path[1:]))
        path_travel_time = 0

        # Checks the travel time of each link and sums it
        for path_link in path_links:
            origin_access_point = self.transport_network.graph[path_link[0]]
            destination_access_point = path_link[1]
            for access_point_link in origin_access_point.links:
                if access_point_link.destination.id == destination_access_point:
                    path_travel_time += access_point_link.travel_time
        
        return path_travel_time

    # Method to find the second half of a path from a transfer point
    def find_second_path(
        self,
        destination_id,
        chosen_transfer_point,
        chosen_second_route
        ):

        # Gets the chosen transfer point's and destination's indexes in the chosen route
        chosen_transfer_point_index_second_route = chosen_second_route.index(
            chosen_transfer_point
        )
        destination_id_index_second_route = chosen_second_route.index(
            destination_id
        )

        # Makes a slice of the route using those indexes
        if destination_id_index_second_route > chosen_transfer_point_index_second_route:
            second_path = chosen_second_route[
                chosen_transfer_point_index_second_route:destination_id_index_second_route + 1
                ]
        elif destination_id_index_second_route < chosen_transfer_point_index_second_route:
            second_path = chosen_second_route[
                destination_id_index_second_route:chosen_transfer_point_index_second_route + 1
                ]
            second_path = list(second_path)
            second_path.reverse()
            second_path = tuple(second_path)

        return second_path

    # Method to get the path's travel time with only one transfer
    def get_one_transfer_path_travel_time(
        self,
        origin_destination_transfer_points_aux,
        route,
        destination_id,
        origin_id_index,
        routes_with_destination,
        routes_with_destination_aux,
        shortest_path_travel_time
        ):

        '''A copy of the list of routes that contain the destination
        is needed to test all the possibilities'''
        if route in routes_with_destination_aux:
            routes_with_destination_aux.remove(route)
        
        # Also a copy of the direct transfer points from origin to destination
        origin_destination_transfer_points_aux = list(origin_destination_transfer_points_aux)

        # Tests for each direct transfer points from origin to destination
        while len(origin_destination_transfer_points_aux) != 0:
            chosen_transfer_point = choice(origin_destination_transfer_points_aux)
            origin_destination_transfer_points_aux.remove(chosen_transfer_point)
            if chosen_transfer_point not in route:
                continue

            # If the chosen transfer point is in the route, gets its index
            chosen_transfer_point_index = route.index(chosen_transfer_point)
            if origin_id_index < chosen_transfer_point_index:

                # Tests it for each route containing the destination
                while len(routes_with_destination_aux) != 0:
                    chosen_second_route = choice(routes_with_destination_aux)
                    routes_with_destination_aux.remove(chosen_second_route)
                    if chosen_transfer_point not in chosen_second_route:
                        continue

                    '''If both the origin and chosen transfer point
                    are in the chosen route, makes the first slice of the path'''
                    path = route[origin_id_index:chosen_transfer_point_index + 1]

                    # Searchs for the second slice of the path
                    second_path = self.find_second_path(
                        destination_id,
                        chosen_transfer_point,
                        chosen_second_route
                    )

                    '''Concatenates both slices,
                    calculates the path travel time and
                    compares it with the shortest one already calculated''' 
                    path = path + second_path[1:]
                    path_travel_time = self.compute_path_travel_time(path) + 5
                    if path_travel_time < shortest_path_travel_time:
                        shortest_path_travel_time = path_travel_time

                # Resets the routes containing the destination for tests with other transfer point        
                routes_with_destination_aux = routes_with_destination

            # Does the same steps above but if the path is in reverse sense                            
            elif origin_id_index > chosen_transfer_point_index:
                while len(routes_with_destination_aux) != 0:
                    chosen_second_route = choice(routes_with_destination_aux)
                    routes_with_destination_aux.remove(chosen_second_route)
                    if chosen_transfer_point not in chosen_second_route:
                        continue
                    path = route[chosen_transfer_point_index:origin_id_index + 1]
                    path = list(path)
                    path.reverse()
                    path = tuple(path)
                    second_path = self.find_second_path(
                        destination_id,
                        chosen_transfer_point,
                        chosen_second_route
                    )
                    path = path + second_path[1:]
                    path_travel_time = self.compute_path_travel_time(path) + 5
                    if path_travel_time < shortest_path_travel_time:
                        shortest_path_travel_time = path_travel_time
                routes_with_destination_aux = routes_with_destination
            
        return shortest_path_travel_time

    # Method to get the path's travel time with two transfers
    def get_two_transfers_path_travel_time(
        self,
        origin_id,
        destination_id,
        route,
        routeset,
        transfer_points_from_origin,
        transfer_points_to_destination,
        routes_with_destination,
        shortest_path_travel_time
        ):

        '''A copy of the list of routes that contain the destination
        is needed to test all the possibilities'''
        routes_with_destination_aux = deepcopy(routes_with_destination)

        '''If the origin is in the route, gets its index,
        the transfer points from it and tests each of them'''
        if origin_id in route:
            origin_id_index = route.index(origin_id)
            transfer_points_from_origin_aux = list(transfer_points_from_origin)
            while len(transfer_points_from_origin_aux) != 0:
                chosen_transfer_point_from_origin = choice(transfer_points_from_origin_aux)
                transfer_points_from_origin_aux.remove(chosen_transfer_point_from_origin)
                if chosen_transfer_point_from_origin not in route:
                    continue

                '''If the chosen transfer point is in the route,
                gets its index and makes a slice of the route
                as the path's first part'''
                chosen_transfer_point_from_origin_index = route.index(chosen_transfer_point_from_origin)
                if origin_id_index < chosen_transfer_point_from_origin_index:
                    first_path = route[origin_id_index:chosen_transfer_point_from_origin_index + 1]
                elif origin_id_index > chosen_transfer_point_from_origin_index:
                    first_path = route[chosen_transfer_point_from_origin_index:origin_id_index + 1]                    
                    first_path = list(first_path)
                    first_path.reverse()
                    first_path = tuple(first_path)

                # Makes a copy of the list containing the transfer points to destination
                transfer_points_to_destination_aux = list(transfer_points_to_destination)

                # Tests for each transfer point
                while len(transfer_points_to_destination_aux) != 0:
                    chosen_transfer_point_to_destination = choice(transfer_points_to_destination_aux)
                    transfer_points_to_destination_aux.remove(chosen_transfer_point_to_destination)
                    if route in routes_with_destination_aux:
                        routes_with_destination_aux.remove(route)

                    # Tests for each route in the routes containing the destination
                    for second_route in routes_with_destination_aux:
                        if chosen_transfer_point_to_destination not in second_route:
                            continue
                        
                        # If the chosen transfer point is in the route, gets its index and destination's index
                        chosen_transfer_point_to_destination_index = second_route.index(chosen_transfer_point_to_destination)
                        destination_id_index = second_route.index(destination_id)

                        # Makes a slice of the route as the path's second part
                        if destination_id_index > chosen_transfer_point_to_destination_index:
                            second_path = second_route[chosen_transfer_point_to_destination_index:destination_id_index + 1]
                        elif destination_id_index < chosen_transfer_point_to_destination_index:
                            second_path = second_route[destination_id_index: chosen_transfer_point_to_destination_index + 1]
                            second_path = list(second_path)
                            second_path.reverse()
                            second_path = tuple(second_path)
                        
                        '''Updates the copy of the routeset,
                        removing the routes already used'''
                        routeset_aux = deepcopy(routeset)
                        routeset_aux.remove(route)
                        routeset_aux.remove(second_route)

                        # Tests for each remaining route in the routeset
                        for third_route in routeset_aux:

                            # Check if both previously chosen transfer points are in the route
                            if (
                                chosen_transfer_point_from_origin not in third_route
                                or
                                chosen_transfer_point_to_destination not in third_route
                            ):
                                continue

                            # If so, gets their indexes
                            chosen_transfer_point_from_origin_index_third_route = third_route.index(
                                chosen_transfer_point_from_origin
                            )
                            chosen_transfer_point_to_destination_index_third_route = third_route.index(
                                chosen_transfer_point_to_destination
                            )

                            # Makes a slice of the route as the path's third part 
                            if (
                                chosen_transfer_point_from_origin_index_third_route
                                <
                                chosen_transfer_point_to_destination_index_third_route
                            ):
                                third_path = third_route[
                                    chosen_transfer_point_from_origin_index_third_route
                                    :
                                    chosen_transfer_point_to_destination_index_third_route
                                    ]
                            elif (
                                chosen_transfer_point_from_origin_index_third_route
                                >
                                chosen_transfer_point_to_destination_index_third_route
                            ):
                                third_path = third_route[
                                    chosen_transfer_point_to_destination_index_third_route
                                    :
                                    chosen_transfer_point_from_origin_index_third_route
                                ]
                                third_path = list(third_path)
                                third_path.reverse()
                                third_path = tuple(third_path)

                            '''Concatenates all three parts,
                            computes the path travel time and
                            compares it with the shortest one already calculated'''
                            path = first_path + third_path[1:] + second_path[1:]
                            path_travel_time = self.compute_path_travel_time(path)
                            if path_travel_time < shortest_path_travel_time:
                                shortest_path_travel_time = path_travel_time

        return shortest_path_travel_time

    '''Method to get the shortest path's travel time
    in a given routeset, given a origin and a destination'''
    def get_shortest_path_travel_time(self, routeset, origin_id, destination_id):

        # Gets and saves the highest path travel time, the routeset's transfer points
        shortest_path_travel_time = self.transport_network.worst_path_travel_time
        routeset_transfer_points = self.get_transfer_points(routeset)

        '''Calculates the transfer points from origin,
        the transfer points to destination,
        the routes containing the origin,
        the routes containing the destination and
        the direct transfer points from origin to destination'''
        transfer_points_from_origin = set()
        transfer_points_to_destination = set()
        routes_with_origin = []
        routes_with_destination = []
        for route in routeset:
            route_aux = set(route)
            if origin_id in route:
                routes_with_origin.append(route)
                transfer_points_in_route_from_origin = route_aux.intersection(routeset_transfer_points)
                transfer_points_from_origin = transfer_points_from_origin.union(
                    transfer_points_in_route_from_origin
                )
            if destination_id in route:
                routes_with_destination.append(route)
                transfer_points_in_route_to_destination = route_aux.intersection(routeset_transfer_points)
                transfer_points_to_destination = transfer_points_to_destination.union(
                    transfer_points_in_route_to_destination
                ) 
        origin_destination_transfer_points = transfer_points_from_origin.intersection(
            transfer_points_to_destination
            )

        # For each route in the routeset
        for route in routeset:
            origin_destination_transfer_points_aux = deepcopy(origin_destination_transfer_points)
            '''Checks if there's a path without transfers,
            so both origin and destination are in the route,
            gets their indexes, makes a slice of the route as the path,
            calculates its travel time and compares it with the already calculated one'''
            if origin_id in route and destination_id in route:
                origin_id_index = route.index(origin_id)
                destination_id_index = route.index(destination_id)
                if origin_id_index < destination_id_index:
                    path = route[origin_id_index:destination_id_index + 1]
                elif origin_id_index > destination_id_index:
                    path = route[destination_id_index:origin_id_index + 1]
                else:
                    return 0
                path_travel_time = self.compute_path_travel_time(path)
                if path_travel_time < shortest_path_travel_time:
                    shortest_path_travel_time = path_travel_time

            # If there's not, searches for a route containing the origin,
            # gets the origin's index in the route and tries to get the path with one transfer
            elif len(origin_destination_transfer_points) != 0:
                if origin_id in route:
                    origin_id_index = route.index(origin_id)
                    routes_with_destination_aux = deepcopy(routes_with_destination)
                    shortest_path_travel_time = self.get_one_transfer_path_travel_time(
                        origin_destination_transfer_points_aux,
                        route,
                        destination_id,
                        origin_id_index,
                        routes_with_destination,
                        routes_with_destination_aux,
                        shortest_path_travel_time
                    )

            # If there're no direct transfer points, tries to get the path with two transfers
            elif len(origin_destination_transfer_points) == 0:
                shortest_path_travel_time = self.get_two_transfers_path_travel_time(
                    origin_id,
                    destination_id,
                    route,
                    routeset,
                    transfer_points_from_origin,
                    transfer_points_to_destination,
                    routes_with_destination,
                    shortest_path_travel_time
                )

        return shortest_path_travel_time

    # Method to calculate the routeset's passenger cost
    def calculate_passenger_cost(self, routeset_size, routeset, demand_matrix):

        # The numerator is the sum of the products of the demand value by the shortest path's travel time
        numerator = 0
    
        # For each pair of origin and destination
        for i in range(len(self.transport_network.graph)):
            for j in range(len(self.transport_network.graph)):

                '''Calculates the shortest path's travel time,
                multiplicates it by their demand value in the demand matrix
                and sums it to the numerator'''
                shortest_path_travel_time_from_i_to_j = self.get_shortest_path_travel_time(routeset, i, j)
                partial_numerator = demand_matrix.demand_matrix[i][j] * shortest_path_travel_time_from_i_to_j
                numerator += partial_numerator

        # The denominator is the sum of all demand values in the routeset
        denominator = 0

        # For each pair of origin and destination
        for i in range(len(self.transport_network.graph)):
            for j in range(len(self.transport_network.graph)):

                # Sums their demand value to the denominator
                denominator += demand_matrix.demand_matrix[i][j]
        passenger_cost = numerator / denominator

        return passenger_cost

    # Method to calculate the routeset's operator cost
    def calculate_operator_cost(self, routeset):

        '''The operator cost is the sum of travel time
        obtained by traversing all routes in one direction'''
        operator_cost = 0
        for route in routeset:

            # For each link in each route, sums its travel time to the operator cost
            route_links = list(zip(route, route[1:]))
            for (i, j) in route_links:
                for link in self.transport_network.graph[i].links:
                    if link.destination.id == j:
                        operator_cost += link.travel_time
        
        return operator_cost

    # Method to generate a offspring from the crossover of two parents
    def crossover(self, parent1, parent2):
        offspring = []

        # A copy of both parents is needed
        parent1_copy = list(deepcopy(parent1))
        parent2_copy = list(deepcopy(parent2))

        # Chooses randomly from the first parent a route as the seed
        seed = choice(parent1_copy)
        parent1_copy.remove(seed)
        offspring.append(seed)
        first_parent = True

        # Repeats until offspring has the same size as its parents
        while len(offspring) < len(parent1):

            # Alternates the chosen parent
            if first_parent:
                chosen_parent = parent2_copy
            else:
                chosen_parent = parent1_copy

            # Calculates the potential routes to be part of the offspring
            potential_routes = []
            for route in chosen_parent:
                seed = set(seed)

                '''It is needed to have at least one access point in common
                between the seed and the potential route'''
                if not seed.isdisjoint(set(route)):
                    potential_routes.append(route)
            
            # Calculates the next route to be added to the offspring from the potential routes
            next_route = []
            smallest_intersection = len(self.transport_network.graph)
            for route in potential_routes:
                if route in offspring:
                    continue
                intersection = seed.intersection(set(route))

                '''Which is the route with the smallest amount
                of access points in common with the seed'''
                if len(intersection) < smallest_intersection:
                    smallest_intersection = len(intersection)
                    next_route = route
            
            '''This is needed to avoid a infinite loop
            by a lack of potential routes absent from the offspring'''
            parent_attempted = tuple(chosen_parent)
            if len(next_route) == 0:
                if "parents_attempted" not in locals():
                    parents_attempted = set()
                    parents_attempted.add(parent_attempted)
                else:
                    parents_attempted.add(parent_attempted)
                    if len(parents_attempted) == 2:
                        break
                first_parent = not first_parent
                continue
            

            '''Updates the seed, adding the chosen route's access points
            to it and alternates the chosen parent'''
            chosen_parent.remove(next_route)
            offspring.append(next_route)
            seed = seed.union(set(next_route))
            parents_attempted = set()
            first_parent = not first_parent
        
        offspring = set(offspring)

        # If the offspring was not successfully generated, deletes it
        if len(offspring) != len(parent1):
            return False

        return offspring

    # Method to add access points to the routeset        
    def add_access_points(
        self,
        routeset,
        access_points_to_be_changed,
        touched_access_points,
        all_access_points
        ):

        # A copy of the routeset is needed
        aux_routeset = list(deepcopy(routeset))
        modified_routeset = []

        # Repeats until the predetermined number of access points is added
        added_access_points = 0
        while added_access_points < access_points_to_be_changed:

            # Or all routes were tested
            if len(aux_routeset) == 0:
                break
            chosen_route = choice(aux_routeset)
            aux_routeset.remove(chosen_route)
            chosen_route = list(chosen_route)

            # Repeats until chosen route has reached the maximum length
            while (len(chosen_route)
                    <
                    self.initial_population_generator.maximum_length):

                '''Gets both terminal's indexes, neighborhoods and
                calculates the possible access points to be added '''
                length_before = len(chosen_route)
                terminal1_id = chosen_route[0]
                terminal2_id = chosen_route[-1]
                terminal1 = self.transport_network.get_by_id(terminal1_id)
                terminal1_neighborhood = set(
                    parser.get_access_points_id(
                        terminal1.get_neighborhood()
                    )
                )
                candidates_for_addition_terminal1 = list(
                    terminal1_neighborhood - set(chosen_route)
                )
                terminal2 = self.transport_network.get_by_id(terminal2_id)
                terminal2_neighborhood = set(
                    parser.get_access_points_id(
                        terminal2.get_neighborhood()
                    )
                )
                candidates_for_addition_terminal2 = list(
                    terminal2_neighborhood - set(chosen_route)
                )
                if (len(candidates_for_addition_terminal1) == 0
                    and
                    len(candidates_for_addition_terminal2) == 0 ):
                    break

                '''Tests one of the terminals, chooses one access point
                from the possible ones and insert it in the route '''
                chosen_terminal = choice([terminal1_id, terminal2_id])
                if chosen_terminal == terminal1_id:
                    if len(candidates_for_addition_terminal1) > 0:
                        chosen_access_point = choice(
                            candidates_for_addition_terminal1
                            )
                        chosen_route.insert(0, chosen_access_point)
                    else:
                        chosen_terminal = terminal2_id
                if chosen_terminal == terminal2_id:
                    if len(candidates_for_addition_terminal2) > 0:
                        chosen_access_point = choice(
                            candidates_for_addition_terminal2
                            )
                        chosen_route.append(chosen_access_point)

                # Checks if the access point was successfully added
                if len(chosen_route) > length_before:
                    added_access_points += 1

                # Terminates if the number of access points to be added was reached
                if added_access_points == access_points_to_be_changed:
                    break

            chosen_route = tuple(chosen_route)
            modified_routeset.append(chosen_route)
        
        # Adds the remaining unchanged routes to the routeset
        if len(modified_routeset) < len(routeset):
            for route in aux_routeset:
                modified_routeset.append(route)
        modified_routeset = set(modified_routeset)

        return modified_routeset

    # Method to delete access points from the routeset
    def delete_access_points(self, routeset, access_points_to_be_changed):

        # A copy of the routeset is needed
        aux_routeset = list(deepcopy(routeset))
        modified_routeset = []
        deleted_access_points = 0

        '''Gets the access points occurences in the routeset,
        in order to only delete the ones that are in more than one route'''
        access_points_occurences = {}
        for route in routeset:
            for access_point_id in route:
                if access_point_id not in access_points_occurences.keys():
                    access_points_occurences[access_point_id] = 1
                else:
                    access_points_occurences[access_point_id] += 1

        # Repeats until the predetermined number of access points is deleted
        while deleted_access_points < access_points_to_be_changed:

            # Or all routes were tested
            if len(aux_routeset) == 0:
                break
            chosen_route = choice(aux_routeset)
            aux_routeset.remove(chosen_route)
            chosen_route = list(chosen_route)

            # Repeats until the chosen route has reached the minimum length
            while (len(chosen_route)
                    >
                    self.initial_population_generator.minimum_length
                ):

                '''Gets both terminals' indexes,
                checks if they appear in more than one route,
                chooses one of them, deletes it from the chosen route
                and checks if the routeset remains connected'''
                terminal1_id = chosen_route[0]
                terminal2_id = chosen_route[-1]
                if (access_points_occurences[terminal1_id] == 1
                    and
                    access_points_occurences[terminal2_id] == 1):
                    break
                terminal_id = choice([terminal1_id, terminal2_id])
                if "terminal_id_before" in locals():
                    while (terminal_id == terminal_id_before):
                        terminal_id = choice([terminal1_id, terminal2_id])
                terminal_id_before = terminal_id
                if access_points_occurences[terminal_id] > 1:
                    length_before = len(chosen_route)
                    terminal_id_in_route = chosen_route.index(terminal_id)
                    chosen_route.remove(terminal_id)
                    routeset_is_connected = self.check_connectivity(routeset)

                    '''This is needed to avoid a infinite loop
                    caused by trying the terminals over and over again'''
                    terminal_id_attempted = terminal_id
                    if not routeset_is_connected:
                        if "terminals_attempted" not in locals():
                            terminals_attempted = set()
                            terminals_attempted.add(terminal_id_attempted)
                            if terminal_id_in_route == 0:
                                chosen_route.insert(terminal_id_in_route, terminal_id)
                                continue
                            elif terminal_id_in_route == len(chosen_route):
                                chosen_route.append(terminal_id)
                                continue
                        else:
                            terminals_attempted.add(terminal_id_attempted)
                            if terminal_id_in_route == 0:
                                chosen_route.insert(terminal_id_in_route, terminal_id)
                            elif terminal_id_in_route == len(chosen_route):
                                chosen_route.append(terminal_id)
                            if len(terminals_attempted) == 2:
                                del terminals_attempted
                                break
                            else:
                                continue
                    else:
                        access_points_occurences[terminal_id] -= 1   

                        # Checks if the terminal was successfully deleted
                        if len(chosen_route) < length_before:
                            deleted_access_points += 1

                # If the terminal appears only in one route, tries the other
                if access_points_occurences[terminal_id] == 1:

                    '''This is needed to avoid a infinite loop
                    caused by trying the terminals over and over again'''
                    terminal_id_attempted = terminal_id
                    if "terminals_attempted" not in locals():
                        terminals_attempted = set()
                        terminals_attempted.add(terminal_id_attempted)
                        continue
                    else:
                        terminals_attempted.add(terminal_id_attempted)
                        if len(terminals_attempted) == 2:
                            del terminals_attempted
                            break
                        else:
                            continue

                # Terminates if the number of access points to be deleted was reached
                if deleted_access_points == access_points_to_be_changed:
                    break

            chosen_route = tuple(chosen_route)
            modified_routeset.append(chosen_route)

        # Adds the remaining unchanged routes to the routeset
        if len(modified_routeset) < len(routeset):
            for route in aux_routeset:
                modified_routeset.append(route)
        modified_routeset = set(modified_routeset)

        return modified_routeset

    # Method to add to or delete access points from the routeset as the mutation
    def mutation(
        self,
        individual,
        touched_access_points,
        all_access_points
        ):
        access_points_to_be_changed = randrange(
            1,
            self.initial_population_generator.routeset_size * (
                self.initial_population_generator.maximum_length//2
            )
        )
        choice = getrandbits(1)
        if choice:
            individual = self.add_access_points(
                individual,
                access_points_to_be_changed,
                touched_access_points,
                all_access_points,
                )
        else:
            individual = self.delete_access_points(
                individual,
                access_points_to_be_changed
                )

        return individual

    # Method to replace a parent in the population with the offspring
    def replace_parents_with_offspring(
        self,
        parent,
        parent_index,
        offspring,
        offspring_passenger_cost,
        offspring_operator_cost,
        passenger_cost,
        operator_cost
        ):
        self.initial_population_generator.population[parent_index] = offspring
        passenger_cost[parent_index] = offspring_passenger_cost
        operator_cost[parent_index] = offspring_operator_cost

    # Method to replace a random parent in the population with the offspring    
    def replace_random_parent(
        self,
        parent1,
        parent1_index,
        parent2,
        parent2_index,
        offspring,
        offspring_passenger_cost,
        offspring_operator_cost,
        passenger_cost,
        operator_cost
        ):
        parent_index = int()
        chosen_parent = choice([parent1, parent2])
        if chosen_parent == parent1:
            parent_index = parent1_index
        elif chosen_parent == parent2:
            parent_index = parent2_index
        seamo2.replace_parents_with_offspring(
            chosen_parent,
            parent_index,
            offspring,
            offspring_passenger_cost,
            offspring_operator_cost,
            passenger_cost,
            operator_cost
            )

    '''Method to calculate the passenger cost and operator cost
    of each routeset in the population and
    to get the best routesets for passenger cost and for operator cost'''
    def evaluate_population(self):
        passenger_cost = {}
        best_routeset_so_far_passenger_cost = []
        operator_cost = {}
        best_routeset_so_far_operator_cost = []
        for routeset_id, routeset in self.initial_population_generator.population.items():
            routeset_passenger_cost = self.calculate_passenger_cost(
                    self.initial_population_generator.routeset_size,
                    routeset,
                    self.demand_matrix
                )
            passenger_cost[routeset_id] = routeset_passenger_cost
            
            routeset_operator_cost = self.calculate_operator_cost(routeset)
            operator_cost[routeset_id] = routeset_operator_cost

        lowest_passenger_cost = min(passenger_cost.values())
        for routeset_index, routeset_passenger_cost in passenger_cost.items():
            if routeset_passenger_cost == lowest_passenger_cost:
                routeset = seamo2.initial_population_generator.population[routeset_index]
                best_routeset_so_far_passenger_cost = [
                    routeset_index,
                    routeset,
                    lowest_passenger_cost
                    ]
                break

        lowest_operator_cost = min(operator_cost.values())
        for routeset_index, routeset_operator_cost in operator_cost.items():
            if routeset_operator_cost == lowest_operator_cost:
                routeset = seamo2.initial_population_generator.population[routeset_index]
                best_routeset_so_far_operator_cost = [
                    routeset_index,
                    routeset,
                    routeset_operator_cost
                    ]
                break

        return passenger_cost, operator_cost, best_routeset_so_far_passenger_cost, best_routeset_so_far_operator_cost

    def plot_routeset(self, routeset, figure, graph, objective, edge_labels):
        for route_index, route in enumerate(routeset):
            route_nodes = []
            route_nodes_positions = {}
            for access_point_id in route:
                route_nodes.append(access_point_id)
                route_nodes_positions[access_point_id] = self.coords.coords[access_point_id]
            route_edges = list(zip(route_nodes, route_nodes[1:]))
            route_edges_labels = {}
            for route_edge in route_edges:
                route_edges_labels[route_edge] = edge_labels[route_edge]
            plt.figure(figure)
            nx.draw_networkx(graph, seamo2.coords.coords, with_labels=True, node_color="#B3B3B3")
            color_map = plt.colormaps.get_cmap("hsv")
            random_color = color_map(random())
            color = np.array(random_color).reshape(1,-1)
            nx.draw_networkx_nodes(graph, route_nodes_positions, route_nodes, node_color=color)
            nx.draw_networkx_edges(graph, route_nodes_positions, route_edges, edge_color=color, width=3)
            nx.draw_networkx_edge_labels(graph, seamo2.coords.coords, edge_labels=route_edges_labels, rotate=False)       
            figure += 1
            plt.savefig(self.file_name + "_best_" + objective + "_cost_route_" + str(route_index) + ".pdf")
            
        return figure

# Execution of SEAMO2
seamo2 = SEAMO2("Mandl")

'''Builds the adjacencies list for the NetworkX module,
creates the transport network with the coordinates
for the access points and saves it in a pdf file with matplotlib'''
adjacencies_list = seamo2.transport_network.build_adjacencies_list()
edge_labels = seamo2.transport_network.get_edges_travel_time()
graph = nx.Graph(adjacencies_list)
nx.draw_networkx(graph, seamo2.coords.coords, with_labels=True, node_color="#B3B3B3")
nx.draw_networkx_edge_labels(graph, seamo2.coords.coords, edge_labels=edge_labels, rotate=False)
plt.savefig(seamo2.file_name + ".pdf")

'''Calculates the passenger costs, the operator costs and
the bests routeset for each objective'''
(
    passenger_cost,
    operator_cost,
    best_routeset_so_far_passenger_cost,
    best_routeset_so_far_operator_cost
) = seamo2.evaluate_population()

generations = int(input("How many generations do you want? "))
figure = 2
plt.figure(figure)

# Repeats until the number of generations is reached
for generation_number in range(generations):
    print(f"Generation number {generation_number}\n")

    # Calculations needed to plot the population with matplotlib
    population_data = []
    passenger_cost_values = []
    operator_cost_values = []
    for routeset_index, routeset in seamo2.initial_population_generator.population.items():
        routeset_passenger_cost_value = passenger_cost[routeset_index]
        routeset_operator_cost_value = operator_cost[routeset_index]
        passenger_cost_values.append(routeset_passenger_cost_value)
        operator_cost_values.append(routeset_operator_cost_value)
        population_data.append((routeset_passenger_cost_value, routeset_operator_cost_value))
    
    # Plots only the generations multiple of 10
    if generation_number % 10 == 0:
        color_map = plt.colormaps.get_cmap("hsv")
        random_color = color_map(random())
        color = np.array(random_color).reshape(1,-1)
        plt.scatter(passenger_cost_values, operator_cost_values, c=color)
        plt.xlabel("Passenger cost")
        plt.ylabel("Operator cost")
        plt.savefig(seamo2.file_name + "_" + str(generation_number) + ".pdf")

    # A copy of the routesets' indexes in the population is needed
    aux_population = list(seamo2.initial_population_generator.population.keys())
    index = 0

    '''For each routeset in the population,
    selects it as the first parent and
    picks randomly a different second parent '''
    for _ in range(len(seamo2.initial_population_generator.population)):
        parent1_index = aux_population[index]
        parent1 = seamo2.initial_population_generator.population[parent1_index]
        aux_population.remove(parent1_index)
        parent2_index = choice(aux_population)
        parent2 = seamo2.initial_population_generator.population[parent2_index]
        aux_population.insert(index, parent1_index)
        index += 1
        if parent1 != parent2:

            # Calls the crossover of the two parents and generates the offspring
            offspring = seamo2.crossover(parent1, parent2)

            if offspring == False:
                continue

            all_access_points = parser.get_access_points_id(seamo2.transport_network.graph)

            # Gets the used access points in the offspring
            touched_access_points = set()
            for route in offspring:
                touched_access_points = touched_access_points.union(set(route))

            # If there're unused access points, tries to repair the offspring
            if len(touched_access_points) < len(seamo2.transport_network.graph):
                offspring = ipg.repair(
                    offspring,
                    all_access_points,
                    touched_access_points,
                    len(seamo2.transport_network.graph),
                    seamo2.initial_population_generator.routeset_size,
                    seamo2.initial_population_generator.maximum_length,
                    seamo2.initial_population_generator.minimum_length,
                    seamo2.transport_network
                    )
                if offspring == False:
                    continue

            # Updates the used access points in the offspring
            for route in offspring:
                touched_access_points = touched_access_points.union(set(route))

            # Applies mutation to the offspring
            offspring = seamo2.mutation(
                offspring,
                touched_access_points,
                all_access_points
                )

            # Deletes the offspring if its a duplicate
            offspring_is_duplicate = False
            for routeset in seamo2.initial_population_generator.population.values():
                if offspring == routeset:
                    offspring_is_duplicate = True
                    break
            if offspring_is_duplicate:
                continue

            # Calculates the offspring's passenger cost and operator cost                    
            offspring_passenger_cost = seamo2.calculate_passenger_cost(
                seamo2.initial_population_generator.routeset_size,
                offspring,
                seamo2.demand_matrix
                )
            offspring_operator_cost = seamo2.calculate_operator_cost(offspring)

            # Gets the first parent's passenger cost and operator cost
            parent1_passenger_cost = passenger_cost[parent1_index]
            parent1_operator_cost = operator_cost[parent1_index] 

            '''If offspring dominates the first parent,
            it replaces the dominated parent in the population'''
            if offspring_passenger_cost < parent1_passenger_cost and offspring_operator_cost < parent1_operator_cost:                
                seamo2.replace_parents_with_offspring(
                    parent1,
                    parent1_index,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost,
                    passenger_cost,
                    operator_cost
                    )
                continue

            # Gets the second parent's passenger cost and operator cost
            parent2_passenger_cost = passenger_cost[parent2_index]
            parent2_operator_cost = operator_cost[parent2_index]

            '''If offspring dominates the second parent,
            it replaces the dominated parent in the population'''
            if offspring_passenger_cost < parent2_passenger_cost and offspring_operator_cost < parent2_operator_cost:
                seamo2.replace_parents_with_offspring(
                    parent2,
                    parent2_index,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost,
                    passenger_cost,
                    operator_cost
                    )
                continue

            '''If offspring dominates the best routeset for passenger cost or
            improves the passenger cost, it replaces one of the chosen parents in the population'''
            if (
                (offspring_passenger_cost < best_routeset_so_far_passenger_cost[2]
                and
                offspring_operator_cost < operator_cost[best_routeset_so_far_passenger_cost[0]])
                or offspring_passenger_cost < best_routeset_so_far_passenger_cost[2]
                ):
                best_routeset_so_far_passenger_cost = [
                    best_routeset_so_far_passenger_cost[0],
                    offspring,
                    offspring_passenger_cost
                    ]
                seamo2.replace_random_parent(
                    parent1,
                    parent1_index,
                    parent2,
                    parent2_index,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost,
                    passenger_cost,
                    operator_cost
                    )                    
                continue

            '''If offspring dominates the best routeset for operator cost or
            improves the operator cost, it replaces one of the chosen parents in the population'''
            if ((offspring_operator_cost < best_routeset_so_far_operator_cost[2]
                and
                offspring_passenger_cost < passenger_cost[best_routeset_so_far_operator_cost[0]])
                or offspring_operator_cost < best_routeset_so_far_operator_cost[2]
                ):
                best_routeset_so_far_operator_cost = [
                    best_routeset_so_far_operator_cost[0],
                    offspring,
                    offspring_operator_cost
                    ]
                seamo2.replace_random_parent(
                    parent1,
                    parent1_index,
                    parent2,
                    parent2_index,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost,
                    passenger_cost,
                    operator_cost
                    )
                continue

            # If the offspring and its parents are mutually non-dominanting
            if (
                    (offspring_passenger_cost >= parent1_passenger_cost
                    and
                    offspring_operator_cost <= parent1_operator_cost)
                        or
                    (offspring_passenger_cost <= parent1_passenger_cost
                    and
                    offspring_operator_cost >= parent1_operator_cost)
                        or
                    (offspring_passenger_cost >= parent2_passenger_cost
                    and
                    offspring_operator_cost <= parent2_operator_cost)
                        or
                    (offspring_passenger_cost <= parent2_passenger_cost
                    and
                    offspring_operator_cost >= parent2_operator_cost)
                ):

                '''Finds a routeset in the population that is dominated by the offspring
                and replaces it with the offspring'''
                for routeset_index, routeset in seamo2.initial_population_generator.population.items():
                    routeset_passenger_cost = passenger_cost[routeset_index]
                    routeset_operator_cost = operator_cost[routeset_index]
                    if (offspring_passenger_cost < routeset_passenger_cost
                        and
                        offspring_operator_cost < routeset_operator_cost):
                        seamo2.initial_population_generator.population[routeset_index] = offspring
                        passenger_cost[routeset_index] = offspring_passenger_cost
                        operator_cost[routeset_index] = offspring_operator_cost
            else:
                continue

# Generates images of the best routeset for each objective with NetworkX and saves them in pdf files
nodes = parser.get_access_points_id(seamo2.transport_network.graph)
figure = 3 
figure = seamo2.plot_routeset(
    best_routeset_so_far_passenger_cost[1],
    figure,
    graph,
    "passenger",
    edge_labels
    )

figure = seamo2.plot_routeset(
    best_routeset_so_far_operator_cost[1],
    figure,
    graph,
    "operator",
    edge_labels
    )

# Generates a txt file with the final population
pareto_frontier = []
for routeset_index in seamo2.initial_population_generator.population:
    pareto_frontier.append(f"{passenger_cost[routeset_index]:.4f} {operator_cost[routeset_index]}")
file_name = f"{seamo2.file_name}_Pareto.txt"
with open(file_name, 'w') as f:
    f.write('\n'.join(pareto_frontier))

# Generates a txt file with the best routeset for passenger cost
best_passenger_cost = []
for route_index, route in enumerate(best_routeset_so_far_passenger_cost[1]):
    line = f"Route {route_index} : {route}"
    best_passenger_cost.append(line)
file_name = f"{seamo2.file_name}_Best_Passenger_Cost.txt"
with open(file_name, 'w') as f:
    f.write(f"Best {seamo2.file_name} routeset for passenger cost\n")
    f.write('\n'.join(best_passenger_cost))

# Generates a txt file with the best routeset for operator cost
best_operator_cost = []
for route_index, route in enumerate(best_routeset_so_far_operator_cost[1]):
    line = f"Route {route_index} : {route}"
    best_operator_cost.append(line)
file_name = f"{seamo2.file_name}_Best_Operator_Cost.txt"
with open(file_name, 'w') as f:
    f.write(f"Best {seamo2.file_name} routeset for operator cost\n")
    f.write('\n'.join(best_operator_cost))
