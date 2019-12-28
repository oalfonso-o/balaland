import sys
import pygame


class BalaRect(pygame.Rect):
    def __init__(self, x, y, size, color, solid=False):
        super().__init__(int(x), int(y), size, size)
        self.color = color
        self.solid = solid


class TileMap:
    tile_color = 220, 200, 100
    white = 255, 255, 255

    def __init__(self):
        self.tile_size = 200
        self.safety_tiles = 1
        self.map = self.load_map()
        self.width = len(self.map)
        self.height = len(self.map)

    def load_map(self, map_file='tile_map.tm'):
        map_ = []
        with open(map_file, 'r') as fd:
            for y, file_line in enumerate(fd):
                map_row = []
                for x, file_tile in enumerate(file_line.replace('\n', '')):
                    color = self.tile_color if int(file_tile) else self.white
                    solid = bool(int(file_tile))
                    tile_rect = BalaRect(
                        x * self.tile_size, y * self.tile_size, self.tile_size,
                        color, solid
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
        self.size = 3  # radius from pj to end of cam in tiles
        self.pos = pygame.math.Vector2(-30, -30)
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


class Pj:
    color = (100, 175, 220)

    def __init__(self, cam):
        self.speed = pygame.math.Vector2(20, 20)
        self.direction = pygame.math.Vector2(0, 0)
        self.size = 50
        self.pos = self._cam_centered_position(cam.width)
        self.rect = BalaRect(
            self.pos.x, self.pos.y, self.size, self.color, True)
        cam.update_limit_pos(self.size)

    def _cam_centered_position(self, cam_width):
        center = (cam_width // 2) - (self.size // 2)
        return pygame.math.Vector2(center, center)

    def get_center_position(self):
        return self.pos + pygame.math.Vector2(self.size // 2, self.size // 2)

    def get_bottom_right_position(self):
        return self.pos + pygame.math.Vector2(self.size, self.size)


class Balaland:
    black = 0, 0, 0

    def __init__(self):
        self.tile_map = TileMap()
        self.cam = Cam(self.tile_map)
        self.pj = Pj(self.cam)
        self.clock = pygame.time.Clock()

    def run(self):
        self.handle_events()
        self.handle_movement()
        self.draw()

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def handle_movement(self):
        pj_direction_x = self.get_pj_single_axis_movement(
            'x', pygame.K_a, pygame.K_d)
        pj_direction_y = self.get_pj_single_axis_movement(
            'y', pygame.K_w, pygame.K_s)

        if pj_direction_x:
            self.handle_x_collisions(pj_direction_x)
        if pj_direction_y:
            self.handle_y_collisions(pj_direction_y)

    def handle_x_collisions(self, pj_direction_x):
        self.cam.pos.x += pj_direction_x * self.pj.speed.x
        x_tiles = self.get_drawable_tiles()
        x_solid_tiles = [t for t in x_tiles if t.solid]
        x_collide_tile = self.pj.rect.collidelist(x_solid_tiles)
        if x_collide_tile >= 0:
            x_collide_rect = x_solid_tiles[x_collide_tile]
            pj_center = self.pj.get_center_position()
            left_dist = abs(pj_center.x - x_collide_rect.x)
            right_dist = abs(
                pj_center.x - x_collide_rect.x - x_collide_rect.width)
            if left_dist < right_dist:
                # collision on left side, correct it
                self.cam.pos.x -= (
                    abs(self.pj.pos.x + self.pj.size - x_collide_rect.x))
            else:
                # collision on right side, correct it
                self.cam.pos.x += abs(
                    x_collide_rect.x + x_collide_rect.width - self.pj.pos.x)

    def handle_y_collisions(self, pj_direction_y):
        self.cam.pos.y += pj_direction_y * self.pj.speed.y
        y_tiles = self.get_drawable_tiles()
        y_solid_tiles = [t for t in y_tiles if t.solid]
        y_collide_tile = self.pj.rect.collidelist(y_solid_tiles)
        if y_collide_tile >= 0:
            y_collide_rect = y_solid_tiles[y_collide_tile]
            pj_center = self.pj.get_center_position()
            top_dist = abs(pj_center.y - y_collide_rect.y)
            bottom_dist = abs(
                pj_center.y - y_collide_rect.y - y_collide_rect.height)
            if top_dist < bottom_dist:
                # collision on top side, correct it
                self.cam.pos.y -= (
                    abs(self.pj.pos.y + self.pj.size - y_collide_rect.y))
            else:
                # collision on bottom side, correct it
                self.cam.pos.y += abs(
                    y_collide_rect.y + y_collide_rect.height - self.pj.pos.y)

    def draw(self):
        self.cam.screen.fill(self.black)
        tiles = self.get_drawable_tiles()
        self.draw_map(tiles)
        pygame.draw.rect(self.cam.screen, self.pj.rect.color, self.pj.rect)
        pygame.display.flip()

    def get_drawable_tiles(self):
        tiles_in_cam = self.tile_map.get_tiles(
            self.cam.pos, self.cam.cam_tiles())
        drawable_tiles = [
            BalaRect(
                tile.x - self.cam.pos.x, tile.y - self.cam.pos.y,
                tile.width, tile.color, tile.solid
            )
            for tile in tiles_in_cam
        ]
        return drawable_tiles

    def draw_map(self, tiles):
        for tile in tiles:
            pygame.draw.rect(self.cam.screen, tile.color, tile)

    def get_pj_single_axis_movement(self, axis, negative_key, positive_key):
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


if __name__ == '__main__':
    pygame.init()
    balaland = Balaland()
    while True:
        balaland.run()
        balaland.clock.tick(40)
