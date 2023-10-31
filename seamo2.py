import initial_population_generator as ipg
import parser
from random import choice, getrandbits, randrange
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt


class SEAMO2:
    def __init__(self):
        self.transport_network = parser.TransportNetwork("MandlTravelTimes.txt")
        self.demand_matrix = parser.DemandMatrixParser("MandlDemand.txt")
        self.initial_population_generator = ipg.InitialPopulationGenerator(self.transport_network)

    def get_transfer_points(self, routeset):
        touched_points_n_times = {}
        transfer_points = set()
        for route in routeset:
            for access_point_id in route:
                if access_point_id not in touched_points_n_times.keys():
                    touched_points_n_times[access_point_id] = 1
                else:
                    touched_points_n_times[access_point_id] += 1
        for access_point_id in touched_points_n_times.keys():
            if touched_points_n_times[access_point_id] > 1:
                transfer_points.add(access_point_id)
        return transfer_points


    def compute_path_travel_time(self, path):
        path_links = list(zip(path, path[1:]))
        path_travel_time = 0
        for path_link in path_links:
            origin_access_point = self.transport_network.graph[path_link[0]]
            destination_access_point = path_link[1]
            for access_point_link in origin_access_point.links:
                if access_point_link.destination.id == destination_access_point:
                    path_travel_time += access_point_link.travel_time
        return path_travel_time

    def find_second_path(
        self,
        routes_with_destination_aux,
        destination_id,
        chosen_transfer_point,
        chosen_second_route
        ):
        chosen_transfer_point_index_second_route = chosen_second_route.index(
            chosen_transfer_point
        )
        destination_id_index_second_route = chosen_second_route.index(
            destination_id
        )
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
        return second_path, routes_with_destination_aux

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
        if route in routes_with_destination_aux:
            routes_with_destination_aux.remove(route)
        origin_destination_transfer_points_aux = list(origin_destination_transfer_points_aux)
        while len(origin_destination_transfer_points_aux) != 0:
            chosen_transfer_point = choice(origin_destination_transfer_points_aux)
            origin_destination_transfer_points_aux.remove(chosen_transfer_point)
            if chosen_transfer_point not in route:
                continue
            chosen_transfer_point_index = route.index(chosen_transfer_point)
            if origin_id_index < chosen_transfer_point_index:
                while len(routes_with_destination_aux) != 0:
                    chosen_second_route = choice(routes_with_destination_aux)
                    routes_with_destination_aux.remove(chosen_second_route)
                    if chosen_transfer_point not in chosen_second_route:
                        continue
                    path = route[origin_id_index:chosen_transfer_point_index + 1]
                    second_path, routes_with_destination_aux = self.find_second_path(
                        routes_with_destination_aux,
                        destination_id,
                        chosen_transfer_point,
                        chosen_second_route
                    )
                    path = path + second_path[1:]
                    path_travel_time = self.compute_path_travel_time(path) + 5
                    if path_travel_time < shortest_path_travel_time:
                        shortest_path_travel_time = path_travel_time
                routes_with_destination_aux = routes_with_destination                            
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
                    second_path, routes_with_destination_aux = self.find_second_path(
                        routes_with_destination_aux,
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
        routes_with_destination_aux = deepcopy(routes_with_destination)
        if origin_id in route:
            origin_id_index = route.index(origin_id)
            transfer_points_from_origin_aux = list(transfer_points_from_origin)
            while len(transfer_points_from_origin_aux) != 0:
                chosen_transfer_point_from_origin = choice(transfer_points_from_origin_aux)
                transfer_points_from_origin_aux.remove(chosen_transfer_point_from_origin)
                if chosen_transfer_point_from_origin not in route:
                    continue
                chosen_transfer_point_from_origin_index = route.index(chosen_transfer_point_from_origin)
                if origin_id_index < chosen_transfer_point_from_origin_index:
                    first_path = route[origin_id_index:chosen_transfer_point_from_origin_index + 1]
                elif origin_id_index > chosen_transfer_point_from_origin_index:
                    first_path = route[chosen_transfer_point_from_origin_index:origin_id_index + 1]
                    
                    first_path = list(first_path)
                    first_path.reverse()
                    first_path = tuple(first_path)
                transfer_points_to_destination_aux = list(transfer_points_to_destination)
                while len(transfer_points_to_destination_aux) != 0:
                    chosen_transfer_point_to_destination = choice(transfer_points_to_destination_aux)
                    transfer_points_to_destination_aux.remove(chosen_transfer_point_to_destination)
                    if route in routes_with_destination_aux:
                        routes_with_destination_aux.remove(route)
                    for second_route in routes_with_destination_aux:
                        if chosen_transfer_point_to_destination not in second_route:
                            continue
                        chosen_transfer_point_to_destination_index = second_route.index(chosen_transfer_point_to_destination)
                        destination_id_index = second_route.index(destination_id)
                        if destination_id_index > chosen_transfer_point_to_destination_index:
                            second_path = second_route[chosen_transfer_point_to_destination_index:destination_id_index + 1]
                        elif destination_id_index < chosen_transfer_point_to_destination_index:
                            second_path = second_route[destination_id_index: chosen_transfer_point_to_destination_index + 1]
                            second_path = list(second_path)
                            second_path.reverse()
                            second_path = tuple(second_path)
                        routeset_aux = deepcopy(routeset)
                        routeset_aux.remove(route)
                        routeset_aux.remove(second_route)
                        for third_route in routeset_aux:
                            if (
                                chosen_transfer_point_from_origin not in third_route
                                or
                                chosen_transfer_point_to_destination not in third_route
                            ):
                                continue
                            chosen_transfer_point_from_origin_index_third_route = third_route.index(
                                chosen_transfer_point_from_origin
                            )
                            chosen_transfer_point_to_destination_index_third_route = third_route.index(
                                chosen_transfer_point_to_destination
                            )
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
                            path = first_path + third_path[1:] + second_path[1:]
                            path_travel_time = self.compute_path_travel_time(path)
                            if path_travel_time < shortest_path_travel_time:
                                shortest_path_travel_time = path_travel_time
        return shortest_path_travel_time                                            

    def get_shortest_path_travel_time(self, routeset, origin_id, destination_id):
        shortest_path_travel_time = self.transport_network.worst_path_travel_time
        routeset_transfer_points = self.get_transfer_points(routeset)
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
        for route in routeset:
            origin_destination_transfer_points_aux = deepcopy(origin_destination_transfer_points)
            # Path without transfers
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
            # Path with one transfer
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
            # Path with two transfers
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

    def calculate_passenger_cost(self, routeset_size, routeset, demand_matrix):
        numerator = 0
        for i in range(len(self.transport_network.graph)):
            for j in range(len(self.transport_network.graph)):
                shortest_path_travel_time_from_i_to_j = self.get_shortest_path_travel_time(routeset, i, j)
                partial_numerator = demand_matrix.demand_matrix[i][j] * shortest_path_travel_time_from_i_to_j
                numerator += partial_numerator
        denominator = 0
        for i in range(len(self.transport_network.graph)):
            for j in range(len(self.transport_network.graph)):
                denominator += demand_matrix.demand_matrix[i][j]
        passenger_cost = numerator / denominator
        return passenger_cost

    def calculate_operator_cost(self, routeset):
        operator_cost = 0
        for route in routeset:
            route_links = list(zip(route, route[1:]))
            for (i, j) in route_links:
                # possível melhora do tempo de execução usando hash
                for link in self.transport_network.graph[i].links:
                    if link.destination.id == j:
                        operator_cost += link.travel_time
        return operator_cost


    def crossover(self, parent1, parent2):
        offspring = []
        parent1_copy = list(deepcopy(parent1))
        parent2_copy = list(deepcopy(parent2))
        seed = choice(parent1_copy)
        parent1_copy.remove(seed)
        offspring.append(seed)
        first_parent = True
        while len(offspring) < len(parent1):
            if first_parent:
                chosen_parent = parent2_copy
            else:
                chosen_parent = parent1_copy
            potential_routes = []
            for route in chosen_parent:
                seed = set(seed)
                if not seed.isdisjoint(set(route)):
                    potential_routes.append(route)
            next_route = []
            smallest_intersection = len(self.transport_network.graph)
            for route in potential_routes:
                intersection = seed.intersection(set(route))
                if len(intersection) < smallest_intersection:
                    smallest_intersection = len(intersection)
                    next_route = route
            chosen_parent.remove(next_route)
            offspring.append(next_route)
            seed = seed.union(set(next_route))
            first_parent = not first_parent
        offspring = set(offspring)
        return offspring

    
            
    def add_access_points(
        self,
        routeset,
        access_points_to_be_changed,
        absent_access_points,
        touched_access_points,
        all_access_points
        ):
        aux_routeset = list(deepcopy(routeset))
        modified_routeset = []
        added_access_points = 0
        while added_access_points < access_points_to_be_changed:
            if len(aux_routeset) == 0:
                break
            chosen_route = choice(aux_routeset)
            aux_routeset.remove(chosen_route)
            chosen_route = list(chosen_route)
            while (len(chosen_route)
                    <
                    self.initial_population_generator.maximum_length):
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
                if len(chosen_route) > length_before:
                    added_access_points += 1
                if added_access_points == access_points_to_be_changed:
                    break
            chosen_route = tuple(chosen_route)
            modified_routeset.append(chosen_route)
        if len(modified_routeset) < len(routeset):
            for route in aux_routeset:
                modified_routeset.append(route)
        modified_routeset = set(modified_routeset)    
        return modified_routeset

    def delete_access_points(self, routeset, access_points_to_be_changed):
        aux_routeset = list(deepcopy(routeset))
        modified_routeset = []
        deleted_access_points = 0
        access_points_occurences = {}
        for route in routeset:
            for access_point_id in route:
                if access_point_id not in access_points_occurences.keys():
                    access_points_occurences[access_point_id] = 1
                else:
                    access_points_occurences[access_point_id] += 1
        while deleted_access_points < access_points_to_be_changed:
            if len(aux_routeset) == 0:
                break
            chosen_route = choice(aux_routeset)
            aux_routeset.remove(chosen_route)
            chosen_route = list(chosen_route)
            while (len(chosen_route)
                    >
                    self.initial_population_generator.minimum_length
                ):
                terminal1_id = chosen_route[0]
                terminal2_id = chosen_route[-1]
                if (access_points_occurences[terminal1_id] == 1
                    and
                    access_points_occurences[terminal2_id] == 1):
                    break
                terminal_id = choice([terminal1_id, terminal2_id])
                if access_points_occurences[terminal_id] > 1:
                    length_before = len(chosen_route)
                    chosen_route.remove(terminal_id)
                    access_points_occurences[terminal_id] -= 1
                    if len(chosen_route) < length_before:
                        deleted_access_points += 1
                if deleted_access_points == access_points_to_be_changed:
                    break
            chosen_route = tuple(chosen_route)
            modified_routeset.append(chosen_route)
        if len(modified_routeset) < len(routeset):
            for route in aux_routeset:
                modified_routeset.append(route)
        modified_routeset = set(modified_routeset)
        return modified_routeset


    def mutation(
        self,
        individual,
        absent_access_points,
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
                absent_access_points,
                touched_access_points,
                all_access_points,
                )
        else:
            individual = self.delete_access_points(
                individual,
                access_points_to_be_changed
                )
        return individual

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

seamo2 = SEAMO2()

adjacencies_list = seamo2.transport_network.build_adjacencies_list()

graph = nx.Graph(adjacencies_list)
pos = {
    0:(1, 9),
    1:(3, 8),
    2:(4.5, 7.75),
    3:(2.75, 6.2),
    4:(0.8, 6.6),
    5:(4.6, 6),
    6:(7, 4.5),
    7:(5.5, 5),
    8:(8.5, 6.8),
    9:(5.8, 3.25),
    10:(3.8, 2.25),
    11:(1.3, 3.5),
    12:(5.25, 1),
    13:(6.7, 1.75),
    14:(6.75, 5.8)
}
nx.draw_networkx(graph, pos, with_labels=True)
plt.show()

(
    passenger_cost,
    operator_cost,
    best_routeset_so_far_passenger_cost,
    best_routeset_so_far_operator_cost
) = seamo2.evaluate_population()


print("BEFORE SEAMO2 IMPROVEMENT\n")
"""
for routeset_index, routeset in seamo2.initial_population_generator.population:
    print(f'Routeset {routeset_index}:\n')
    nodes = parser.get_access_points_id(seamo2.transport_network.graph)
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple']
    figure = 2 
    for j, route in enumerate(routeset):
        print(f'Route {j}: [', end='')
        route_nodes = []
        route_nodes_positions = {}
        for access_point_id in route:
            route_nodes.append(access_point_id)
            route_nodes_positions[access_point_id] = pos[access_point_id]
            if len(route) == 1:
                print(f'[{access_point_id}]')
            else:
                if access_point_id == route[-1]:
                    print(f'{access_point_id}]')
                else:
                    print(f'{access_point_id} -', end=' ')
        route_edges = list(zip(route_nodes, route_nodes[1:]))
        color = choice(colors)
        colors.remove(color)
        plt.figure(figure)
        nx.draw_networkx(graph, pos, with_labels=True)
        nx.draw_networkx_nodes(graph, route_nodes_positions, route_nodes, node_color=color)
        nx.draw_networkx_edges(graph, route_nodes_positions, route_edges, edge_color=color, width=2)        
        figure += 1
#    plt.show()                
    print()

    print("Passenger cost: {:.2f}\n".format(passenger_cost[routeset_index][2]))
    print("Operator cost: {:.2f}\n".format(operator_cost[routeset_index][2]))
"""    
print(f"Best routeset for passenger cost: Routeset {best_routeset_so_far_passenger_cost[0]}\n")
print(f"Best routeset for operator cost: Routeset {best_routeset_so_far_operator_cost[0]}\n")

population_before = deepcopy(seamo2.initial_population_generator.population)
generations = int(input("How many generations do you want? "))
for _ in range(generations):

    print(f"Best passenger cost: {best_routeset_so_far_passenger_cost[2]}")
    print(f"Best operator cost: {best_routeset_so_far_operator_cost[2]}")

    population_data = []
    passenger_cost_values = []
    operator_cost_values = []
    for routeset_index, routeset in seamo2.initial_population_generator.population.items():
        routeset_passenger_cost_value = passenger_cost[routeset_index]
        routeset_operator_cost_value = operator_cost[routeset_index]
        passenger_cost_values.append(routeset_passenger_cost_value)
        operator_cost_values.append(routeset_operator_cost_value)
        population_data.append((routeset_passenger_cost_value, routeset_operator_cost_value))
    plt.scatter(passenger_cost_values, operator_cost_values)
    #plt.plot(passenger_cost_values, operator_cost_values)
    plt.xlabel("Passenger cost")
    plt.ylabel("Operator cost")
    plt.show()


    aux_population = list(seamo2.initial_population_generator.population.keys())
    #TODO: For each individual in the population
    while :
        parent1_index = aux_population[0]
        parent1 = seamo2.initial_population_generator.population[parent1_index]
        aux_population.remove(parent1_index)
        parent2_index = choice(aux_population)
        parent2 = seamo2.initial_population_generator.population[parent2_index]
        aux_population.append(parent1_index)
        if parent1 != parent2:
            if (
                (parent1_index, parent2_index) not in mated_individuals
                or
                (parent2_index, parent1_index) not in mated_individuals
                ):
                mated_individuals.add((parent1_index, parent2_index))
                mated_individuals.add((parent2_index, parent1_index))
            else:
                continue
            offspring = seamo2.crossover(parent1, parent2)
            all_access_points = parser.get_access_points_id(seamo2.transport_network.graph)
            # get used access points on routeset
            touched_access_points = set()
            for route in offspring:
                touched_access_points = touched_access_points.union(set(route))
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
            # update used access points on routeset
            for route in offspring:
                touched_access_points = touched_access_points.union(set(route))
            # calculate absent access points from routeset
            absent_access_points = set(all_access_points) - touched_access_points
            offspring = seamo2.mutation(
                offspring,
                absent_access_points,
                touched_access_points,
                all_access_points
                )
            offspring_is_duplicate = False
            for routeset in seamo2.initial_population_generator.population.values():
                if offspring == routeset:
                    offspring_is_duplicate = True
                    break
            if offspring_is_duplicate:
                continue                    
            offspring_passenger_cost = seamo2.calculate_passenger_cost(
                seamo2.initial_population_generator.routeset_size,
                offspring,
                seamo2.demand_matrix
                )
            offspring_operator_cost = seamo2.calculate_operator_cost(offspring)
            parent1_passenger_cost = passenger_cost[parent1_index]
            parent1_operator_cost = operator_cost[parent1_index] 

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
            parent2_passenger_cost = passenger_cost[parent2_index]
            parent2_operator_cost = operator_cost[parent2_index]
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
            if (offspring_passenger_cost < best_routeset_so_far_passenger_cost[2]
                and
                offspring_operator_cost < operator_cost[best_routeset_so_far_passenger_cost[0]]):
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
            if (offspring_operator_cost < best_routeset_so_far_operator_cost[2]
                and
                offspring_passenger_cost < passenger_cost[best_routeset_so_far_operator_cost[0]]
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
            if offspring_passenger_cost < best_routeset_so_far_passenger_cost[2]:
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
            if offspring_operator_cost < best_routeset_so_far_operator_cost[2]:
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

print("AFTER SEAMO2 IMPROVEMENT\n")
"""
for routeset_index, routeset in seamo2.initial_population_generator.population:
    print(f'Routeset {routeset_index}:\n')
    nodes = parser.get_access_points_id(seamo2.transport_network.graph)
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple']
    figure = 2 
    for j, route in enumerate(routeset):
        print(f'Route {j}: [', end='')
        route_nodes = []
        route_nodes_positions = {}
        for access_point_id in route:
            route_nodes.append(access_point_id)
            route_nodes_positions[access_point_id] = pos[access_point_id]
            if len(route) == 1:
                print(f'[{access_point_id}]')
            else:
                if access_point_id == route[-1]:
                    print(f'{access_point_id}]')
                else:
                    print(f'{access_point_id} -', end=' ')
        route_edges = list(zip(route_nodes, route_nodes[1:]))
        color = choice(colors)
        colors.remove(color)
        plt.figure(figure)
        nx.draw_networkx(graph, pos, with_labels=True)
        nx.draw_networkx_nodes(graph, route_nodes_positions, route_nodes, node_color=color)
        nx.draw_networkx_edges(graph, route_nodes_positions, route_edges, edge_color=color, width=2)        
        figure += 1
#    plt.show()                
    print()

    print("Passenger cost: {:.2f}\n".format(passenger_cost[routeset_index][2]))
    print("Operator cost: {:.2f}\n".format(operator_cost[routeset_index][2]))
    """
print(f"Best routeset for passenger cost: Routeset {best_routeset_so_far_passenger_cost[0]}\n")
print(f"Best routeset for operator cost: Routeset {best_routeset_so_far_operator_cost[0]}\n")
