import initial_population_generator as ipg
import parser


class SEAMO2:
    def __init__(self):
        self.transport_network = parser.TransportNetwork("MandlTravelTimes.txt")
        self.demand_matrix = parser.DemandMatrixParser("MandlDemand.txt")
        self.initial_population_generator = ipg.InitialPopulationGenerator(transport_network)

    def get_shortest_path_travel_time(routeset, origin_id, destination_id):
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

    def calculate_passenger_cost(routeset_size, routeset, demand_matrix):
        numerator = 0
        for i in range(len(routeset_size)):
            for j in range(len(routeset_size)):
                shortest_path_travel_time_from_i_to_j = get_shortest_path_travel_time(routeset, i, j)
                partial_numerator = demand_matrix[i][j] * shortest_path_travel_time_from_i_to_j
                numerator += partial_numerator
        denominator = 0
        for i in range(len(routeset_size)):
            for j in range(len(routeset_size)):
                denominator += demand_matrix[i][j]
        passenger_cost = numerator / denominator
        return passenger_cost

    def calculate_operator_cost(routeset):
        operator_cost = 0
        for route in routeset:
            for i, j in route:
                for link in self.transport_network.graph[i].links:
                    if link[0] == j:
                        operator_cost += link[1]


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