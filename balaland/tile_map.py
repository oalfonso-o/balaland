import os
import copy

import pygame

import balaland


class TileMap:
    solid_tile_color = 220, 200, 100
    enemy_color = 255, 0, 0
    white = 255, 255, 255
    maps_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'maps')

    def __init__(self):
        self.tile_size = int(os.environ.get('BL_TILE_MAP_TILE_SIZE'))
        self.safety_tiles = 1
        self.enemy_size = int(os.environ.get('BL_PJ_SIZE'))
        self.enemies = []
        self.map = self.load_map()
        self.width = len(self.map)
        self.height = len(self.map)

    def load_map(self, map_file=None):
        if not map_file:
            map_file = os.environ.get('BL_TILE_MAP_DEFAULT_MAP')
        map_file_path = os.path.join(self.maps_path, map_file)
        map_ = []
        with open(map_file_path, 'r') as fd:
            for y, file_line in enumerate(fd):
                map_row = []
                for x, file_tile in enumerate(file_line.replace('\n', '')):
                    if file_tile == 'E':
                        self.enemies.append(
                            balaland.EnemyRect(
                                x * self.tile_size, y * self.tile_size,
                                self.enemy_size, self.enemy_color
                            )
                        )
                    tile_solid = file_tile == 'w'
                    tile_color = (
                        self.solid_tile_color if tile_solid else self.white)
                    tile_rect = balaland.BalalandRect(
                        x * self.tile_size, y * self.tile_size, self.tile_size,
                        tile_color, tile_solid
                    )
                    map_row.append(tile_rect)
                map_.append(map_row)
        return map_

    def get_tiles(self, map_pos, num_tiles):
        start_tile_pos_y = int(map_pos.y // self.tile_size - self.safety_tiles)
        start_tile_pos_y = start_tile_pos_y if start_tile_pos_y >= 0 else 0
        start_tile_pos_x = int(map_pos.x // self.tile_size - self.safety_tiles)
        start_tile_pos_x = start_tile_pos_x if start_tile_pos_x >= 0 else 0
        end_tile_pos_y = start_tile_pos_y + num_tiles + self.safety_tiles
        end_tile_pos_y = (
            end_tile_pos_y if end_tile_pos_y <= self.width else self.width)
        end_tile_pos_x = start_tile_pos_x + num_tiles + self.safety_tiles
        end_tile_pos_x = (
            end_tile_pos_x if end_tile_pos_x <= self.width else self.width)
        tiles = [
            tile
            for map_row in self.map[start_tile_pos_y:end_tile_pos_y]
            for tile in map_row[start_tile_pos_x:end_tile_pos_x]
        ]
        return tiles


class Node:
    def __init__(
        self, solid, x, y, grid_x, grid_y, g=0, h=0, parent=None
    ):
        self.solid = solid
        self.x = x
        self.y = y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.g = g
        self.h = h
        self.parent = parent

    def get_f(self):
        return self.g + self.h

    def update_cost(self, parent, g, h):
        # import pudb; pudb.set_trace()
        self.parent = parent
        self.g = g
        self.h = h


class NodeGrid:
    def __init__(self, from_rect):
        ''' Switch x and y to use x as first index, like a grid '''
        self.from_rect = from_rect
        self.nodes = []
        self.path = []

    def initalize(self, tile_map, target_rect):
        self.target_rect = target_rect
        self.tile_map = tile_map
        for grid_x, tile_x in enumerate(tile_map.map[0]):
            node_col = []
            for grid_y in range(len(tile_map.map)):
                tile = tile_map.map[grid_y][grid_x]
                solid = tile.solid
                node_col.append(Node(solid, tile.x, tile.y, grid_x, grid_y))
            self.nodes.append(node_col)
        self.grid_size_x = len(self.nodes)
        self.grid_size_y = len(self.nodes[0])
        self.from_node = self.get_node(self.from_rect.x, self.from_rect.y)
        self.target_node = self.get_node(
            self.target_rect.x, self.target_rect.y)
        self.open = []
        self.closed = [self.from_node]
        for neightbour in self.get_neightbours(self.from_node):
            # import pudb; pudb.set_trace()
            g = self._calc_g(self.from_node, neightbour)
            h = self._calc_h(neightbour, self.target_node)
            neightbour.update_cost(self.from_node, g, h)
            self.open.append(neightbour)

    def get_next_path_node(self):
        return self.path[0]

    def get_direction(self):
        next_path_node = self.get_next_path_node()
        direction = (
            pygame.math.Vector2(next_path_node.x, next_path_node.y)
            - pygame.math.Vector2(self.from_rect.x, self.from_rect.y)
        )
        if bool(direction):
            return direction.normalize()
        return direction  # TODO: why 0? this is just a dirty bugfix

    def update(self):
        self.from_node = self.get_node(self.from_rect.x, self.from_rect.y)
        self.target_node = self.get_node(
            self.target_rect.x, self.target_rect.y)
        for current_node in self.open_nodes_sorted_by_lowest_f_cost():
            import pudb; pudb.set_trace()
            self.open.pop(self.open.index(current_node))
            self.closed.append(current_node)

            if current_node is self.target_node:
                import pudb; pudb.set_trace()
                break

            for neightbour in self.get_neightbours(current_node):
                if (
                    neightbour.get_f() < current_node.get_f()
                    or neightbour not in self.open
                ):
                    g = self._calc_g(current_node, neightbour)
                    h = self._calc_h(neightbour, self.target_node)
                    neightbour.update_cost(current_node, g, h)
                    if neightbour not in self.open:
                        # import pudb; pudb.set_trace()
                        self.open.append(neightbour)
        self.update_path()

    @staticmethod
    def _calc_g(current_node, neightbour):
        current_g = (
            10
            if current_node.grid_x == neightbour.grid_x
            or current_node.grid_y == neightbour.grid_y
            else 14
        )
        return current_node.g + current_g

    def _calc_h(self, from_node, target_node):
        dist_x = int(
            abs(from_node.x - target_node.x) // self.tile_map.tile_size)
        dist_y = int(
            abs(from_node.y - target_node.y) // self.tile_map.tile_size)
        diagonals = 0
        while dist_x and dist_y:
            dist_x -= 1
            dist_y -= 1
            diagonals += 1
        straights = dist_x + dist_y
        return (diagonals * 14) + (straights * 10)

    def update_path(self):
        # import pudb; pudb.set_trace()
        self.path = []
        node = copy.copy(self.target_node)
        while node.parent:
            node = node.parent
            self.path.append(node)
        self.path.reverse()

    def open_nodes_sorted_by_lowest_f_cost(self):
        return sorted(self.open, key=lambda n: n.get_f())

    def get_node(self, x, y):
        grid_x = int(x // self.tile_map.tile_size)
        grid_y = int(y // self.tile_map.tile_size)
        return self.nodes[grid_x][grid_y]

    def get_neightbours(self, node):
        neightbours = []
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                if x == 0 and y == 0:
                    continue
                check_x = node.grid_x + x
                check_y = node.grid_y + y
                if (
                    check_x >= 0
                    and check_x < self.grid_size_x
                    and check_y >= 0
                    and check_y < self.grid_size_y
                ):
                    neightbour = self.nodes[check_x][check_y]
                    if not neightbour.solid and neightbour not in self.closed:
                        neightbours.append(neightbour)
        return neightbours
