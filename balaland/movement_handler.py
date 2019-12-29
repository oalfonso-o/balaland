import pygame


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
        self.handle_pj_movement_axis('x', pj_direction_x)
        self.handle_pj_movement_axis('y', pj_direction_y)
        self.pj.update_weapon_position()

    def get_pj_axis_movement(self, axis, negative_key, positive_key):
        pressed_keys = pygame.key.get_pressed()
        negative_held = pressed_keys[negative_key]
        positive_held = pressed_keys[positive_key]
        half_cam_size = self.cam.width // 2
        half_pj_size = self.pj.width // 2
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

    def handle_pj_movement_axis(self, axis, direction):
        new_cam_pos = (
            getattr(self.cam.pos, axis)
            + (direction * getattr(self.pj.speed, axis))
        )
        setattr(self.cam.pos, axis, new_cam_pos)
        solid_tiles = self.balaland.get_drawable_solid_tiles()
        self.rect_collision(axis, solid_tiles, self.pj, self.cam.pos)

    def rect_collision(
        self, axis, collidable_rects, moving_rect, vector_to_fix_pos
    ):
        collide_rect_id = moving_rect.collidelist(collidable_rects)
        if collide_rect_id >= 0:
            side = 'width' if axis == 'x' else 'height'
            collide_rect = collidable_rects[collide_rect_id]
            collide_rect_axis = getattr(collide_rect, axis)
            collide_rect_size = getattr(collide_rect, side)
            moving_rect_center_axis = getattr(moving_rect.center_pos, axis)
            moving_rect_axis = getattr(moving_rect, axis)
            moving_rect_size = getattr(moving_rect, side)
            vector_to_fix_pos_axis = getattr(vector_to_fix_pos, axis)
            negative_dist = abs(moving_rect_center_axis - collide_rect_axis)
            positive_dist = abs(
                + moving_rect_center_axis
                - collide_rect_axis
                - collide_rect_size
            )
            if negative_dist < positive_dist:
                moving_rect_axis_fixed = (
                    vector_to_fix_pos_axis
                    - abs(
                        + moving_rect_axis
                        + moving_rect_size
                        - collide_rect_axis
                    )
                )
            else:
                moving_rect_axis_fixed = (
                    vector_to_fix_pos_axis
                    + abs(
                        - moving_rect_axis
                        + collide_rect_size
                        + collide_rect_axis
                    )
                )
            setattr(vector_to_fix_pos, axis, moving_rect_axis_fixed)
            return True
        return False

    def handle_projectiles(self):
        self.projectile_collision(self.projectile_tile_collision)
        self.projectile_collision(self.projectile_living_collision)

    def projectile_collision(self, collision_callback):
        collided_projectiles = []
        for id_, projectile in enumerate(self.projectiles):
            if collision_callback(projectile):
                collided_projectiles.append(projectile)
        self.clean_collided_projectiles(collided_projectiles)

    def projectile_tile_collision(self, projectile):
        tiles = self.balaland.tile_map.get_tiles(
            self.cam.pos, self.cam.cam_tiles())
        solid_tiles = [t for t in tiles if t.solid]
        projectile.x += projectile.movement.x
        collision_x = self.rect_collision(
            'x', solid_tiles, projectile, projectile)
        projectile.y += projectile.movement.y
        collision_y = self.rect_collision(
            'y', solid_tiles, projectile, projectile)
        return collision_x or collision_y

    def projectile_living_collision(self, projectile):
        livings = self.balaland.tile_map.enemies
        collided_living = projectile.collidelist(livings)
        if collided_living >= 0:
            somebody_rect = livings[collided_living]
            somebody_rect.hit()
            return True
        return False

    def clean_collided_projectiles(self, collided_projectiles):
        for projectile in collided_projectiles:
            collided_projectile = self.projectiles.pop(
                self.projectiles.index(projectile))
            self.collided_projectiles.append(collided_projectile)
