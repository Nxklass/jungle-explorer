import pygame
import logging
from jungle_explorer.levels import Platform, MovingPlatform
from jungle_explorer.config import BASE_WIDTH, BASE_HEIGHT, JUMP_SOUND
from jungle_explorer.assets import PLAYER_FRAMES, JUMP_FRAME

class Player(pygame.sprite.Sprite):
    """Spielerklasse mit Bewegung und Animation."""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.frames = PLAYER_FRAMES
        self.jump_frame = JUMP_FRAME
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 250
        self.jump_power = -650
        self.gravity = 1500
        self.on_ground = False
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.facing_right = True
        self.is_jumping = False
        self.coyote_time = 0.1  # 100 ms Kulanzzeit nach dem Verlassen einer Kante
        self.coyote_timer = 0
        self.jump_buffer = 0.1  # 100 ms Eingabepuffer für Sprünge
        self.jump_buffer_timer = 0
        self.on_moving_platform = None  # Aktuelle bewegliche Plattform
        self.relative_x = None  # Relative X-Position auf der Plattform

    def handle_input(self, event_list: list) -> bool:
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        moving = False
        for event in event_list:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.jump_buffer_timer = self.jump_buffer  # Sprungeingabe puffern
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.facing_right = True
            moving = True
        return moving

    def apply_gravity(self, dt: float) -> None:
        if not self.on_ground:
            self.velocity_y += self.gravity * dt
        else:
            self.velocity_y = 0

    def move(self, dt: float) -> None:
        if self.on_moving_platform and self.on_ground and not self.is_jumping:
            self.rect.x += self.on_moving_platform.delta_x
        # Spieler horizontal gemäß Eingabe bewegen
        self.rect.x += int(self.velocity_x * dt)
        # Relative Position nur bei aktiver Eingabe anpassen
        if self.on_moving_platform and self.on_ground and self.velocity_x != 0:
            self.relative_x += self.velocity_x * dt
            logging.debug("Player relative_x updated due to input: %f", self.relative_x)

    def check_collisions_x(self, platforms: pygame.sprite.Group) -> None:
        # Nur nahe Plattformen für Kollision prüfen
        proximity_rect = self.rect.inflate(100, 100)  # Suchbereich um 100 Pixel erweitern
        nearby_platforms = [p for p in platforms if proximity_rect.colliderect(p.rect)]
        collisions = pygame.sprite.spritecollide(self, nearby_platforms, False)
        for platform in collisions:
            if getattr(platform, 'is_ground', False):
                continue
            collision_rect = platform.collision_rect if isinstance(platform, MovingPlatform) else platform.rect
            if self.velocity_x > 0:
                if self.rect.right > collision_rect.left:
                    self.rect.right = collision_rect.left
                    self.velocity_x = 0
            elif self.velocity_x < 0:
                if self.rect.left < collision_rect.right:
                    self.rect.left = collision_rect.right
                    self.velocity_x = 0
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > BASE_WIDTH:
            self.rect.right = BASE_WIDTH
            self.velocity_x = 0

    def check_collisions_y(self, platforms: pygame.sprite.Group, dt: float) -> None:
        self.rect.y += int(self.velocity_y * dt)
        # Nur nahe Plattformen für Kollision prüfen
        proximity_rect = self.rect.inflate(100, 100)  # Suchbereich um 100 Pixel erweitern
        nearby_platforms = [p for p in platforms if proximity_rect.colliderect(p.rect)]
        was_on_ground = self.on_ground
        self.on_ground = False
        previous_moving_platform = self.on_moving_platform
        self.on_moving_platform = None

        logging.debug("Checking collisions, on_ground initially: %s", self.on_ground)

        for platform in nearby_platforms:
            collision_rect = platform.collision_rect if isinstance(platform, MovingPlatform) else platform.rect
            horizontal_overlap = (
                self.rect.left < collision_rect.right and
                self.rect.right > collision_rect.left
            )
            vertical_tolerance = max(6, int(abs(self.velocity_y * dt)) + 2)
            if self.velocity_y >= 0:
                if (horizontal_overlap and
                    self.rect.bottom >= collision_rect.top - 5 and
                    self.rect.bottom <= collision_rect.top + vertical_tolerance):
                    self.rect.bottom = collision_rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    logging.debug("Landed on platform at y=%d", collision_rect.top)
                    self.coyote_timer = self.coyote_time
                    if isinstance(platform, MovingPlatform):
                        self.on_moving_platform = platform
                        if previous_moving_platform != platform:
                            self.relative_x = self.rect.x - platform.rect.x
                            logging.debug("Player landed on moving platform, relative_x=%f", self.relative_x)
            elif self.velocity_y < 0:
                if (horizontal_overlap and
                    self.rect.top <= collision_rect.bottom and
                    self.rect.top >= collision_rect.bottom - vertical_tolerance):
                    self.rect.top = collision_rect.bottom
                    self.velocity_y = 0

        ground_level = BASE_HEIGHT - 35
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.velocity_y = 0
            self.on_ground = True
            self.is_jumping = False
            logging.debug("Landed on ground at y=%d", ground_level)
            self.coyote_timer = self.coyote_time
            self.on_moving_platform = None
            self.relative_x = None

        if not self.on_ground and was_on_ground and not self.is_jumping:
            self.coyote_timer = self.coyote_time

        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.jump()
            self.jump_buffer_timer = 0

        if self.on_moving_platform and self.on_ground and self.relative_x is not None:
            self.rect.x = int(self.on_moving_platform.rect.x + self.relative_x)
            self.rect.bottom = self.on_moving_platform.collision_rect.top
            logging.debug("Player position synchronized with platform, x=%d, y=%d", self.rect.x, self.rect.bottom)

    def animate(self, moving: bool, dt: float) -> None:
        if self.is_jumping or self.velocity_y < 0:
            self.image = self.jump_frame
        else:
            if moving:
                self.animation_timer += self.animation_speed * (60 * dt)  # Auf 60 FPS normieren
                if self.animation_timer >= 1:
                    self.animation_timer -= 1
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
            else:
                self.current_frame = 0
                self.animation_timer = 0
            self.image = self.frames[self.current_frame]

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def jump(self) -> None:
        if self.on_ground or self.coyote_timer > 0:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True
            self.coyote_timer = 0  # Kulanzzeit beim Sprung zurücksetzen
            self.on_moving_platform = None  # Plattformbindung beim Sprung lösen
            self.relative_x = None  # Relative Position zurücksetzen
            if JUMP_SOUND:
                JUMP_SOUND.play()
            logging.info("Player jumps: velocity_y=%d", self.velocity_y)
        else:
            logging.debug("Jump attempted but not on ground, on_ground=%s, coyote_timer=%f",
                         self.on_ground, self.coyote_timer)

    def update(self, platforms: pygame.sprite.Group, dt: float, event_list: list) -> None:
        try:
            moving = self.handle_input(event_list)
            self.apply_gravity(dt)
            self.move(dt)
            self.check_collisions_x(platforms)
            self.check_collisions_y(platforms, dt)
            # Zeitgeber aktualisieren
            if self.coyote_timer > 0:
                self.coyote_timer -= dt
            if self.jump_buffer_timer > 0:
                self.jump_buffer_timer -= dt
            self.animate(moving, dt)
        except Exception as e:
            logging.error("Error in player update: %s", str(e))
            raise