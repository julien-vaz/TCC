# Module dedicated to generate the initial population

import parser
from random import randint, choice
from copy import deepcopy

# Function to add unused access points during the repair mechanism
def add_unused_access_points(
    chosen_route,
    terminal,
    position,
    unused_access_points,
    touched_access_points
    ):
    chosen_route = list(chosen_route)
    if position == -1:
        position = len(chosen_route)
    terminal_neighborhood = set(parser.get_access_points_id(terminal.get_neighborhood()))

    '''The possible access points to be added are the intersection
     of the terminal's neighborhood with the unused access points '''
    possible_unused_nodes_terminal = list(unused_access_points.intersection(terminal_neighborhood))
    if len(possible_unused_nodes_terminal) != 0:

        '''Chooses the new terminal from the possible access points
        and add it to the route'''
        new_terminal = choice(possible_unused_nodes_terminal)
        touched_access_points.add(new_terminal)
        chosen_route.insert(position, new_terminal)
    chosen_route = tuple(chosen_route)

    return chosen_route, touched_access_points

# Repair mechanism
def repair(
    routeset,
    all_access_points,
    touched_access_points,
    network_size,
    routeset_size,
    maximum_length,
    minimum_length,
    transport_network
    ):
    aux_routeset = deepcopy(list(routeset))
    repaired_routeset = []

    # Tries adding access points to all routes
    while aux_routeset != []:
        chosen_route = choice(aux_routeset)
        aux_routeset.remove(chosen_route)
        if len(chosen_route) < maximum_length:
            unused_access_points = set(all_access_points) - touched_access_points
            for _ in range(2 * network_size):

                '''Until there're no access points outside the routeset
                or the route has reached the maximum length of access points'''
                if (
                    len(unused_access_points) == 0
                    or
                    len(chosen_route) == maximum_length
                    ):
                    break

                # Calculates the both terminal's neighborhoods
                terminal1_id = chosen_route[0]
                terminal1 = transport_network.get_by_id(terminal1_id)
                terminal1_neighborhood = set(
                    parser.get_access_points_id(
                        terminal1.get_neighborhood()
                    )
                )
                terminal2_id = chosen_route[-1]
                terminal2 = transport_network.get_by_id(terminal2_id)
                terminal2_neighborhood = set(
                    parser.get_access_points_id(
                        terminal2.get_neighborhood()
                    )
                )

                # Checks if there isn't unused access points in the neighborhoods
                if (len(unused_access_points.intersection(
                        terminal1_neighborhood
                        )) == 0
                    and
                    len(unused_access_points.intersection(
                        terminal2_neighborhood
                        )) == 0
                    ):
                    break 

                # Adds it from the terminal 1
                chosen_route, touched_access_points = add_unused_access_points(
                    chosen_route,
                    terminal1,
                    0,
                    unused_access_points,
                    touched_access_points,
                    )
                unused_access_points = set(all_access_points) - touched_access_points

                # Adds it from the terminal 2
                chosen_route, touched_access_points = add_unused_access_points(
                    chosen_route,
                    terminal2,
                    -1,
                    unused_access_points,
                    touched_access_points
                    )
                unused_access_points = set(all_access_points) - touched_access_points
        repaired_routeset.append(chosen_route)
    repaired_routeset = set(repaired_routeset)

    # Checks if the routeset was successfully repaired
    if len(touched_access_points) == network_size:

        return repaired_routeset

    return False

