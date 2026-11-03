import pygame
import random
from constants import *
from asteroidfield import AsteroidField
from ufo import LargeUFO, SmallUFO


class AttractSimulation:
    def __init__(
            self,
            large_ufo_sound: pygame.mixer.Sound,
            small_ufo_sound: pygame.mixer.Sound,
            ufo_channel: pygame.mixer.Channel
    ) -> None:

        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        self.ufo_shots = pygame.sprite.Group()

        self.asteroid_groups = (self.asteroids, self.updatable, self.drawable)
        self.ufo_groups = (self.ufos, self.updatable, self.drawable)
        self.ufo_shot_groups = (self.ufo_shots, self.updatable, self.drawable)
        self.asteroid_field = AsteroidField(
            self.asteroids,
            groups=(self.updatable, ),
            asteroid_groups=self.asteroid_groups,
            log_events=False
        )

        self.large_ufo_sound = large_ufo_sound
        self.small_ufo_sound = small_ufo_sound
        self.ufo_channel = ufo_channel

        self.ufo_spawn_timer = 3.0

    def spawn_ufo(self) -> None:

        spawn_from_left = random.choice([True, False])

        ufo_class = random.choice([SmallUFO, LargeUFO])

        ufo_sound = self.large_ufo_sound if ufo_class is LargeUFO else self.small_ufo_sound
        spawn_radius = UFO_LARGE_RADIUS if ufo_class is LargeUFO else UFO_SMALL_RADIUS
        spawn_y = random.uniform(spawn_radius, SCREEN_HEIGHT - spawn_radius)

        if spawn_from_left:
            spawn_x = -spawn_radius
            horizontal_speed = UFO_SPEED
        else:
            spawn_x = SCREEN_WIDTH + spawn_radius
            horizontal_speed = -UFO_SPEED

        new_ufo = ufo_class(
            spawn_x, spawn_y,
            ufo_sound, self.ufo_channel,
            groups=self.ufo_groups, shot_groups=self.ufo_shot_groups,
            shot_speed = 350.0, shot_lifetime = 2.5
        )


        new_ufo.velocity = pygame.Vector2(horizontal_speed, 0)

        self.ufo_spawn_timer = 3.0

    def check_collisions(self) -> None:
        for shot in list(self.ufo_shots):
            for asteroid in list(self.asteroids):
                if asteroid.collides_projectile(shot):
                    shot.kill()
                    asteroid.split()
                    break

        for asteroid in list(self.asteroids):
            for enemy_ufo in list(self.ufos):
                if asteroid.collides_with(enemy_ufo):
                    enemy_ufo.kill()
                    break

    def update(self, dt: float) -> None:
        self.updatable.update(dt)
        if len(self.ufos) == 0:
            self.ufo_spawn_timer = max(0.0, self.ufo_spawn_timer - dt)

            if self.ufo_spawn_timer <= 0:
                self.spawn_ufo()

        self.check_collisions()

    def draw(self, screen: pygame.Surface) -> None:
        for sprite in self.drawable:
            sprite.draw(screen)

    def cleanup(self) -> None:
        for enemy_ufo in list(self.ufos):
            enemy_ufo.kill()

        for sprite in list(self.updatable):
            sprite.kill()

        self.ufo_spawn_timer = 3.0