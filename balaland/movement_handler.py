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
