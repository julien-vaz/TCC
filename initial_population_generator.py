import parser
from random import randint, choice
from copy import deepcopy


def add_unused_access_points(terminal, position, unused_access_points):
    terminal_neighborhood = set(terminal.get_neighborhood())
    # Intersecção, não diferença
    possible_unused_nodes_terminal = list(unused_access_points - terminal_neighborhood)
    if len(possible_unused_nodes_terminal) != 0:
        new_terminal = choice(possible_unused_nodes_terminal)
        touched_access_points.add(new_terminal)
        chosen_route.insert(position, new_terminal)
        return chosen_route, touched_access_points


def repair(
    routeset,
    all_access_points,
    touched_access_points,
    network_size,
    routeset_size,
    maximum_length,
    minimum_length
    ):
    aux_routeset = deepcopy(routeset)
    repaired_routeset = []
    while len(touched_access_points) < network_size and aux_routeset != []:
        chosen_route = choice(aux_routeset)
        aux_routeset.remove(chosen_route)
        if len(chosen_route) < maximum_length:
            # add possible unused access points to either ends
            unused_access_points = all_access_points - touched_access_points
            for _ in range(len(unused_access_points)):
                terminal1 = chosen_route[0]
                chosen_route, touched_access_points = add_unused_access_points(terminal1, 0, unused_access_points)
                unused_access_points = all_access_points - touched_access_points
                terminal2 = chosen_route[-1]
                chosen_route, touched_access_points = add_unused_access_points(terminal2, -1, unused_access_points)
        repaired_routeset.append(chosen_route)
    if len(touched_access_points) == network_size:
        return repaired_routeset
    return False


class InitialPopulationGenerator:
    def __init__(self, transport_network):
        self.routeset_size = int(input("Choose a size for the routesets to be generated: "))
        self.minimum_length = int(input("Choose a minimum length for the routes to be generated: "))
        self.maximum_length = int(input("Choose a maximum length for the routes to be generated: "))
        self.population_size = int(input("Choose the population size: "))
        self.population = self.generate_initial_population(self.population_size, transport_network)

    def generate_initial_population(self, population_size, transport_network):
        print("Initial population is being generated...")
        population = set()
        while len(population) < population_size:
            routeset = generate_routeset(transport_network)
            population.add(routeset)
        print("Initial population has been successfully generated.")
        return population
        

    def generate_routeset(self, transport_network):
        print("Generating routeset...")
        network_size = len(transport_network.graph)

        routes = [] 

        touched_access_points = []
        for count in range(0, self.routeset_size):
            desired_length = randint(self.minimum_length, self.maximum_length)
            # if it's the first route of the routeset
            if count == 0:
                # pick a random access point to be the seed
                selected_access_point = randint(0, network_size - 1)
                routes[0][0] = selected_access_point
            else:
                # seed the next route, ensuring connectivity
                selected_access_point = choice(touched_access_points)
                touched_access_points.append(selected_access_point)
                routes[count][0] = selected_access_point
            route_length = 1

            times_reversed = 0
            while(route_length < desired_length and times_reversed <= 1):
                neighborhood = set(selected_access_point.get_neighborhood())
                all_access_points = set(transport_network.graph.get_access_points_id())
                current_route_access_points = set(routes[count])
                absent_access_points = all_access_points - current_route_access_points
                unused_access_points = list(neighborhood - absent_access_points)
                if unused_access_points != []:
                    route_length += 1
                    next_access_point = choice(unused_access_points)
                    routes[count][route_length] = next_access_point
                    selected_access_point = next_access_point
                    touched_access_points = list(set(touched_access_points).add(next_access_point))
                else:
                    routes[count].reverse()
                    selected_access_point = routes[count][route_length - 1]
                    times_reversed += 1

        if len(touched_access_points) < network_size:
            print("Starting repair of routeset...")
            touched_access_points = set(touched_access_points)
            repaired_routeset = repair(routes, all_access_points, touched_access_points, network_size, routeset_size, maximum_length, minimum_length)
            if repaired_routeset:
                print("Routeset has been successfully repaired. Adding it to the population...")
                return repaired_routeset
            else:
                return "Routeset is infeasible. It will be discarded from the population."