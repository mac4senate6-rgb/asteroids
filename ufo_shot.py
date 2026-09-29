import pygame
from circleshape import CircleShape
from constants import *


class UFOShot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, UFO_SHOT_RADIUS)
        self.lifetime = UFO_SHOT_LIFETIME_SECONDS

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.kill()


