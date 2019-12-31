import os

import pygame


class Cam:
    def __init__(self, tile_map, pj):
        self.tile_map = tile_map
        self.pj = pj
        self.size = int(os.environ.get('BL_CAM_SIZE'))
        self.width = self.height = tile_map.tile_size * self.size
        self.pos = None
        self.follow_pj()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def follow_pj(self):
        self.pos = pygame.math.Vector2(
            self.pj.x - (self.width / 2) + (self.pj.width / 2),
            self.pj.y - (self.height / 2) + (self.pj.height / 2),
        )

    def get_center_screen_vector(self):
        return pygame.math.Vector2(self.width // 2, self.height // 2)
