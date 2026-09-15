import random
from logger import log_event

from circleshape import CircleShape
import pygame
from constants import *


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

        self.points: list[pygame.Vector2] = []
        asteroid_points = 16
        for i in range(asteroid_points):
            angle = 360 / asteroid_points * i
            direction = pygame.Vector2(0, 1).rotate(angle)
            distance_multiplier = random.uniform(0.75, 1.15)
            point = direction * self.radius * distance_multiplier
            self.points.append(point)

    def draw(self, screen: pygame.Surface) -> None:
        world_points = []
        for point in self.points:
            world_points.append(self.position + point)

        pygame.draw.polygon(screen, (255, 255, 255), world_points, LINE_WIDTH)

    def split(self) -> None:
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")

        angle = random.uniform(20, 50)

        velocity1 = self.velocity.rotate(angle)
        velocity2 = self.velocity.rotate(-angle)

        smaller_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid_one = Asteroid(self.position.x, self.position.y, smaller_radius)
        asteroid_two = Asteroid(self.position.x, self.position.y, smaller_radius)

        asteroid_one.velocity = velocity1 * 1.2
        asteroid_two.velocity = velocity2 * 1.2

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_screen()

    def wrap_screen(self) -> None:
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius