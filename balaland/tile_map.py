import os

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
                            balaland.SomebodyRect(
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
