import sys
import copy
import math

import pygame

import balaland


class BalalandGame:
    black = 0, 0, 0
    white = 255, 255, 255
    sensibility = 8
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
        self.angle = 0

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
        target = self.center_cam.x, mouse_pos[1]
        center_screen_vector = self.cam.get_center_screen_vector()
        projectile = balaland.ProjectileRect(
            self.pj.center_pos(), target, center_screen_vector, self.angle)
        self.movement_handler.projectiles.append(projectile)

    def draw(self):
        self.mouse_rel_x += pygame.mouse.get_rel()[0]
        dist_x = self.center_cam.x - self.mouse_rel_x
        self.angle = (dist_x / self.sensibility)
        self.cam.screen.fill(self.white)
        tile_rect = balaland.BalalandRect(500, 0, 100, (0, 0, 100), True)
        in_cam = self._locate_rect_in_cam(tile_rect)
        self.cam.screen.blit(in_cam.surface, in_cam)
        self.draw_map()
        self.draw_dead_enemies()
        self.draw_projectiles()
        self.draw_pj()
        self.draw_crosshair()
        pygame.display.update()

    def _locate_rect_in_cam(self, rect):
        relocated_rect = copy.copy(rect)
        x_relative = relocated_rect.center[0] - self.pj.center[0]
        y_relative = relocated_rect.center[1] - self.pj.center[1]
        relocated_rect.surface = pygame.transform.rotate(
            rect.original_surface, -self.angle)
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
        x = x + self.pj.center[0] - self.cam.pos.x
        y = y + self.pj.center[1] - self.cam.pos.y
        relocated_rect.center = x, y
        return relocated_rect

    def _locate_pj_rect_in_cam(self, rect):
        x = rect.x - self.cam.pos.x
        y = rect.y - self.cam.pos.y
        return balaland.BalalandRect(x, y, rect.width, rect.color)

    def draw_map(self):
        for tile in self.get_visible_rects():
            rect_in_cam = self._locate_rect_in_cam(tile)
            self.cam.screen.blit(rect_in_cam.surface, rect_in_cam)

    def get_visible_rects(self):
        collidable_rects = (
            self.get_drawable_solid_tiles()
            + [enemy for enemy in self.tile_map.enemies if enemy.hp]
        )
        rays = self.get_rays(collidable_rects)
        self.move_rays(rays, collidable_rects)
        visible_surface = self.get_visible_surface(rays)
        return self.get_rects_in_visible_surface(
            collidable_rects, visible_surface)

    def get_drawable_solid_tiles(self):
        tiles = self.tile_map.get_tiles(self.cam.pos, self.cam.size)
        return [t for t in tiles if t.solid]

    def get_rays(self, collidable_rects):
        rays = []
        close_rays = []
        x = self.pj.x
        y = self.pj.y
        for rect in collidable_rects:
            rays.append(balaland.Ray(x, y, rect.top, rect.left))
            rays.append(balaland.Ray(x, y, rect.top, rect.right))
            rays.append(balaland.Ray(x, y, rect.bottom, rect.left))
            rays.append(balaland.Ray(x, y, rect.bottom, rect.left))
        for ray in rays:
            close_rays.append(
                balaland.Ray(x, y, ray.target_x, ray.target_y, correct='+'))
            close_rays.append(
                balaland.Ray(x, y, ray.target_x, ray.target_y, correct='-'))
        return rays

    def move_rays(self, rays, collidable_rects):
        dummy_vector = pygame.math.Vector2(0, 0)
        for ray in rays:
            for step in range(ray.limit):
                ray.x += ray.direction.x
                if (
                    self.movement_handler.rect_collision(
                        'x', collidable_rects, ray, dummy_vector)
                ):
                    break
                ray.y += ray.direction.y
                if (
                    self.movement_handler.rect_collision(
                        'y', collidable_rects, ray, dummy_vector)
                ):
                    break

    def get_visible_surface(self, rays):
        sorted_rays = sorted(rays, key=lambda x: x.angle)
        points = [(ray.x, ray.y) for ray in sorted_rays]
        surface = pygame.surface.Surface(
            (balaland.Ray.limit * 2, balaland.Ray.limit * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.polygon(surface, self.black, points)
        return surface

    def get_rects_in_visible_surface(self, collidable_rects, visible_surface):
        rects = []
        visible_mask = pygame.mask.from_surface(visible_surface)
        for rect in collidable_rects:
            offset_x = self.pj.x - balaland.Ray.limit - rect.x
            offset_y = self.pj.y - balaland.Ray.limit - rect.y
            if rect.mask.overlap(visible_mask, (offset_x, offset_y)):
                rects.append(rect)
        return rects

    def draw_dead_enemies(self):
        for enemy in [e for e in self.tile_map.enemies if not e.hp]:
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
        pj_in_cam = self._locate_pj_rect_in_cam(self.pj)
        weapon_in_cam = self._locate_pj_rect_in_cam(self.pj.weapon)
        pygame.draw.rect(self.cam.screen, pj_in_cam.color, pj_in_cam)
        pygame.draw.rect(self.cam.screen, weapon_in_cam.color, weapon_in_cam)

    def draw_crosshair(self):
        # TODO: customize crosshair more
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] >= self.center_cam.y:
            pygame.mouse.set_pos(mouse_pos[0], self.center_cam.y)
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