# Class to receive the user parameters and generate the initial population
class InitialPopulationGenerator:
    def __init__(self, transport_network):
        self.routeset_size = int(input("Choose a size for the routesets to be generated: "))
        self.minimum_length = int(input("Choose a minimum length for the routes to be generated: "))
        self.maximum_length = int(input("Choose a maximum length for the routes to be generated: "))
        self.population_size = int(input("Choose the population size: "))
        self.transport_network = transport_network
        self.population = self.generate_initial_population(
            self.population_size,
            self.transport_network
            )

    def generate_initial_population(self, population_size, transport_network):
        print("Initial population is being generated...")
        # Population is a dictionary in order to use the routesets' indexes as keys
        population = {}
        routeset_index = 0
        while len(population) < population_size:
            routeset = self.generate_routeset(transport_network)
            if routeset not in population.values() and routeset != False:
                population[routeset_index] = routeset
                routeset_index += 1
        print("Initial population has been successfully generated.")

        return population
        
    def generate_routeset(self, transport_network):
        print("Generating routeset...")
        network_size = len(transport_network.graph)

        # Routeset is created as an array to be easier to manipulate the structure
        routes = [[]]

        # The already used access points are stored in this set
        touched_access_points = set()

        # In case of not reaching the desired length, the route is regenerated
        regrow_route = False
        count = 0
        while count < self.routeset_size:
            desired_length = randint(self.minimum_length, self.maximum_length)
            print(f"Desired length: {desired_length}")

            # If it's the first route of the routeset
            if count == 0:

                # Picks a random access point to be the seed
                selected_access_point = choice(self.transport_network.graph)
                selected_access_point_id = selected_access_point.id
                if regrow_route:
                    selected_access_point_id = regrow_route_from
                routes[count] = [selected_access_point_id]
                touched_access_points.add(selected_access_point_id)
            else:

                # Seeds the next route, ensuring connectivity in the routeset
                selected_access_point_id = choice(list(touched_access_points))
                if regrow_route:
                    selected_access_point_id = regrow_route_from
                    routes[count].append(selected_access_point_id)
                else:
                    routes.insert(count, [selected_access_point_id])
                touched_access_points.add(selected_access_point_id)
            route_length = len(routes[count])

            # This stores the last set of already used access points for the regrow strategy
            touched_access_points_before = deepcopy(touched_access_points)

            # The route can have its growing sense reversed only once
            times_reversed = 0
            while(route_length < desired_length and times_reversed <= 1):
                selected_access_point = self.transport_network.get_by_id(
                    selected_access_point_id
                )

                # Gets the selected access point's neighborhood in order to keep growing the route
                neighborhood = selected_access_point.get_neighborhood()
                neighborhood_ids = set(parser.get_access_points_id(neighborhood))
                all_access_points = transport_network.graph
                all_access_points_ids = set(parser.get_access_points_id(all_access_points))
                current_route_access_points_ids = set(routes[count])
                absent_access_points_ids = all_access_points_ids - current_route_access_points_ids

                # The candidates are the unused access points that belong to the access point's neighborhood
                unused_access_points_ids = list(neighborhood_ids.intersection(
                    absent_access_points_ids
                    )
                )

                # If there are still remaining access points
                if unused_access_points_ids != []:

                    # Picks randomly one and insert it in the route
                    next_access_point = choice(unused_access_points_ids)
                    routes[count].insert(route_length + 1, next_access_point)
                    route_length = len(routes[count])
                    selected_access_point_id = next_access_point
                    touched_access_points.add(next_access_point)
                else:

                    # Reverses the route's growing sense
                    routes[count].reverse()
                    selected_access_point_id = routes[count][route_length - 1]
                    times_reversed += 1

            # If the desired length is not reached
            if route_length != desired_length:
                print(f"Desired length was not achieved. Trying to grow route {count} again.")

                # Tries again from the route's initial access point
                regrow_route = True
                regrow_route_from = routes[count][0]
                routes[count].clear()

                # Resets the set of used access points to before the route was grown
                touched_access_points = touched_access_points_before
            else:
                print(f"Route {count} has been successfully generated.")
                regrow_route = False
                count += 1

        # Converts the routeset from array to set
        routeset = set()
        for route in routes:

            # And the routes from array to tuple
            route = tuple(route)
            routeset.add(route)
        print("Routeset has been generated")
        print()

        # Checks if there weren't duplicated routes
        if len(routeset) != self.routeset_size:
            print("Routeset is infeasible. It will be discarded from the population.")
            return False

        # Checks if the routeset is connected
        if len(touched_access_points) < network_size:
            print("Starting repair of routeset...")
            repaired_routeset = repair(
                routeset,
                all_access_points_ids,
                touched_access_points,
                network_size,
                self.routeset_size,
                self.maximum_length,
                self.minimum_length,
                self.transport_network
                )
            if repaired_routeset:
                print("Routeset has been successfully repaired. Adding it to the population...")

                return repaired_routeset
            else:
                print("Routeset is infeasible. It will be discarded from the population.")
                
                return False
            
        return routeset