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
        self.direction = pygame.math.Vector2(0, 0)
        self.size = int(os.environ.get('BL_PJ_SIZE'))
        self.weapon_scale = int(os.environ.get('BL_PJ_WEAPON_SCALE'))
        self.pos = self.cam_centered_position(cam.width)
        self.rect = balaland.BalalandRect(
            self.pos.x, self.pos.y, self.size, self.pj_color, True)
        self.weapon = pygame.Rect(
            self.pos.x, self.pos.y,
            int(os.environ.get('BL_PJ_WEAPON_WIDTH')),
            int(os.environ.get('BL_PJ_WEAPON_HEIGHT')),
        )
        cam.update_limit_pos(self.size)

    def cam_centered_position(self, cam_width):
        center = (cam_width // 2) - (self.size // 2)
        return pygame.math.Vector2(center, center)

    def get_center_position(self):
        return self.pos + pygame.math.Vector2(self.size // 2, self.size // 2)

    def update_weapon_position(self):
        mouse_pos = pygame.mouse.get_pos()
        self.direction = (self.get_center_position() - mouse_pos).normalize()
        self.weapon.x = (
            self.get_center_position().x
            + (self.direction.x * self.weapon_scale)
            - (self.weapon.width / 2)
        )
        self.weapon.y = (
            self.get_center_position().y
            + (self.direction.y * self.weapon_scale)
            - (self.weapon.height / 2)
        )
