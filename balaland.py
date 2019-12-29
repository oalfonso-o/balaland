import sys
import os
from dotenv import load_dotenv

import pygame

from cursor import CROSSHAIR


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

    def get_center_map_pos(self):
        return pygame.math.Vector2(
            self.x + self.size[0] / 2,
            self.y + self.size[1] / 2,
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


class TileMap:
    solid_tile_color = 220, 200, 100
    enemy_color = 255, 0, 0
    white = 255, 255, 255

    def __init__(self):
        self.tile_size = int(os.environ.get('BL_TILE_MAP_TILE_SIZE'))
        self.safety_tiles = 1
        self.enemy_size = int(os.environ.get('BL_PJ_SIZE'))
        self.enemies = []
        self.map = self.load_map()
        self.width = len(self.map)
        self.height = len(self.map)

    def load_map(self, map_file='tile_map.tm'):
        map_ = []
        with open(map_file, 'r') as fd:
            for y, file_line in enumerate(fd):
                map_row = []
                for x, file_tile in enumerate(file_line.replace('\n', '')):
                    if file_tile == 'E':
                        self.enemies.append(
                            SomebodyRect(
                                x * self.tile_size, y * self.tile_size,
                                self.enemy_size, self.enemy_color
                            )
                        )
                    tile_solid = file_tile == 'w'
                    tile_color = (
                        self.solid_tile_color if tile_solid else self.white)
                    tile_rect = BalalandRect(
                        x * self.tile_size, y * self.tile_size, self.tile_size,
                        tile_color, tile_solid
                    )
                    map_row.append(tile_rect)
                map_.append(map_row)
        return map_

    def get_tiles(self, map_pos, num_tiles):
        start_tile_pos_y = int(map_pos.y // self.tile_size - self.safety_tiles)
        start_tile_pos_y = start_tile_pos_y if start_tile_pos_y >= 0 else 0
        start_tile_pos_x = int(map_pos.x // self.tile_size - self.safety_tiles)
        start_tile_pos_x = start_tile_pos_x if start_tile_pos_x >= 0 else 0
        end_tile_pos_y = start_tile_pos_y + num_tiles + self.safety_tiles
        end_tile_pos_y = (
            end_tile_pos_y if end_tile_pos_y <= self.width else self.width)
        end_tile_pos_x = start_tile_pos_x + num_tiles + self.safety_tiles
        end_tile_pos_x = (
            end_tile_pos_x if end_tile_pos_x <= self.width else self.width)
        tiles = [
            tile
            for map_row in self.map[start_tile_pos_y:end_tile_pos_y]
            for tile in map_row[start_tile_pos_x:end_tile_pos_x]
        ]
        return tiles


class Cam:
    def __init__(self, tile_map):
        self.size = int(os.environ.get('BL_CAM_SIZE'))
        self.pos = pygame.math.Vector2(
            int(os.environ.get('BL_CAM_POS_START_X')),
            int(os.environ.get('BL_CAM_POS_START_Y')),
        )
        # TODO: review this
        self.width = tile_map.tile_size * self.size + tile_map.tile_size
        self.screen = pygame.display.set_mode((self.width, self.width))
        self.map_width = tile_map.width * tile_map.tile_size
        self.map_height = tile_map.height * tile_map.tile_size
        self.limit_pos = None

    def update_limit_pos(self, pj_size):
        ''' After a pj is instantiated, this method must be called '''
        half_cam_size = self.width // 2
        half_pj_size = pj_size // 2
        negative_cam_limit = half_pj_size - half_cam_size
        positive_cam_limit = self.map_width - half_cam_size - half_pj_size
        self.limit_pos = {
            'x': {
                '+': positive_cam_limit,
                '-': negative_cam_limit,
            },
            'y': {
                '+': positive_cam_limit,
                '-': negative_cam_limit,
            },
        }

    def cam_tiles(self):
        return self.size * 2 + 1

    def move_pos_limit(self, axis, direction):
        setattr(self.pos, axis, self.limit_pos[axis][direction])

    def get_center_map_pos(self):
        return pygame.math.Vector2(
            self.pos.x + self.width // 2,
            self.pos.y + self.width // 2,
        )


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
        self.rect = BalalandRect(
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


class MovementHandler:
    def __init__(self, balaland):
        self.balaland = balaland
        self.cam = self.balaland.cam
        self.pj = self.balaland.pj
        self.projectiles = []
        self.collided_projectiles = []

    def move(self):
        self.handle_pj_movement()
        self.handle_projectiles()

    def handle_pj_movement(self):
        pj_direction_x = self.get_pj_axis_movement(
            'x', pygame.K_a, pygame.K_d)
        pj_direction_y = self.get_pj_axis_movement(
            'y', pygame.K_w, pygame.K_s)

        if pj_direction_x:
            self.handle_pj_collisions('x', pj_direction_x)
        if pj_direction_y:
            self.handle_pj_collisions('y', pj_direction_y)
        self.pj.update_weapon_position()

    def get_pj_axis_movement(self, axis, negative_key, positive_key):
        pressed_keys = pygame.key.get_pressed()
        negative_held = pressed_keys[negative_key]
        positive_held = pressed_keys[positive_key]
        half_cam_size = self.cam.width // 2
        half_pj_size = self.pj.size // 2
        cam_axis = getattr(self.cam.pos, axis)
        speed = getattr(self.pj.speed, axis)
        negative_cam_margin = half_pj_size - half_cam_size
        positive_margin = self.cam.map_width - half_cam_size - half_pj_size
        if negative_held and positive_held:
            pj_direction = 0
        elif negative_held and cam_axis > negative_cam_margin:
            if cam_axis < (negative_cam_margin + speed):
                self.cam.move_pos_limit(axis, '-')
                pj_direction = 0
            else:
                pj_direction = -1
        elif positive_held and cam_axis < positive_margin:
            if cam_axis > (positive_margin - speed):
                self.cam.move_pos_limit(axis, '+')
                pj_direction = 0
            else:
                pj_direction = 1
        else:
            pj_direction = 0
        return pj_direction

    def handle_pj_collisions(self, axis, direction):
        new_cam_pos = (
            getattr(self.cam.pos, axis)
            + (direction * getattr(self.pj.speed, axis))
        )
        setattr(self.cam.pos, axis, new_cam_pos)
        tiles = self.balaland.get_drawable_tiles()
        solid_tiles = [t for t in tiles if t.solid]
        collide_tile = self.pj.rect.collidelist(solid_tiles)
        if collide_tile >= 0:
            side = 'width' if axis == 'x' else 'height'
            collide_rect = solid_tiles[collide_tile]
            collide_rect_axis = getattr(collide_rect, axis)
            collide_rect_size = getattr(collide_rect, side)
            pj_center = self.pj.get_center_position()
            pj_center_axis = getattr(pj_center, axis)
            pj_pos_axis = getattr(self.pj.pos, axis)
            negative_dist = abs(pj_center_axis - collide_rect_axis)
            positive_dist = abs(
                pj_center_axis - collide_rect_axis - collide_rect_size)
            if negative_dist < positive_dist:
                fixed_cam_pos = (
                    getattr(self.cam.pos, axis)
                    - abs(pj_pos_axis + self.pj.size - collide_rect_axis)
                )
                setattr(self.cam.pos, axis, fixed_cam_pos)
            else:
                fixed_cam_pos = (
                    getattr(self.cam.pos, axis)
                    + abs(collide_rect_axis + collide_rect_size - pj_pos_axis)
                )
                setattr(self.cam.pos, axis, fixed_cam_pos)

    def handle_projectiles(self):
        self.handle_projectiles_and_tiles()
        self.handle_projectiles_and_somebodies()

    def handle_projectiles_and_tiles(self):
        tiles = self.balaland.tile_map.get_tiles(
            self.cam.pos, self.cam.cam_tiles())
        solid_tiles = [t for t in tiles if t.solid]
        collided_projectiles = []
        for id_, projectile in enumerate(self.projectiles):
            collision = self.update_projectile_position(
                solid_tiles, projectile)
            if collision:
                collided_projectiles.append(projectile)
        self.clean_collided_projectiles(collided_projectiles)

    def clean_collided_projectiles(self, collided_projectiles):
        for projectile in collided_projectiles:
            collided_projectile = self.projectiles.pop(
                self.projectiles.index(projectile))
            self.collided_projectiles.append(collided_projectile)

    def update_projectile_position(self, solid_tiles, projectile):
        projectile.x += projectile.movement.x
        collision_x = self.projectile_collision('x', solid_tiles, projectile)
        projectile.y += projectile.movement.y
        collision_y = self.projectile_collision('y', solid_tiles, projectile)
        return collision_x or collision_y

    def projectile_collision(self, axis, solid_tiles, projectile):
        collide_tile = projectile.collidelist(solid_tiles)
        if collide_tile >= 0:
            side = 'width' if axis == 'x' else 'height'
            collide_rect = solid_tiles[collide_tile]
            collide_rect_axis = getattr(collide_rect, axis)
            collide_rect_size = getattr(collide_rect, side)
            projectile_center = projectile.get_center_map_pos()
            projectile_center_axis = getattr(projectile_center, axis)
            projectile_axis = getattr(projectile, axis)
            negative_dist = abs(projectile_center_axis - collide_rect_axis)
            positive_dist = abs(
                projectile_center_axis - collide_rect_axis - collide_rect_size)
            if negative_dist < positive_dist:
                fixed_projectile_axis = (
                    getattr(projectile, axis)
                    - abs(
                        projectile_axis
                        + projectile.size[0]
                        - collide_rect_axis
                    )
                )
                setattr(projectile, axis, fixed_projectile_axis)
            else:
                fixed_projectile_axis = (
                    getattr(projectile, axis)
                    + abs(
                        collide_rect_axis
                        + collide_rect_size
                        - projectile_axis
                    )
                )
                setattr(projectile, axis, fixed_projectile_axis)
            return True
        return False

    def handle_projectiles_and_somebodies(self):
        somebodies = self.balaland.tile_map.enemies
        collided_projectiles = []
        for id_, projectile in enumerate(self.projectiles):
            collided_sombody = projectile.collidelist(somebodies)
            if collided_sombody >= 0:
                somebody_rect = somebodies[collided_sombody]
                somebody_rect.hit()
                collided_projectiles.append(projectile)
        self.clean_collided_projectiles(collided_projectiles)


class Balaland:
    black = 0, 0, 0

    def __init__(self):
        pygame.init()
        pygame.event.set_grab(False)  # TODO: set true
        cursor = pygame.cursors.compile(
            CROSSHAIR, black='#', white='.', xor='o')
        pygame.mouse.set_cursor((24, 24), (11, 11), *cursor)
        self.tile_map = TileMap()
        self.cam = Cam(self.tile_map)
        self.pj = Pj(self.cam)
        self.clock = pygame.time.Clock()
        self.movement_handler = MovementHandler(self)

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
        projectile = ProjectileRect(
            center_map_pos.x, center_map_pos.y, mouse_pos, self.pj.pos)
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
            BalalandRect(
                tile.x - self.cam.pos.x, tile.y - self.cam.pos.y,
                tile.width, tile.color, tile.solid
            )
            for tile in tiles_in_cam
        )

    def draw_enemies(self):
        for e in self.tile_map.enemies:
            e_rect = BalalandRect(
                round(e.x - self.cam.pos.x), round(e.y - self.cam.pos.y),
                e.width, e.color, e.solid
            )
            pygame.draw.rect(self.cam.screen, e_rect.color, e_rect)

    def draw_pj(self):
        pygame.draw.rect(self.cam.screen, self.pj.rect.color, self.pj.rect)
        pygame.draw.rect(self.cam.screen, self.pj.weapon_color, self.pj.weapon)

    def draw_projectiles(self):
        for p in (
            self.movement_handler.projectiles
            + self.movement_handler.collided_projectiles
        ):
            p_rect = ProjectileRect(
                round(p.x - self.cam.pos.x), round(p.y - self.cam.pos.y))
            pygame.draw.rect(self.cam.screen, p_rect.color, p_rect)


if __name__ == '__main__':
    load_dotenv()
    balaland = Balaland()
    while True:
        balaland.update()
        balaland.clock.tick(int(os.environ.get('BL_CLOCK_TICK')))
