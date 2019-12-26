import sys
import pygame

pygame.init()

black = 0, 0, 0

pj_pos = pygame.math.Vector2(0, 0)
pj_speed = pygame.math.Vector2(10, 10)
pj_direction = pygame.math.Vector2(0, 0)
pj_size = 50
pj_rect = pygame.Rect(pj_pos.x, pj_pos.y, pj_size, pj_size)
pj_color = 255, 255, 255

tile_map = []
tile_size = 200

cam_size = 2  # radius from pj to end of cam in tiles
cam_pos = pygame.math.Vector2(0, 0)
cam_width = tile_size * cam_size + tile_size
cam_screen = pygame.display.set_mode((cam_width, cam_width))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pressed_keys = pygame.key.get_pressed()
    a_held = pressed_keys[pygame.K_a]
    d_held = pressed_keys[pygame.K_d]
    w_held = pressed_keys[pygame.K_w]
    s_held = pressed_keys[pygame.K_s]
    if a_held and d_held:
        pj_direction.x = 0
    elif a_held:
        pj_direction.x = -1
    elif d_held:
        pj_direction.x = 1
    else:
        pj_direction.x = 0

    if w_held and s_held:
        pj_direction.y = 0
    elif w_held:
        pj_direction.y = -1
    elif s_held:
        pj_direction.y = 1
    else:
        pj_direction.y = 0

    pj_movement = (
        int(pj_direction.x * pj_speed.x),
        int(pj_direction.y * pj_speed.y),
    )
    pj_rect = pj_rect.move(pj_movement)

    cam_screen.fill(black)
    pygame.draw.rect(cam_screen, pj_color, pj_rect)
    pygame.display.flip()
    clock.tick(40)
