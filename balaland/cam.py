import os

import pygame


class Cam:
    def __init__(self, tile_map):
        self.size = int(os.environ.get('BL_CAM_SIZE'))
        self.pos = pygame.math.Vector2(
            int(os.environ.get('BL_CAM_POS_START_X')),
            int(os.environ.get('BL_CAM_POS_START_Y')),
        )
        # TODO: review this
        self.width = tile_map.tile_size * self.size + tile_map.tile_size
        self.screen = pygame.display.set_mode((self.width, self.width))
        self.map_width = tile_map.width * tile_map.tile_size
        self.map_height = tile_map.height * tile_map.tile_size
        self.limit_pos = None

    def update_limit_pos(self, pj_size):
        ''' After a pj is instantiated, this method must be called '''
        half_cam_size = self.width // 2
        half_pj_size = pj_size // 2
        negative_cam_limit = half_pj_size - half_cam_size
        positive_cam_limit = self.map_width - half_cam_size - half_pj_size
        self.limit_pos = {
            'x': {
                '+': positive_cam_limit,
                '-': negative_cam_limit,
            },
            'y': {
                '+': positive_cam_limit,
                '-': negative_cam_limit,
            },
        }

    def cam_tiles(self):
        return self.size * 2 + 1

    def move_pos_limit(self, axis, direction):
        setattr(self.pos, axis, self.limit_pos[axis][direction])

    def get_center_map_pos(self):
        return pygame.math.Vector2(
            self.pos.x + self.width // 2,
            self.pos.y + self.width // 2,
        )
