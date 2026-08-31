from pygame.surface import Surface
import random
from logger import log_event

from circleshape import CircleShape
import pygame
from constants import *


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(surface=screen, color=(255, 255, 255), center=self.position, radius=self.radius, width=LINE_WIDTH)

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