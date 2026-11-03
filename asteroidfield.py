import random
#use it to randomly choose which edge an asteroid enters from, its speed, etc.
from collections.abc import Callable
#use this only for a type hint. It describes a function that can be stored inside another data structure

import pygame

from logger import log_event
from asteroid import Asteroid
from constants import *

Edge = tuple[pygame.Vector2, Callable[[float], pygame.Vector2]]

class AsteroidField(pygame.sprite.Sprite):
    containers: pygame.sprite.Group

    edges: list[Edge] = [
        (
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ),
        (
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ),
        (
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ),
        (
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ),
    ]

    def __init__(
            self,
            asteroid_group: pygame.sprite.Group,
            groups: tuple[pygame.sprite.Group, ...] | None = None,
            asteroid_groups: tuple[pygame.sprite.Group, ...] | None = None,
            log_events: bool = True,
    ) -> None:
        if groups is not None:  # Check whether explicit groups were provided.
            pygame.sprite.Sprite.__init__(self, *groups)  # Register the field with the supplied groups.
        else:  # Otherwise, use the existing gameplay containers.
            pygame.sprite.Sprite.__init__(self, self.containers)  # Preserve normal gameplay registration.

        self.asteroid_group = asteroid_group  # Store the asteroid group monitored for wave progression.
        self.asteroid_groups = asteroid_groups  # Store the registration groups for newly spawned asteroids.
        self.log_events = log_events  # Store whether gameplay events should be recorded.

        self.wave_size = 4  # Set the initial asteroid count.
        self.wave_timer = 0.0  # Initialize the wave timer.
        self.wave_delay = 2.0  # Set the delay between waves.
        self.speed_multiplier = 1.0  # Initialize the speed multiplier.
        self.wave_number = 0  # Initialize the wave counter.

    def spawn(self, radius: float, position: pygame.Vector2, velocity: pygame.Vector2) -> None:
        asteroid = Asteroid(position.x, position.y, radius, groups=self.asteroid_groups, log_events=self.log_events)
        asteroid.velocity = velocity

    def spawn_wave(self) -> None:
        for _ in range(self.wave_size):
            edge = random.choice(self.edges)

            speed = random.randint(40, 100)
            speed *= self.speed_multiplier

            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))

            position = edge[1](random.uniform(0, 1))

            self.spawn(ASTEROID_MAX_RADIUS, position, velocity)

    def update(self, dt: float) -> None:
        if len(self.asteroid_group) > 0:
            self.wave_timer = 0.0
            return

        self.wave_timer += dt

        if self.wave_timer >= self.wave_delay:
            self.wave_number += 1
            self.spawn_wave()

            if self.log_events:
                log_event("wave_start", wave=self.wave_number, asteroid_count=self.wave_size, speed_multiplier=self.speed_multiplier)

            self.wave_timer = 0.0
            self.wave_size = min(self.wave_size + 2, 10)
            self.speed_multiplier = min(self.speed_multiplier + 0.05, 10)

