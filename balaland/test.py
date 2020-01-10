import os
import sys
from dotenv import load_dotenv

import pygame

import balaland
from balaland.cursors.standard import CROSSHAIR


class BalalandGame:
    black = 0, 0, 0
    white = 255, 255, 255

    def __init__(self):
        pygame.init()
        pygame.event.set_grab(False)  # TODO: set true
        cursor = pygame.cursors.compile(
            CROSSHAIR, black='#', white='.', xor='o')
        pygame.mouse.set_cursor((24, 24), (11, 11), *cursor)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((200, 200))
        self.original_surface = pygame.Surface((40, 40))
        self.surface = self.original_surface
        self.rect = self.surface.get_rect()
        self.angle = 0
        # s = pygame.Surface((40,40))  # the size of your rect
        # s.set_alpha(128)                # alpha level
        # s.fill((255,255,255))           # this fills the entire surface
        # self.original_surface.blit(s, (0,0))    # (0,0) are the top-left coordinates
        # pygame.draw.rect(self.original_surface, self.white, pygame.rect.Rect(0,0,0,0))
        # self.rect.center = (100, 100)

    def run(self):
        while True:
            self.handle_events()
            self.screen.fill(self.white)
            self.angle += 1 % 360
            self.surface = pygame.transform.rotate(self.original_surface, self.angle)
            self.rect = self.surface.get_rect()
            print(self.rect)
            self.screen.blit(self.surface, self.rect)
            # x, y = self.rect.center
            # self.rect = self.surface.get_rect()
            # self.rect.center = (x, y)

            pygame.display.flip()
            pygame.display.update()
            self.clock.tick(int(os.environ.get('BL_CLOCK_TICK')))

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


load_dotenv()
game = BalalandGame()
game.run()
