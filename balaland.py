import sys
import pygame


class BalaRect(pygame.Rect):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size)
        self.color = color


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
                    tile_rect = BalaRect(
                        x * self.tile_size, y * self.tile_size, self.tile_size,
                        color
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
        self.size = 2  # radius from pj to end of cam in tiles
        self.pos = pygame.math.Vector2(0, 0)
        self.width = tile_map.tile_size * self.size + tile_map.tile_size
        self.screen = pygame.display.set_mode((self.width, self.width))
        self.map_width = tile_map.width * tile_map.tile_size
        self.map_height = tile_map.height * tile_map.tile_size

    def cam_tiles(self):
        return self.size * 2 + 1


class Pj:
    color = (100, 175, 220)

    def __init__(self, cam_width):
        self.speed = pygame.math.Vector2(10, 10)
        self.direction = pygame.math.Vector2(0, 0)
        self.size = 50
        self.pos = self._cam_centered_position(cam_width)
        self.rect = BalaRect(self.pos.x, self.pos.y, self.size, self.color)

    def _cam_centered_position(self, cam_width):
        center = (cam_width // 2) - (self.size // 2)
        return pygame.math.Vector2(center, center)


class Balaland:
    black = 0, 0, 0

    def __init__(self):
        self.tile_map = TileMap()
        self.cam = Cam(self.tile_map)
        self.pj = Pj(self.cam.width)
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
        self.cam.pos += self.get_pj_movement()

    def draw(self):
        self.cam.screen.fill(self.black)
        self.draw_map()
        pygame.draw.rect(self.cam.screen, self.pj.rect.color, self.pj.rect)
        pygame.display.flip()

    def draw_map(self):
        tiles_in_cam = self.tile_map.get_tiles(
            self.cam.pos, self.cam.cam_tiles())
        for tile in tiles_in_cam:
            screen_tile_pos = BalaRect(
                tile.x - self.cam.pos.x, tile.y - self.cam.pos.y,
                tile.width, tile.color,
            )
            pygame.draw.rect(
                self.cam.screen, screen_tile_pos.color, screen_tile_pos)

    def get_pj_movement(self):
        pressed_keys = pygame.key.get_pressed()
        a_held = pressed_keys[pygame.K_a]
        d_held = pressed_keys[pygame.K_d]
        w_held = pressed_keys[pygame.K_w]
        s_held = pressed_keys[pygame.K_s]
        half_cam_size = self.cam.width // 2
        half_pj_size = self.pj.size // 2
        if a_held and d_held:
            self.pj.direction.x = 0
        elif a_held and self.cam.pos.x > (0 - half_cam_size + half_pj_size):
            self.pj.direction.x = -1
        elif d_held and self.cam.pos.x < (self.cam.map_width - half_cam_size - half_pj_size):  # NOQA E501
            self.pj.direction.x = 1
        else:
            self.pj.direction.x = 0

        if w_held and s_held:
            self.pj.direction.y = 0
        elif w_held and self.cam.pos.y > (0 - half_cam_size + half_pj_size):
            self.pj.direction.y = -1
        elif s_held and self.cam.pos.y < (self.cam.map_height - half_cam_size - half_pj_size):  # NOQA E501
            self.pj.direction.y = 1
        else:
            self.pj.direction.y = 0

        return pygame.math.Vector2(
            int(self.pj.direction.x * self.pj.speed.x),
            int(self.pj.direction.y * self.pj.speed.y),
        )


if __name__ == '__main__':
    pygame.init()
    balaland = Balaland()
    while True:
        balaland.run()
        balaland.clock.tick(40)
