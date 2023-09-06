import initial_population_generator as ipg
import parser


class SEAMO2:
    def __init__(self):
        self.transport_network = parser.TransportNetwork("MandlTravelTimes.txt")
        self.demand_matrix = parser.DemandMatrixParser("MandlDemand.txt")
        self.initial_population_generator = ipg.InitialPopulationGenerator(transport_network)

    def get_shortest_path(routeset, origin_id, destination_id):
        shortest_path_travel_time = 0
        for route in routeset:
            if origin_id in route and destination_id in route:
                for access_point_id in route:
                    pass


    def calculate_passenger_cost(routeset_size, routeset, demand_matrix):
        numerator = 0
        for i in range(len(routeset_size)):
            for j in range(len(routeset_size)):
                get_shortest_path(routeset, i, j)
                # partial_numerator = demand_matrix[i][j] * 

seamo2 = SEAMO2()

passenger_cost = []
operator_cost = []
for routeset in seamo2.initial_population_generator.population:
    seamo2.calculate_passenger_cost(seamo2.initial_population_generator.routeset_size, routeset, seamo2.demand_matrix)
