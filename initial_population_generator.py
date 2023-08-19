import parser
from random import randint, choice


class InitialPopulationGenerator:
    def __init__(self):
        self.routeset_size = int(input("Choose a size for the routesets to be generated: "))
        self.minimum_length = int(input("Choose a minimum length for the routes to be generated: "))
        self.maximum_length = int(input("Choose a maximum length for the routes to be generated: "))
        self.population_size = int(input("Choose the population size: "))
        self.generate_initial_population()

    def generate_initial_population(self):
        generate_routeset()

    def generate_routeset(self):
        transport_network = TransportNetwork("MandlTravelTimes.txt")
        network_size = len(transport_network.graph)

        routes = [] 

        touched_access_points = []
        for count in range(0, self.routeset_size):
            current_length = randint(self.minimum_length, self.maximum_length)
            if count == 0:
                selected_access_point = randint(0, network_size - 1)
                routes[0][0] = selected_access_point
            else:
                selected_access_point = choice(touched_access_points)
                touched_access_points.append(selected_access_point)
                routes[count][0] = selected_access_point
            route_length = 1
