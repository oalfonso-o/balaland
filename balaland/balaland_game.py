import sys

import pygame

import balaland
from balaland.cursors.standard import CROSSHAIR


class BalalandGame:
    black = 0, 0, 0

    def __init__(self):
        pygame.init()
        pygame.event.set_grab(False)  # TODO: set true
        cursor = pygame.cursors.compile(
            CROSSHAIR, black='#', white='.', xor='o')
        pygame.mouse.set_cursor((24, 24), (11, 11), *cursor)
        self.tile_map = balaland.TileMap()
        self.pj = self.tile_map.pj
        self.cam = balaland.Cam(self.tile_map, self.pj)
        self.clock = pygame.time.Clock()
        self.movement_handler = balaland.MovementHandler(self)
        self._update_node_grids()

    def _update_node_grids(self):
        for enemy in self.tile_map.enemies:
            enemy.init_node_grid(self.tile_map, self.pj)

    def update(self):
        self.move()
        self.draw()

    def move(self):
        self.movement_handler.move()
        self.handle_events()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    # TODO: reactivate when not debugging
                    pygame.event.set_grab(not pygame.event.get_grab())
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_left_click_event(event)

    def handle_mouse_left_click_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        center_screen_vector = self.cam.get_center_screen_vector()
        projectile = balaland.ProjectileRect(
            self.pj.center_pos(), mouse_pos, center_screen_vector)
        self.movement_handler.projectiles.append(projectile)

    def draw(self):
        self.cam.screen.fill(self.black)
        self.draw_map()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_pj()
        pygame.display.flip()

    def _locate_rect_in_cam(self, rect):
        x = rect.x - self.cam.pos.x
        y = rect.y - self.cam.pos.y
        return balaland.BalalandRect(x, y, rect.width, rect.color)

    def draw_map(self):
        for tile in self.tile_map.get_tiles(self.cam.pos, self.cam.size):
            rect_in_cam = self._locate_rect_in_cam(tile)
            pygame.draw.rect(self.cam.screen, rect_in_cam.color, rect_in_cam)

    def get_drawable_solid_tiles(self):
        tiles = self.tile_map.get_tiles(self.cam.pos, self.cam.size)
        return [t for t in tiles if t.solid]

    def draw_enemies(self):
        for enemy in self.tile_map.enemies:
            rect_in_cam = self._locate_rect_in_cam(enemy)
            pygame.draw.rect(self.cam.screen, rect_in_cam.color, rect_in_cam)

    def draw_projectiles(self):
        for projectile in (
            self.movement_handler.projectiles
            + self.movement_handler.collided_projectiles
        ):
            rect_in_cam = self._locate_rect_in_cam(projectile)
            pygame.draw.rect(self.cam.screen, rect_in_cam.color, rect_in_cam)

    def draw_pj(self):
        pj_in_cam = self._locate_rect_in_cam(self.pj)
        weapon_in_cam = self._locate_rect_in_cam(self.pj.weapon)
        pygame.draw.rect(self.cam.screen, pj_in_cam.color, pj_in_cam)
        pygame.draw.rect(self.cam.screen, weapon_in_cam.color, weapon_in_cam)
