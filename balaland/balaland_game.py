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
        self.cam = balaland.Cam(self.tile_map)
        self.pj = balaland.Pj(self.cam)
        self.clock = pygame.time.Clock()
        self.movement_handler = balaland.MovementHandler(self)

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
                    # pygame.event.set_grab(not pygame.event.get_grab())
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_left_click_event(event)

    def handle_mouse_left_click_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        center_map_pos = self.cam.get_center_map_pos()
        projectile = balaland.ProjectileRect(
            center_map_pos.x, center_map_pos.y,
            mouse_pos,
            self.pj.x, self.pj.y,
        )
        self.movement_handler.projectiles.append(projectile)

    def draw(self):
        self.cam.screen.fill(self.black)
        self.draw_map()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_pj()
        pygame.display.flip()

    def draw_map(self):
        for tile in self.get_drawable_tiles():
            pygame.draw.rect(self.cam.screen, tile.color, tile)

    def get_drawable_tiles(self):
        tiles_in_cam = self.tile_map.get_tiles(
            self.cam.pos, self.cam.cam_tiles())
        return (
            balaland.BalalandRect(
                tile.x - self.cam.pos.x, tile.y - self.cam.pos.y,
                tile.width, tile.color, tile.solid
            )
            for tile in tiles_in_cam
        )

    def get_drawable_solid_tiles(self):
        tiles = self.get_drawable_tiles()
        return [t for t in tiles if t.solid]

    def draw_enemies(self):
        for e in self.tile_map.enemies:
            e_rect = balaland.BalalandRect(
                round(e.x - self.cam.pos.x), round(e.y - self.cam.pos.y),
                e.width, e.color, e.solid
            )
            pygame.draw.rect(self.cam.screen, e_rect.color, e_rect)

    def draw_pj(self):
        pygame.draw.rect(self.cam.screen, self.pj.color, self.pj)
        pygame.draw.rect(self.cam.screen, self.pj.weapon_color, self.pj.weapon)

    def draw_projectiles(self):
        for p in (
            self.movement_handler.projectiles
            + self.movement_handler.collided_projectiles
        ):
            p_rect = balaland.ProjectileRect(
                round(p.x - self.cam.pos.x), round(p.y - self.cam.pos.y))
            pygame.draw.rect(self.cam.screen, p_rect.color, p_rect)
