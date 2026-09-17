import pygame
from circleshape import CircleShape
from constants import *


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.lifetime = SHOT_LIFETIME_SECONDS

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(surface=screen, color=(255, 255, 255), center=self.position, radius=self.radius, width=LINE_WIDTH)

    def wrap_screen(self) -> None:
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_screen()

        self.lifetime -= dt

        if self.lifetime <= 0:
            self.kill()