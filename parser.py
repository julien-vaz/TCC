class Link:
    def __init__(self, destination_id, travel_time):
        self.destination_id = destination_id
        self.travel_time = travel_time
        self.demand = 0
    
    def set_demand(self, demand):
        self.demand = demand


class AccessPoint:
    def __init__(self, id):
        self.id = id
        self.links = []

    def add_link(self, link: Link):
        self.links.append(link)

    def get_neighborhood(self):
        neighborhood = []
        for neighbor in self.links:
            neighborhood.append(neighbor.destination_id)
        return neighborhood


class TransportNetwork:
    def __init__(self, travel_time_matrix):
        self.graph = []
        self.read(travel_time_matrix)

    def read(self, travel_time_matrix):
        travel_time_matrix = open(travel_time_matrix, 'r')

        origin_id = 0
        for line in travel_time_matrix:
            if line == '\n':
                continue
            line = line[0:-1]
            aux = line.split()
            self.graph.append(AccessPoint(origin_id))
            
            for (destination_id, travel_time) in enumerate(aux):
                if travel_time == '0' or travel_time == 'Inf':
                    continue
                self.graph[origin_id].add_link(Link(destination_id, travel_time))

            print(f'Links from {self.graph[origin_id].id} to:\n')
            for link in self.graph[origin_id].links:
                print(f'{link.destination_id} with travel time = {link.travel_time}\n')

            origin_id += 1

    def get_access_points_id(self):
        access_points_id = []
        for access_point in self.graph:
            access_points_id.append(access_point.id)
        return access_points_id


mandl = TransportNetwork("MandlTravelTimes.txt")
