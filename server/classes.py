import random

generator_options = {
    "width":25,
    "height":25,
    "Birth_chance":60,
    "Death_limit":3,
    "Birth_limit":4,
    "Number_of_steps":3
}

class Cave_Generator:
    def __init__(self, options):
        self.options = options

    def create_map(self):
        map = []
        
        for x in range(self.options["width"]):
            empty_list = []
            for y in range(self.options["height"]):
                empty_list.append(False)
            map.append(empty_list)
        
        for index_x, x in enumerate(map):
            for index_y, y in enumerate(map[index_x]):
                if self.options["Birth_chance"] < random.randint(0,100):
                    map[index_x][index_y] = True

        return map

    def count_alive_neighbours(self, x, y, oldMap):
        count = 0

        for i in range(3):
            for j in range(3):
                neighbour_x = (x-1) + i
                neighbour_y = (y-1) + j

                if i == 1 and j == 1:
                    pass
                elif neighbour_x < 0 or neighbour_y < 0 or neighbour_x >= self.options["width"] or neighbour_y >= self.options["height"]:    
                    count += 1
                elif oldMap[neighbour_x][neighbour_y]:
                    count += 1
        
        return count

    def do_simulation_step(self, oldMap):
        newMap = []

        for x in range(self.options["width"]):
            empty_list = []
            for y in range(self.options["height"]):
                empty_list.append(False)
            newMap.append(empty_list)

        for index_x, x in enumerate(oldMap):
            for index_y, y in enumerate(oldMap):
                nbs = self.count_alive_neighbours(index_x, index_y, oldMap)
                
                if oldMap[index_x][index_y]:
                    if nbs < self.options["Death_limit"]:
                        newMap[index_x][index_y] = False
                    else: 
                        newMap[index_x][index_y] = True
                else: 
                    if nbs > self.options["Birth_limit"]:
                        newMap[index_x][index_y] = True
                    else:
                        newMap[index_x][index_y] = False
        
        return newMap

    def generate_cave(self):
        map = self.create_map()

        for i in range(self.options["Number_of_steps"]):
            map = self.do_simulation_step(map)

        return map