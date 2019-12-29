import os

import pygame


class BalalandRect(pygame.Rect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(int(x), int(y), size, size)
        self.color = color
        self.solid = solid


class ProjectileRect(BalalandRect):
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
        self.center_pos = self._real_center_pos()

    def _real_center_pos(self):
        return pygame.math.Vector2(
            self.x + self.width / 2,
            self.y + self.height / 2,
        )


class SomebodyRect(BalalandRect):
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
