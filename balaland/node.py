import copy

import pygame


class Node:
    def __init__(
        self, id_, solid, x, y, grid_x, grid_y, g=0, h=0, parent=None
    ):
        self.id = id_
        self.solid = solid
        self.x = x
        self.y = y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.g = g
        self.h = h
        self.parent = parent

    def __repr__(self):
        return f'{self.x//80}, {self.y//80}, parent=[{self.parent}]'

    def get_f(self):
        return self.g + self.h

    def update_cost(self, parent, g, h):
        self.parent = parent
        self.g = g
        self.h = h

    def reset(self):
        self.parent = None
        self.g = 0
        self.h = 0


class NodeGrid:
    def __init__(self, from_rect):
        ''' Switch x and y to use x as first index, like a grid '''
        self.from_rect = from_rect
        self.nodes = []
        self.next_node = None

    def initalize(self, tile_map, target_rect):  # TODO: refactor arch
        self.target_rect = target_rect
        self.tile_map = tile_map
        id_ = 1
        for grid_x, tile_x in enumerate(tile_map.map[0]):
            node_col = []
            for grid_y in range(len(tile_map.map)):
                tile = tile_map.map[grid_y][grid_x]
                solid = tile.solid
                node_col.append(
                    Node(id_, solid, tile.x, tile.y, grid_x, grid_y))
                id_ += 1
            self.nodes.append(node_col)
        self.grid_size_x = len(self.nodes)
        self.grid_size_y = len(self.nodes[0])
        self.from_node = self._get_node(self.from_rect.x, self.from_rect.y)
        self.target_node = self._get_node(
            self.target_rect.x, self.target_rect.y)
        self.open = [self.from_node]
        self.closed = []
        self.next_node = None
        self._find_next_node()

    def update(self):
        self._find_next_node()

    def get_direction(self):
        center_next_node_x = self.next_node.x + (self.tile_map.tile_size // 2)
        center_next_node_y = self.next_node.y + (self.tile_map.tile_size // 2)
        direction = (
            pygame.math.Vector2(center_next_node_x, center_next_node_y)
            - pygame.math.Vector2(self.from_rect.x, self.from_rect.y)
        )
        if bool(direction):
            return direction.normalize()
        return direction

    def _get_node(self, x, y):
        grid_x = int(x // self.tile_map.tile_size)
        grid_y = int(y // self.tile_map.tile_size)
        return self.nodes[grid_x][grid_y]

    def _find_next_node(self):
        while self.open and not self.target_node.parent:
            current_node = self.open.pop(0)
            self.closed.append(current_node)
            for neightbour in self._get_neightbours(current_node):
                if (
                    neightbour.get_f() < current_node.get_f()
                    or neightbour not in self.open
                ):
                    g = self._calc_g(current_node, neightbour)
                    h = self._calc_h(neightbour, self.target_node)
                    neightbour.update_cost(current_node, g, h)
                    if neightbour not in self.open:
                        self.open.append(neightbour)
            self._sort_open_nodes()
        self._path_finded()

    def _get_neightbours(self, node):
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
                    if abs(x) and abs(y):
                        right_n = self.nodes[0][node.grid_y]
                        left_n = self.nodes[node.grid_x][0]
                        if right_n.solid or left_n.solid:
                            continue
                    neightbour = self.nodes[check_x][check_y]
                    if not neightbour.solid and neightbour not in self.closed:
                        neightbours.append(neightbour)
        return neightbours

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

    def _sort_open_nodes(self):
        self.open = sorted(self.open, key=lambda n: (n.get_f(), n.id))

    def _path_finded(self):
        self.from_node = self._get_node(self.from_rect.x, self.from_rect.y)
        self.target_node = self._get_node(
            self.target_rect.x, self.target_rect.y)
        self._update_next_node()
        self.open = [self.from_node]
        self.closed = []
        self._reset_nodes()

    def _update_next_node(self):
        for tile in self.tile_map.get_not_collidable_tiles():
            tile.color = (255, 255, 255)
        node = copy.copy(self.target_node)
        while node.parent:
            if not node.parent.parent:
                self.next_node = node
                break
            node = node.parent
            grid_x = int(node.x // self.tile_map.tile_size)
            grid_y = int(node.y // self.tile_map.tile_size)
            self.tile_map.map[grid_y][grid_x].color = (130, 1, 10)

    def _reset_nodes(self):
        for node_col in self.nodes:
            for node in node_col:
                node.reset()
        self.target_node.parent = None
