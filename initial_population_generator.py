import parser
from random import randint, choice
from copy import deepcopy


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
    # Intersecção, não diferença
    possible_unused_nodes_terminal = list(unused_access_points.intersection(terminal_neighborhood))
    if len(possible_unused_nodes_terminal) != 0:
        new_terminal = choice(possible_unused_nodes_terminal)
        touched_access_points.add(new_terminal)
        chosen_route.insert(position, new_terminal)
    chosen_route = tuple(chosen_route)
    return chosen_route, touched_access_points


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
    while aux_routeset != []:
        chosen_route = choice(aux_routeset)
        aux_routeset.remove(chosen_route)
        if len(chosen_route) < maximum_length:
            # add possible unused access points to either ends
            unused_access_points = set(all_access_points) - touched_access_points
            
            # MAYBE TOO MANY ITERATIONS
            for _ in range(2 * network_size):
                if (
                    len(unused_access_points) == 0
                    or
                    len(chosen_route) == maximum_length
                    ):
                    break
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
                if (len(unused_access_points.intersection(
                        terminal1_neighborhood
                        )) == 0
                    and
                    len(unused_access_points.intersection(
                        terminal2_neighborhood
                        )) == 0
                    ):
                    break 
                
                chosen_route, touched_access_points = add_unused_access_points(
                    chosen_route,
                    terminal1,
                    0,
                    unused_access_points,
                    touched_access_points,
                    )
                unused_access_points = all_access_points - touched_access_points
                
                chosen_route, touched_access_points = add_unused_access_points(
                    chosen_route,
                    terminal2,
                    -1,
                    unused_access_points,
                    touched_access_points
                    )
                unused_access_points = all_access_points - touched_access_points
        repaired_routeset.append(chosen_route)
    repaired_routeset = set(repaired_routeset)
    if len(touched_access_points) == network_size:
        return repaired_routeset
    return False


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
        population = []
        routeset_index = 0
        while len(population) < population_size:
            routeset = self.generate_routeset(transport_network)
            if routeset not in population and routeset != False:
                population.append([routeset_index, routeset])
                routeset_index += 1
        print("Initial population has been successfully generated.")
        return population
        

    def generate_routeset(self, transport_network):
        print("Generating routeset...")
        network_size = len(transport_network.graph)

        routes = [[]]

        touched_access_points = set()
        regrow_route = False
        count = 0
        while count < self.routeset_size:
            desired_length = randint(self.minimum_length, self.maximum_length)
            print(f"Desired length: {desired_length}")
            # if it's the first route of the routeset
            if count == 0:
                # pick a random access point to be the seed
                selected_access_point = choice(self.transport_network.graph)
                selected_access_point_id = selected_access_point.id
                if regrow_route:
                    selected_access_point_id = regrow_route_from
                routes[count] = [selected_access_point_id]
                touched_access_points.add(selected_access_point_id)
            else:
                # seed the next route, ensuring connectivity
                selected_access_point_id = choice(list(touched_access_points))
                if regrow_route:
                    selected_access_point_id = regrow_route_from
                    routes[count].append(selected_access_point_id)
                else:
                    routes.insert(count, [selected_access_point_id])
                touched_access_points.add(selected_access_point_id)
            route_length = len(routes[count])

            touched_access_points_before = deepcopy(touched_access_points)
            times_reversed = 0
            while(route_length < desired_length and times_reversed <= 1):
                selected_access_point = self.transport_network.get_by_id(
                    selected_access_point_id
                )
                neighborhood = selected_access_point.get_neighborhood()
                neighborhood_ids = set(parser.get_access_points_id(neighborhood))
                all_access_points = transport_network.graph
                all_access_points_ids = set(parser.get_access_points_id(all_access_points))
                current_route_access_points_ids = set(routes[count])
                absent_access_points_ids = all_access_points_ids - current_route_access_points_ids
                unused_access_points_ids = list(neighborhood_ids.intersection(
                    absent_access_points_ids
                    )
                )
                if unused_access_points_ids != []:
                    next_access_point = choice(unused_access_points_ids)
                    routes[count].insert(route_length + 1, next_access_point)
                    route_length = len(routes[count])
                    selected_access_point_id = next_access_point
                    touched_access_points.add(next_access_point)
                else:
                    routes[count].reverse()
                    selected_access_point_id = routes[count][route_length - 1]
                    times_reversed += 1
            
            if route_length != desired_length:
                print(f"Desired length was not achieved. Trying to grow route {count} again.")
                regrow_route = True
                regrow_route_from = routes[count][0]
                routes[count].clear()
                touched_access_points = touched_access_points_before

            else:
                print(f"Route {count} has been successfully generated.")
                regrow_route = False
                count += 1
        
        routeset = set()
        for route in routes:
            route = tuple(route)
            routeset.add(route)
        print("Routeset has been generated")
        print()

        if len(routeset) != self.routeset_size:
            print("Routeset is infeasible. It will be discarded from the population.")
            return False
        
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