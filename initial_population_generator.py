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
        #TODO
        generate_routeset()

    def generate_routeset(self):
        transport_network = TransportNetwork("MandlTravelTimes.txt")
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
                    route[count][route_length] = next_access_point
                    selected_access_point = next_access_point
                    touched_access_points = set(touched_access_points).add(next_access_point)
                else:
                    
                    selected_access_point = routes[]
                    times_reversed += 1