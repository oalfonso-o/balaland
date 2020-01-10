import pygame
import math

rad = math.pi / 180;


class Tile:

    def __init__(self, x=0, y=0, size=(200, 200), color=(0, 0, 0)):
        self.original_image = pygame.Surface(size, pygame.SRCALPHA)
        # self.original_image.fill((0, 0, 0))
        pygame.draw.rect(
            self.original_image,
            color,
            pygame.Rect((0, 0), size),
        )
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect_center = x + (size[0] / 2), y + (size[1] / 2)
        self.rect.center = self.rect_center
        self.x_relative = x - 500
        self.y_relative = y - 500
        self.angle = 0

    def update(self):
        self.angle += 1 % 360
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
        self.rect.center = x+500, y+500


def main():
    map_center = 500, 500
    clock = pygame.time.Clock()
    tile1 = Tile(x=0, y=0, size=(200, 200), color=(100, 0, 0))
    tile2 = Tile(x=200, y=0, size=(200, 200), color=(0, 100, 0))
    tile3 = Tile(x=0, y=200, size=(200, 200), color=(0, 0, 100))
    tile4 = Tile(x=200, y=200, size=(200, 200), color=(255, 0, 0))
    tiles = [tile1, tile2, tile3, tile4]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (500, 500), 3)
        for tile in tiles:
            tile.update()
            screen.blit(tile.image, tile.rect)
        pygame.display.update()
        clock.tick(40)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    main()
