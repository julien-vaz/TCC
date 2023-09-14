import initial_population_generator as ipg
import parser
from random import choice
from copy import deepcopy


class SEAMO2:
    def __init__(self):
        self.transport_network = parser.TransportNetwork("MandlTravelTimes.txt")
        self.demand_matrix = parser.DemandMatrixParser("MandlDemand.txt")
        self.initial_population_generator = ipg.InitialPopulationGenerator(transport_network)

    def get_shortest_path_travel_time(self, routeset, origin_id, destination_id):
        shortest_path_travel_time = "Infinite"
        for route in routeset:
            if origin_id in route and destination_id in route:
                shortest_path_travel_time = 0
                origin_id_index = route.index(origin_id)
                destination_id_index = route.index(destination_id)
                path = route[origin_id_index:destination_id_index + 1]
                path_links = list(zip(path, path[1:]))
                path_travel_time = 0
                for path_link in path_links:
                    origin_access_point = self.transport_network.graph[path_link[0]]
                    destination_access_point = path_link[1]
                    for access_point_link in origin_access_point.links:
                        if access_point_link[0] == destination_access_point:
                            path_travel_time += access_point_link[1]
                if path_travel_time < shortest_path_travel_time:
                    shortest_path_travel_time = path_travel_time
        return shortest_path_travel_time

    def calculate_passenger_cost(self, routeset_size, routeset, demand_matrix):
        numerator = 0
        for i in range(len(routeset_size)):
            for j in range(len(routeset_size)):
                shortest_path_travel_time_from_i_to_j = self.get_shortest_path_travel_time(routeset, i, j)
                partial_numerator = demand_matrix[i][j] * shortest_path_travel_time_from_i_to_j
                numerator += partial_numerator
        denominator = 0
        for i in range(len(routeset_size)):
            for j in range(len(routeset_size)):
                denominator += demand_matrix[i][j]
        passenger_cost = numerator / denominator
        return passenger_cost

    def calculate_operator_cost(self, routeset):
        operator_cost = 0
        for route in routeset:
            for i, j in route:
                for link in self.transport_network.graph[i].links:
                    if link[0] == j:
                        operator_cost += link[1]

    def crossover(self, parent1, parent2):
        offspring = []
        parent1_copy = deepcopy(parent1)
        parent2_copy = deepcopy(parent2)
        seed = set(choice(parent1_copy))
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
                if not seed.isdisjoint(set(route)):
                    potential_routes.append(route)
            next_route = []
            smallest_intersection = len(self.transport_network.graph)
            for route in potential_routes:
                intersection = seed.intersection(set(route))
                if intersection < smallest_intersection:
                    smallest_intersection = intersection
                    next_route = route
                    chosen_parent.remove(next_route)
                    offspring.append(next_route)
            seed.add(set(next_route))
            first_parent = not first_parent
        return offspring
            


seamo2 = SEAMO2()

passenger_cost = []
best_routeset_so_far_passenger_cost = []
operator_cost = []
best_routeset_so_far_operator_cost = []
for routeset in seamo2.initial_population_generator.population:
    routeset_passenger_cost = seamo2.calculate_passenger_cost(
            seamo2.initial_population_generator.routeset_size,
            routeset,
            seamo2.demand_matrix
        )
    passenger_cost.append(routeset_passenger_cost)
    if routeset_passenger_cost == min(passenger_cost):
        best_routeset_so_far_passenger_cost = routeset

    routeset_operator_cost = seamo2.calculate_operator_cost(
        routeset
    )
    operator_cost.append(routeset_operator_cost)
    if routeset_operator_cost == min(operator_cost):
        best_routeset_so_far_operator_cost = routeset

generations = int(input("How many generations do you want? "))
for _ in range(generations):
    for parent1 in seamo2.initial_population_generator.population:
        parent2 = random.choice(seamo2.initial_population_generator)
        if parent1 != parent2:
            offspring = crossover(parent1, parent2)