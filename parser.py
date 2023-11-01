def get_access_points_id(list):
        access_points_id = []
        for access_point in list:
            access_points_id.append(access_point.id)
        return access_points_id

class Link:
    def __init__(self, destination, travel_time):
        self.destination = destination
        self.travel_time = travel_time
        self.demand = 0


class AccessPoint:
    def __init__(self, id):
        self.id = id
        self.links = []

    def add_link(self, link: Link):
        self.links.append(link)

    def get_neighborhood(self):
        neighborhood = []
        for neighbor in self.links:
            neighborhood.append(neighbor.destination)
        return neighborhood

class CoordsParser:
    def __init__(self, coords_file):
        self.coords = self.read(coords_file)

    def read(self, coords_file):
        coords_file = open(coords_file, 'r')
        parsed_coords = {}

        line_index = 0
        for line in coords_file:
            line = line.split()
            if len(line) == 1:
                continue
            coord = []
            for value in line:
                value = float(value)
                coord.append(value)
            coord = tuple(coord)
            parsed_coords[line_index] = coord
            line_index += 1
        return parsed_coords


class DemandMatrixParser:
    def __init__(self, demand_matrix):
        self.demand_matrix = self.read(demand_matrix)

    def read(self, demand_matrix):
        demand_matrix = open(demand_matrix, 'r')
        parsed_demand = []

        for line in demand_matrix:
            line = line.lstrip()
            line = line.rstrip()
            if line == '':
                continue
            line = line.split()
            int_line = []
            for value in line:
                value = int(value)
                int_line.append(value)
            parsed_demand.append(int_line)
        return parsed_demand


class TransportNetwork:
    def __init__(self, travel_time_matrix):
        self.graph = []
        self.read(travel_time_matrix)


    def get_worst_path_travel_time(self):
        highest_travel_time = 0
        for access_point in self.graph:
            for link in access_point.links:
                if highest_travel_time < link.travel_time:
                    highest_travel_time = link.travel_time
        return highest_travel_time * len(self.graph)

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
                self.graph[origin_id].add_link(Link(AccessPoint(destination_id), int(travel_time)))

            '''
            print(f'Links from {self.graph[origin_id].id} to:\n')
            for link in self.graph[origin_id].links:
                print(f'{link.destination} with travel time = {link.travel_time}\n')
            '''
            origin_id += 1

        self.worst_path_travel_time = self.get_worst_path_travel_time()

    def get_by_id(self, access_point_id):
        for access_point in self.graph:
            if access_point.id == access_point_id:
                return access_point

    def build_adjacencies_list(self):
        adjacencies_list = {}
        for access_point in self.graph:
            if access_point.id not in adjacencies_list:
                access_point_adjacencies = get_access_points_id(access_point.get_neighborhood())
                adjacencies_list[access_point.id] = access_point_adjacencies
        return adjacencies_list
    