import os

import pygame

import balaland


class BaseRect(pygame.Rect):
    def __init__(self, x, y, width, height, color):
        super().__init__(int(x), int(y), width, height)
        size = (width, height)
        self.original_surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            self.original_surface, color, pygame.Rect((0, 0), size))
        self.surface = self.original_surface
        rect = self.surface.get_rect()
        self.width = rect.width
        self.height = rect.height
        self.color = color


class BalalandRect(BaseRect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(int(x), int(y), size, size, color)
        self.solid = solid


class CenterPosRect(BalalandRect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(x, y, size, color, solid)

    # TODO: property
    def center_pos(self):
        return pygame.math.Vector2(
            self.x + self.width / 2,
            self.y + self.height / 2,
        )


class ProjectileRect(CenterPosRect):
    def __init__(
        self, pos, mouse_pos=None, center_screen_pos=None, angle=None
    ):
        if mouse_pos and center_screen_pos and angle:
            raw_direction = (
                + pygame.math.Vector2(center_screen_pos.x, center_screen_pos.y)
                - mouse_pos
            )
            self.direction = balaland.MovementHandler.rotate_and_normalize(
                raw_direction.x, raw_direction.y, angle)
            self.speed = float(os.environ.get('BL_PROJECTILE_SPEED'))
            self.movement = pygame.math.Vector2(
                - (self.direction.x * self.speed),
                - (self.direction.y * self.speed),
            )
        super().__init__(
            pos.x, pos.y,
            int(os.environ.get('BL_PROJECTILE_SIZE')),
            (0, 0, 0,),
            True,
        )

    def hit(self):
        self.color = 150, 0, 0
        self.width *= 2


class LivingRect(CenterPosRect):
    dead_color = 60, 0, 0
    critical_hp_color = 140, 0, 0

    def __init__(self, x, y, size, color, solid=True, hp=None):
        super().__init__(int(x), int(y), size, color, solid)
        self.hp = hp or int(os.environ.get('BL_LIVING_DEFAULT_HP'))

    def hit(self):
        self.hp -= 1
        if not self.hp:
            self.color = self.dead_color
            self.solid = False
        elif self.hp == 1:
            self.color = self.critical_hp_color


class Pj(LivingRect):

    def __init__(self, x, y):
        self.width = self.height = int(os.environ.get('BL_PJ_SIZE'))
        self.x = x
        self.y = y
        self.speed = pygame.math.Vector2(
            int(os.environ.get('BL_PJ_SPEED_X')),
            int(os.environ.get('BL_PJ_SPEED_Y')),
        )
        self.color = (100, 175, 220)
        self.weapon_distance = int(os.environ.get('BL_PJ_WEAPON_DISTANCE'))
        self.weapon = BaseRect(
            self.x, self.y,
            int(os.environ.get('BL_PJ_WEAPON_WIDTH')),
            int(os.environ.get('BL_PJ_WEAPON_HEIGHT')),
            (0, 0, 0),
        )
        super().__init__(
            int(self.x), int(self.y), self.width, self.color, True)

    def update_weapon_pos(self):
        self.weapon.x = self.x + (self.width / 2)
        self.weapon.y = self.y


class EnemyRect(LivingRect):

    def __init__(self, x, y, size, color):
        super().__init__(int(x), int(y), size, color)
        self.speed = pygame.math.Vector2(
            int(os.environ.get('BL_ENEMY_SPEED_X')),
            int(os.environ.get('BL_ENEMY_SPEED_Y')),
        )
        self.node_grid = balaland.NodeGrid(self)

    def init_node_grid(self, tile_map, target_rect):
        self.node_grid.initalize(tile_map, target_rect)
