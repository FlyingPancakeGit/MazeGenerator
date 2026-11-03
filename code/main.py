import pygame

import random


class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Maze:
    def __init__(self, size, start):
        # setup
        self.size = size
        self.wall_remove_count = int(self.size ** 2 / 20)
        self.destructible_wall_count = int(self.size ** 2 / 25)
        self.loot_crate_count = int(self.size ** 2 / 90)
        self.quicksand_count = int(self.size ** 2 / 25)
        self.maze = {}

        self.visited_list = []
        self.path_stack = []

        self.start_cell = start

    def generate_maze(self): # Fills out the dictionary representing the maze with walls.
        for x in range(self.size):
            for y in range(self.size):
                self.maze[(x, y)] = 'X' # Letter 'X' represents a wall tile.

    def generate_paths(self):
        current_cell = self.start_cell
        self.path_stack.append(current_cell)

        while self.path_stack:
            self.maze[current_cell] = 'S' # Letter 'S' represents a sand/path tile.
            self.visited_list.append(current_cell)
            neighbour_cell = self.check_neighbours(current_cell)

            if neighbour_cell:
                # By calculating the average co-ordinates of the current and neighbour tiles combined, the co-ordinates
                # of the tile in-between them (the wall tile) can be found.
                wall_cell = ((current_cell[0] + neighbour_cell[0]) / 2, (current_cell[1] + neighbour_cell[1]) / 2)
                self.maze[wall_cell] = 'S'
                self.path_stack.append(current_cell)
                current_cell = neighbour_cell
            elif self.path_stack:
                current_cell = self.path_stack.pop()

        for key, value in self.maze.items():
            # Ensures that the maze is surrounded by a wall, so that no players can escape.
            if key[0] == 0 or key[1] == 0 or key[0] == self.size - 1 or key[1] == self.size - 1:
                self.maze[key] = 'X'

    def check_neighbours(self, current_cell): # Checks the neighbouring cells to the current cell.
        offsets = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        while offsets:
            offset = random.choice(offsets)
            offsets.remove(offset)

            neighbour_cell = (current_cell[0] + offset[0], current_cell[1] + offset[1])
            if (
                0 <= neighbour_cell[0] <= self.size - 1 and 0
                <= neighbour_cell[1] <= self.size - 1
                and neighbour_cell not in self.visited_list # Checks neighbour_cell is in the maze (e.g., not at co-ords
                # (-1, -1), and has not already been visited.
            ):
                return neighbour_cell

        return None

    def get_removable_walls(self):
        offset_pairs = [[(1, 0), (0, 1)], [(1, 0), (0, -1)], [(-1, 0), (0, -1)], [(-1, 0), (0, 1)]]
        walls = [key for key in self.maze.keys() if self.maze[key] == 'X']
        removable_walls = []

        for wall in walls:
            wall_valid = True
            for pair in offset_pairs:
                offset_1 = (wall[0] + pair[0][0], wall[1] + pair[0][1])
                offset_2 = (wall[0] + pair[1][0], wall[1] + pair[1][1])

                if (
                    min(offset_1) > 0 and max(offset_1) < self.size - 1
                    and min(offset_2) > 0 and max(offset_2) < self.size - 1
                ):
                    if self.maze[offset_1] == 'X' and self.maze[offset_2] == 'X':
                        wall_valid = False
                else:
                    wall_valid = False

            if wall_valid:
                removable_walls.append(wall)

        return removable_walls

    def remove_walls(self):
        removable_walls = self.get_removable_walls()

        for wall in range(self.wall_remove_count):
            chosen_wall = random.choice(removable_walls)
            self.maze[chosen_wall] = 'S'
            removable_walls.remove(chosen_wall)

    def add_destructible_walls(self):
        walls = [key for key in self.maze.keys() if self.maze[key] == 'X' and min(key) > 0 and max(key) < self.size - 1]

        for wall in range(self.destructible_wall_count):
            chosen_wall = random.choice(walls)
            self.maze[chosen_wall] = 'D'
            walls.remove(chosen_wall)

    def add_quicksand(self):
        paths = [key for key in self.maze.keys() if self.maze[key] == 'S']

        for path in range(self.quicksand_count):
            chosen_path = random.choice(paths)
            self.maze[chosen_path] = 'Q'
            paths.remove(chosen_path)

    def add_loot_crates(self):
        paths = [key for key in self.maze.keys() if self.maze[key] == 'S']
        offsets = [(0, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

        for path in range(self.loot_crate_count):
            chosen_path = random.choice(paths)
            self.maze[chosen_path] = 'L'

            for offset in offsets:
                pos = (chosen_path[0] + offset[0], chosen_path[1] + offset[1])

                if pos in paths:
                    paths.remove(pos)

    def maze_loop(self):
        self.generate_maze()
        self.generate_paths()
        self.remove_walls()
        self.add_destructible_walls()
        self.add_quicksand()
        self.add_loot_crates()

        return self.maze


class Main:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((800, 800))
        pygame.display.set_caption('Maze Generator')
        self.running = True

        # groups
        self.all_sprites = pygame.sprite.Group()

        # maze
        self.maze = Maze(25, (1, 1)).maze_loop()
        self.place_maze()

    def place_maze(self):
        images = [pygame.image.load('../graphics/path.png').convert_alpha(),
                  pygame.image.load('../graphics/wall.png').convert_alpha(),
                  pygame.image.load('../graphics/breakable_wall.png').convert_alpha(),
                  pygame.image.load('../graphics/loot_crate.png').convert_alpha(),
                  pygame.image.load('../graphics/quicksand.png').convert_alpha()
                ]

        for key, value in self.maze.items():
            image = None
            pos = (key[0] * 32, key[1] * 32)

            if value == 'S':
                image = images[0]
            elif value == 'X':
                image = images[1]
            elif value == 'D':
                image = images[2]
            elif value == 'L':
                image = images[3]
            elif value == 'Q':
                image = images[4]

            Tile((self.all_sprites), image, pos)

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.all_sprites.update()

            # draw
            self.display_surface.fill((255, 255, 255))
            self.all_sprites.draw(self.display_surface)

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    main = Main()
    main.main_loop()


