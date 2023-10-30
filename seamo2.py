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
            second_path.reverse()
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
                    path.reverse()
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
        route,
        routeset,
        transfer_points_from_origin,
        transfer_points_to_destination,
        routes_with_destination
        ):
        routes_with_destination_aux = deepcopy(routes_with_destination)
        if origin_id in route:
            origin_id_index = route.index(origin_id)
            transfer_points_from_origin_aux = transfer_points_from_origin
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
                    first_path.reverse()
                transfer_points_to_destination_aux = transfer_points_to_destination
                while len(transfer_points_to_destination_aux) != 0:
                    chosen_transfer_point_to_destination = choice(transfer_points_to_destination_aux)
                    transfer_points_to_destination_aux.remove(chosen_transfer_point_to_destination)
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
                            second_path.reverse()
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
                                third_path.reverse()
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
                shortest_path_travel_time = get_two_transfers_path_travel_time(
                    origin_id,
                    route,
                    routeset,
                    transfer_points_from_origin,
                    transfer_points_to_destination,
                    routes_with_destination
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

    # TODO: NEED TO FIND AND FIX BUG
    def crossover(self, parent1, parent2):
        offspring = []
        parent1_copy = deepcopy(parent1)
        parent2_copy = deepcopy(parent2)
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
        return offspring

    
            
    def add_access_points(
        self,
        routeset,
        access_points_to_be_changed,
        absent_access_points,
        touched_access_points,
        all_access_points
        ):
        aux_routeset = deepcopy(routeset)
        modified_routeset = []
        added_access_points = 0
        while added_access_points < access_points_to_be_changed:
            chosen_route = choice(aux_routeset)
            aux_routeset.remove(chosen_route)
            route_cannot_be_modified_anymore = False
            while len(touched_access_points) < len(all_access_points):
                if route_cannot_be_modified_anymore:
                    break
                terminal1 = chosen_route[0]
                access_points_touched_before = deepcopy(touched_access_points)
                if len(chosen_route) < self.initial_population_generator.maximum_length:
                    chosen_route, touched_access_points = ipg.add_unused_access_points(
                        chosen_route,
                        terminal1,
                        0,
                        absent_access_points,
                        touched_access_points
                        )
                if len(touched_access_points) == len(access_points_touched_before) + 1:
                    added_access_points += 1
                    route_cannot_be_modified_anymore = False
                else:
                    route_cannot_be_modified_anymore = True
                terminal2 = chosen_route[-1]
                access_points_touched_before = deepcopy(touched_access_points)
                if len(chosen_route) < self.initial_population_generator.maximum_length:
                    chosen_route, touched_access_points = ipg.add_unused_access_points(
                        chosen_route,
                        terminal2,
                        -1,
                        absent_access_points,
                        touched_access_points
                        )
                if len(touched_access_points) == len(access_points_touched_before) + 1:
                    added_access_points += 1
                    route_cannot_be_modified_anymore = False
                else:
                    route_cannot_be_modified_anymore = True
            modified_routeset.append(chosen_route)
        return modified_routeset

    def delete_access_point(
        self,
        chosen_route,
        terminal,
        position,
        aux_routeset
        ):
        for route in aux_routeset:
            if terminal in route:
                chosen_route.remove(terminal)
                break
        unfeasible = False
        chosen_route_access_points = set(chosen_route)
        for route in aux_routeset:
            route_access_points = set(route)
            if chosen_route.isdisjoint(route_access_points):
                unfeasible = True
            else:
                unfeasible = False
        if unfeasible:
            chosen_route.insert(terminal, position)
        return chosen_route, unfeasible

    def delete_access_points(self, routeset, access_points_to_be_changed):
        aux_routeset = deepcopy(routeset)
        modified_routeset = []
        deleted_access_points = 0
        while deleted_access_points < access_points_to_be_changed:
            chosen_route = choice(aux_routeset)
            chosen_route_index = aux_routeset.index(chosen_route)
            aux_routeset.remove(chosen_route)
            aux_routeset2 = deepcopy(aux_routeset)
            if previous_route is not None:
                aux_routeset2.insert(previous_route, previous_route_index)
            route_cannot_be_modified_anymore = False
            while not route_cannot_be_modified_anymore:
                terminal1 = chosen_route[0]
                length_before = len(chosen_route)
                if len(chosen_route) > self.initial_population_generator.minimum_length:
                    chosen_route, route_cannot_be_modified_anymore = self.delete_access_point(
                        chosen_route,
                        terminal1,
                        0,
                        aux_routeset2)
                if len(chosen_route) < length_before:
                    deleted_access_points += 1
                terminal2 = chosen_route[-1]
                length_before = len(chosen_route)
                if len(chosen_route) > self.initial_population_generator.minimum_length:
                    chosen_route, route_cannot_be_modified_anymore = self.delete_access_point(
                        chosen_route,
                        terminal2,
                        -1,
                        aux_routeset2)
                if len(chosen_route) < length_before:
                    deleted_access_points += 1
            previous_route = chosen_route
            previous_route_index = chosen_route_index
            modified_routeset.append(chosen_route)
        return modified_routeset

    def mutation(self, individual, absent_access_points, touched_access_points):
        access_points_to_be_changed = randrange(
            1,
            self.initial_population_generator.routeset_size * (
                self.initial_population_generator.maximum_length/2
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
        objective1,
        parent_objective1,
        objective2,
        parent_objective2,
        offspring,
        offspring_objective1,
        offspring_objective2
        ):
        self.initial_population_generator.population.remove(parent)
        objective1.remove([parent, parent_objective1])
        objective2.remove([parent, parent_objective2])
        self.initial_population_generator.population.add(offspring)
        objective1.append([offspring, offspring_objective1])
        objective2.append([offspring, offspring_objective2])
        
    def replace_random_parent(
        self,
        passenger_cost,
        operator_cost,
        parent1,
        parent2,
        parent1_passenger_cost,
        parent1_operator_cost,
        parent2_passenger_cost,
        parent2_operator_cost,
        offspring,
        offspring_passenger_cost,
        offspring_operator_cost
        ):
        chosen_parent = choice([parent1, parent2])
        if chosen_parent == parent1:
            parent_passenger_cost = parent1_passenger_cost
            parent_operator_cost = parent1_operator_cost
        elif chosen_parent == parent2:
            parent_passenger_cost = parent2_passenger_cost
            parent_operator_cost = parent2_operator_cost
        seamo2.replace_parents_with_offspring(
            chosen_parent,
            passenger_cost,
            parent_passenger_cost,
            operator_cost,
            parent_operator_cost,
            offspring,
            offspring_passenger_cost,
            offspring_operator_cost
            )

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


passenger_cost = []
best_routeset_so_far_passenger_cost = []
operator_cost = []
best_routeset_so_far_operator_cost = []
for (routeset_id, routeset) in enumerate(seamo2.initial_population_generator.population):
    routeset_passenger_cost = seamo2.calculate_passenger_cost(
            seamo2.initial_population_generator.routeset_size,
            routeset,
            seamo2.demand_matrix
        )
    passenger_cost.append([routeset_id, routeset, routeset_passenger_cost])
    
    routeset_operator_cost = seamo2.calculate_operator_cost(routeset)
    operator_cost.append([routeset_id, routeset, routeset_operator_cost])

lowest_passenger_cost = passenger_cost[0][2]
for routeset in passenger_cost:
    if routeset[2] < lowest_passenger_cost:
        lowest_passenger_cost = routeset[2]
for routeset in passenger_cost:
    if routeset[2] == lowest_passenger_cost:
        best_routeset_so_far_passenger_cost = routeset

lowest_operator_cost = operator_cost[0][2]
for routeset in operator_cost:
    if routeset[2] < lowest_operator_cost:
        lowest_operator_cost = routeset[2]
for routeset in operator_cost:
    if routeset[2] == lowest_operator_cost:
        best_routeset_so_far_operator_cost = routeset

'''
generations = int(input("How many generations do you want? "))
for _ in range(generations):
    for parent1 in seamo2.initial_population_generator.population:
        parent2 = choice(seamo2.initial_population_generator.population)
        if parent1 != parent2:
            offspring = seamo2.crossover(parent1, parent2)
            all_access_points = parser.get_access_points_id(seamo2.transport_network.graph)
            # get used access points on routeset
            touched_access_points = set()
            for route in offspring:
                touched_access_points.union(set(route))
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
                touched_access_points.union(set(route))
            # calculate absent access points from routeset
            absent_access_points = all_access_points - touched_access_points
            offspring = seamo2.mutation(
                offspring,
                absent_access_points,
                touched_access_points,
                all_access_points
                )
            if offspring in seamo2.initial_population_generator.population:
                continue
            offspring_passenger_cost = seamo2.calculate_passenger_cost(
                seamo2.initial_population_generator.routeset_size,
                offspring,
                seamo2.demand_matrix
                )
            offspring_operator_cost = seamo2.calculate_operator_cost(offspring)
            parent1_passenger_cost = seamo2.calculate_passenger_cost(
                seamo2.initial_population_generator.routeset_size,
                parent1,
                seamo2.demand_matrix
            )
            parent1_operator_cost = seamo2.calculate_operator_cost(parent1)
            if offspring_passenger_cost < parent1_passenger_cost and offspring_operator_cost < parent1_operator_cost:
                seamo2.replace_parents_with_offspring(
                    parent1,
                    passenger_cost,
                    parent1_passenger_cost,
                    operator_cost,
                    parent1_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )
                continue
            parent2_passenger_cost = seamo2.calculate_passenger_cost(
                seamo2.initial_population_generator.routeset_size,
                parent2,
                seamo2.demand_matrix
            )
            parent2_operator_cost = seamo2.calculate_operator_cost(parent2)
            if offspring_passenger_cost < parent2_passenger_cost and offspring_operator_cost < parent2_operator_cost:
                seamo2.replace_parents_with_offspring(
                    parent2,
                    passenger_cost,
                    parent2_passenger_cost,
                    operator_cost,
                    parent2_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )
                continue
            if (offspring_passenger_cost < best_routeset_so_far_passenger_cost[1]
                and
                offspring_operator_cost < calculate_operator_cost(best_routeset_so_far_passenger_cost[0])):
                best_routeset_so_far_passenger_cost = [offspring, offspring_passenger_cost]
                seamo2.replace_random_parent(
                    passenger_cost,
                    operator_cost,
                    parent1,
                    parent2,
                    parent1_passenger_cost,
                    parent1_operator_cost,
                    parent2_passenger_cost,
                    parent2_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )                    
                continue
            if (offspring_operator_cost < best_routeset_so_far_operator_cost[1]
                and
                offspring_passenger_cost < calculate_passenger_cost(best_routeset_so_far_operator_cost[0])):
                best_routeset_so_far_operator_cost = [offspring, offspring_operator_cost]
                seamo2.replace_random_parent(
                    passenger_cost,
                    operator_cost,
                    parent1,
                    parent2,
                    parent1_passenger_cost,
                    parent1_operator_cost,
                    parent2_passenger_cost,
                    parent2_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )
                continue
            if offspring_passenger_cost < best_routeset_so_far_passenger_cost[1]:
                best_routeset_so_far_passenger_cost = [offspring, offspring_passenger_cost]
                seamo2.replace_random_parent(
                    passenger_cost,
                    operator_cost,
                    parent1,
                    parent2,
                    parent1_passenger_cost,
                    parent1_operator_cost,
                    parent2_passenger_cost,
                    parent2_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )
                continue
            if offspring_operator_cost < best_routeset_so_far_operator_cost[1]:
                best_routeset_so_far_operator_cost = [offspring, offspring_operator_cost]
                seamo2.replace_random_parent(
                    passenger_cost,
                    operator_cost,
                    parent1,
                    parent2,
                    parent1_passenger_cost,
                    parent1_operator_cost,
                    parent2_passenger_cost,
                    parent2_operator_cost,
                    offspring,
                    offspring_passenger_cost,
                    offspring_operator_cost
                    )
                continue        
            if (offspring_passenger_cost == parent1_passenger_cost == parent2_passenger_cost
                and
                offspring_operator_cost == parent1_operator_cost == parent2_operator_cost):
                for routeset in seamo2.initial_population_generator.population:
                    routeset_passenger_cost = passenger_cost[routeset]
                    routeset_operator_cost = operator_cost[routeset]
                    if (offspring_passenger_cost < routeset_passenger_cost
                        and
                        offspring_operator_cost < routeset_operator_cost):
                        seamo2.initial_population_generator.population.remove(routeset)
                        seamo2.initial_population_generator.population.add(offspring)
                        passenger_cost.remove([routeset, routeset_passenger_cost])
                        passenger_cost.append([offspring, offspring_passenger_cost])
                        operator_cost.remove([routeset, routeset_operator_cost])
                        operator_cost.append([offspring, offspring_operator_cost])
                        continue
            else:
                continue
'''
for i, routeset in enumerate(seamo2.initial_population_generator.population):
    print(f'Routeset {i}:\n')
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
    plt.show()                
    print()

    print("Passenger cost: {:.2f}\n".format(passenger_cost[i][2]))
    print("Operator cost: {:.2f}\n".format(operator_cost[i][2]))
    
print(f"Best routeset for passenger cost: Routeset {best_routeset_so_far_passenger_cost[0]}\n")
print(f"Best routeset for operator cost: Routeset {best_routeset_so_far_operator_cost[0]}\n")
