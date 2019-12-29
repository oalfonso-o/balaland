import os

import pygame

import balaland


class Pj:
    pj_color = (100, 175, 220)
    weapon_color = (0, 0, 0)

    def __init__(self, cam):
        self.speed = pygame.math.Vector2(
            int(os.environ.get('BL_PJ_SPEED_X')),
            int(os.environ.get('BL_PJ_SPEED_Y')),
        )
        self.size = int(os.environ.get('BL_PJ_SIZE'))
        self.weapon_scale = int(os.environ.get('BL_PJ_WEAPON_SCALE'))
        self.pos = self.cam_centered_position(cam.width)
        self.center_pos = self._real_center_pos()
        self.rect = balaland.BalalandRect(
            self.pos.x, self.pos.y, self.size, self.pj_color, True)
        self.weapon = pygame.Rect(
            self.pos.x, self.pos.y,
            int(os.environ.get('BL_PJ_WEAPON_WIDTH')),
            int(os.environ.get('BL_PJ_WEAPON_HEIGHT')),
        )
        cam.update_limit_pos(self.size)

    def cam_centered_position(self, cam_width):
        center = (cam_width / 2) - (self.size / 2)
        return pygame.math.Vector2(center, center)

    def _real_center_pos(self):
        return self.pos + pygame.math.Vector2(self.size / 2, self.size / 2)

    def update_weapon_position(self):
        mouse_pos = pygame.mouse.get_pos()
        direction = (self.self.center_pos - mouse_pos).normalize()
        self.weapon.x = (
            self.self.center_pos.x
            + (direction.x * self.weapon_scale)
            - (self.weapon.width / 2)
        )
        self.weapon.y = (
            self.self.center_pos.y
            + (direction.y * self.weapon_scale)
            - (self.weapon.height / 2)
        )
