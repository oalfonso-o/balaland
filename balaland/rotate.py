import sys
import math

import pygame

rad = math.pi / 180
map_size = 1000
map_size_half = int(map_size / 2)
sensibility = 4


class Tile:

    def __init__(self, x=0, y=0, size=(200, 200), color=(0, 0, 0)):
        self.original_image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(
            self.original_image,
            color,
            pygame.Rect((0, 0), size),
        )
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect_center = x + (size[0] / 2), y + (size[1] / 2)
        self.rect.center = self.rect_center
        self.x_relative = x - map_size_half
        self.y_relative = y - map_size_half
        self.angle = 0

    def update(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, - self.angle)
        self.rect = self.image.get_rect()
        x = (
            (self.x_relative * math.cos(self.angle * rad))
            - (self.y_relative * math.sin(self.angle * rad))
        )
        y = (
            (self.y_relative * math.cos(self.angle * rad))
            + (self.x_relative * math.sin(self.angle * rad))
        )
        self.rect.center = x + map_size_half, y + map_size_half


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                pygame.event.set_grab(not pygame.event.get_grab())


def main():
    pygame.init()
    pygame.event.set_grab(True)
    screen = pygame.display.set_mode((map_size, map_size))
    clock = pygame.time.Clock()
    tile1 = Tile(x=0, y=0, size=(200, 200), color=(100, 0, 0))
    tile2 = Tile(x=200, y=0, size=(200, 200), color=(0, 100, 0))
    tile3 = Tile(x=0, y=200, size=(200, 200), color=(0, 0, 100))
    tile4 = Tile(x=200, y=200, size=(200, 200), color=(255, 0, 0))
    tiles = [tile1, tile2, tile3, tile4]
    mouse_rel_x = 0
    pygame.mouse.set_visible(False)
    while True:
        handle_events()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] > map_size_half:
            pygame.mouse.set_pos(mouse_pos[0], map_size_half)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((255, 255, 255))
        pygame.draw.circle(
            screen, (0, 0, 0), (map_size_half, map_size_half), 3
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (map_size_half - 5, mouse_pos[1] - 5),
            (map_size_half + 5, mouse_pos[1] + 5),
            1,
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (map_size_half + 5, mouse_pos[1] - 5),
            (map_size_half - 5, mouse_pos[1] + 5),
            1,
        )
        mouse_rel_x += pygame.mouse.get_rel()[0]
        dist_x = map_size_half - mouse_rel_x
        angle = (dist_x / sensibility)
        for tile in tiles:
            tile.update(angle)
            screen.blit(tile.image, tile.rect)
        pygame.display.update()

        clock.tick(40)


if __name__ == '__main__':
    main()
