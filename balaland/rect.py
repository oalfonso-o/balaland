import os

import pygame


class BalalandRect(pygame.Rect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(int(x), int(y), size, size)
        self.color = color
        self.solid = solid


class CenterPosRect(BalalandRect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(x, y, size, color, solid)
        self.center_pos = self._real_center_pos()

    def _real_center_pos(self):
        return pygame.math.Vector2(
            self.x + self.width / 2,
            self.y + self.height / 2,
        )


class ProjectileRect(CenterPosRect):
    def __init__(self, x, y, mouse_pos=None, pj_pos=None):  # TODO: pj center position
        if mouse_pos and pj_pos:
            self.direction = (
                pygame.math.Vector2(pj_pos.x, pj_pos.y) - mouse_pos
            ).normalize()
            self.speed = float(os.environ.get('BL_PROJECTILE_SPEED'))
            self.movement = pygame.math.Vector2(
                - (self.direction.x * self.speed),
                - (self.direction.y * self.speed),
            )
        super().__init__(
            x, y,
            int(os.environ.get('BL_PROJECTILE_SIZE')),
            (0, 0, 0,),
            True,
        )


class LivingRect(CenterPosRect):
    dead_color = 0, 0, 0
    critical_hp_color = 140, 0, 0

    def __init__(self, x, y, size, color, solid=True, hp=None):
        super().__init__(int(x), int(y), size, color, solid)
        self.hp = hp or int(os.environ.get('BL_SOMEBODY_DEFAULT_HP'))

    def hit(self):
        self.hp -= 1
        if not self.hp:
            self.color = self.dead_color
            self.solid = False
        elif self.hp == 1:
            self.color = self.critical_hp_color


class Pj(LivingRect):
    pj_color = (100, 175, 220)
    weapon_color = (0, 0, 0)

    def __init__(self, cam):
        self.size = int(os.environ.get('BL_PJ_SIZE'))
        # TODO: set respawn in place by map, with this method Pj can respawn
        # in a collisionable rect
        self._center_pj_in_cam(cam.width)  # TODO: use also height
        self.center_pos = self._real_center_pos()
        self.speed = pygame.math.Vector2(
            int(os.environ.get('BL_PJ_SPEED_X')),
            int(os.environ.get('BL_PJ_SPEED_Y')),
        )
        self.color = self.pj_color
        self.weapon_scale = int(os.environ.get('BL_PJ_WEAPON_SCALE'))
        self.weapon = pygame.Rect(
            self.pos.x, self.pos.y,
            int(os.environ.get('BL_PJ_WEAPON_WIDTH')),
            int(os.environ.get('BL_PJ_WEAPON_HEIGHT')),
        )
        cam.update_limit_pos(self.size)
        super().__init__(
            int(self.x), int(self.y), self.size, self.color, True)

    def _center_pj_in_cam(self, cam_width):
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
