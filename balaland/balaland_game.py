import sys
import copy
import math

import pygame

import balaland


class BalalandGame:
    black = 0, 0, 0
    sensibility = 4
    radians = math.pi / 180

    def __init__(self):
        pygame.init()
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.tile_map = balaland.TileMap()
        self.pj = self.tile_map.pj
        self.cam = balaland.Cam(self.tile_map, self.pj)
        self.clock = pygame.time.Clock()
        self.movement_handler = balaland.MovementHandler(self)
        self._update_node_grids()
        self.mouse_rel_x = 0
        self.center_cam = self.cam.get_center_screen_vector()

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
                    pygame.event.set_grab(not pygame.event.get_grab())
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
        self.mouse_rel_x += pygame.mouse.get_rel()[0]
        dist_x = self.center_cam - self.mouse_rel_x
        self.angle = (dist_x / self.sensibility)
        self.cam.screen.fill(self.black)
        self.draw_map()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_pj()
        self.draw_crosshair()
        pygame.display.flip()

    def _locate_rect_in_cam(self, rect):
        relocated_rect = copy.copy(rect)
        x_relative = relocated_rect.x - self.pj.x
        y_relative = relocated_rect.y - self.pj.y
        relocated_rect.surface = pygame.transform.rotate(
            relocated_rect.original_surface, -self.angle)
        surface_rect = relocated_rect.surface.get_rect()
        relocated_rect.width = surface_rect.width
        relocated_rect.height = surface_rect.height
        x = (
            (x_relative * math.cos(self.angle * self.radians))
            - (y_relative * math.sin(self.angle * self.radians))
        )
        y = (
            (y_relative * math.cos(self.angle * self.radians))
            + (x_relative * math.sin(self.angle * self.radians))
        )
        relocated_rect.center = x + self.pj.x, y + self.pj.y
        return relocated_rect

    def draw_map(self):
        for tile in self.tile_map.get_tiles(self.cam.pos, self.cam.size):
            rect_in_cam = self._locate_rect_in_cam(tile)
            self.cam.screen.blit(rect_in_cam.surface, rect_in_cam)

    def get_drawable_solid_tiles(self):
        tiles = self.tile_map.get_tiles(self.cam.pos, self.cam.size)
        return [t for t in tiles if t.solid]

    def draw_enemies(self):
        for enemy in self.tile_map.enemies:
            rect_in_cam = self._locate_rect_in_cam(enemy)
            self.cam.screen.blit(rect_in_cam.surface, rect_in_cam)

    def draw_projectiles(self):
        for projectile in (
            self.movement_handler.projectiles
            + self.movement_handler.collided_projectiles
        ):
            rect_in_cam = self._locate_rect_in_cam(projectile)
            self.cam.screen.blit(rect_in_cam.surface, rect_in_cam)

    def draw_pj(self):
        pj_in_cam = self._locate_rect_in_cam(self.pj)
        weapon_in_cam = self._locate_rect_in_cam(self.pj.weapon)
        self.cam.screen.blit(pj_in_cam.surface, pj_in_cam)
        self.cam.screen.blit(weapon_in_cam.surface, weapon_in_cam)

    def draw_crosshair(self):
        # TODO: customize crosshair more
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(
            self.cam.screen,
            (0, 0, 0),
            (self.center_cam.x - 5, mouse_pos[1] - 5),
            (self.center_cam.y + 5, mouse_pos[1] + 5),
            1,
        )
        pygame.draw.line(
            self.cam.screen,
            (0, 0, 0),
            (self.center_cam.x + 5, mouse_pos[1] - 5),
            (self.center_cam.y - 5, mouse_pos[1] + 5),
            1,
        )
