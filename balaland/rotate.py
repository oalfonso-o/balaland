import sys
import math
import copy

import pygame

RAD = math.pi / 180
MAP_SIZE = 1000
MAP_SIZE_HALF = int(MAP_SIZE / 2)
SENSIBILITY = 4


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
        self.x_relative = x - MAP_SIZE_HALF
        self.y_relative = y - MAP_SIZE_HALF
        self.angle = 0


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
    screen = pygame.display.set_mode((MAP_SIZE, MAP_SIZE))
    clock = pygame.time.Clock()
    tile1 = Tile(x=0, y=0, size=(200, 200), color=(100, 0, 0))
    tile2 = Tile(x=200, y=0, size=(200, 200), color=(0, 100, 0))
    tile3 = Tile(x=0, y=200, size=(200, 200), color=(0, 0, 100))
    tile4 = Tile(x=200, y=200, size=(200, 200), color=(255, 0, 0))
    tiles = [tile1, tile2, tile3, tile4]
    mouse_rel_x = 0
    pygame.mouse.set_visible(False)
    pj = None
    while True:
        handle_events()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] > MAP_SIZE_HALF:
            pygame.mouse.set_pos(mouse_pos[0], MAP_SIZE_HALF)
            mouse_pos[1] = MAP_SIZE_HALF

        screen.fill((255, 255, 255))
        mouse_rel_x += pygame.mouse.get_rel()[0]
        dist_x = MAP_SIZE_HALF - mouse_rel_x
        angle = (dist_x / SENSIBILITY)
        for tile in tiles:
            ctile = copy.copy(tile)
            x_relative = ctile.x - pj.x
            y_relative = ctile.y - pj.y
            ctile.image = pygame.transform.rotate(ctile.original_image, -angle)
            rect = ctile.image.get_rect()
            ctile.x = rect.x
            ctile.y = rect.y
            x = (
                (x_relative * math.cos(angle * RAD))
                - (y_relative * math.sin(angle * RAD))
            )
            y = (
                (y_relative * math.cos(angle * RAD))
                + (x_relative * math.sin(angle * RAD))
            )
            ctile.center = x + pj.x, y + pj.y

            screen.blit(ctile.image, ctile.rect)

        pygame.draw.line(
            screen,
            (0, 0, 0),
            (MAP_SIZE_HALF - 5, mouse_pos[1] - 5),
            (MAP_SIZE_HALF + 5, mouse_pos[1] + 5),
            1,
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (MAP_SIZE_HALF + 5, mouse_pos[1] - 5),
            (MAP_SIZE_HALF - 5, mouse_pos[1] + 5),
            1,
        )
        pygame.display.update()

        clock.tick(40)


if __name__ == '__main__':
    main()
