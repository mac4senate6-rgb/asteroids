import random
from logger import log_event

from circleshape import CircleShape
from asteroid_shapes import ASTEROID_SHAPES
import pygame
from constants import *


class Asteroid(CircleShape):
    def __init__(
            self,
            x: float,
            y: float,
            radius: float,
            groups: tuple[pygame.sprite.Group, ...] | None=None,
            log_events: bool=True
    ):
        super().__init__(x, y, radius, groups=groups)
        self.log_events = log_events

        selected_shape = random.choice(ASTEROID_SHAPES)

        self.original_points: list[pygame.Vector2] = [point * self.radius for point in selected_shape]
        self.points: list[pygame.Vector2] = [point.copy() for point in self.original_points]
        self.spin_direction = random.choice((-1, 1))
        self.rotation_speed = 90.0
        self.angle = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        world_points = []
        for point in self.points:
            world_points.append(self.position + point)

        pygame.draw.polygon(screen, (255, 255, 255), world_points, LINE_WIDTH)

    def collides_projectile(self, projectile: CircleShape) -> bool:
        maximum_distance = max(point.length() for point in self.points)
        center_distance = self.position.distance_to(projectile.position)
        if center_distance > maximum_distance + projectile.radius:
            return False

        vertices = [self.position + point for point in self.points] # Convert the asteroid's relative vertices into screen coordinates.
        projectile_center = projectile.position
        inside = False

        for index in range(len(vertices)):
            start = vertices[index]
            end = vertices[(index + 1) % len(vertices)]

            if (start.y > projectile_center.y) != (end.y > projectile_center.y):
                intersection_x = (
                        start.x
                        + (projectile_center.y - start.y)
                        * (end.x - start.x)
                        / (end.y - start.y)
                )

                if projectile_center.x < intersection_x:
                    inside = not inside

            edge = end - start
            edge_length_squared = edge.length_squared()

            if edge_length_squared == 0:
                closest_point = start
            else:
                projection = (projectile_center - start).dot(edge) / edge_length_squared
                projection = max(0.0, min(1.0, projection))
                closest_point = start + projection * edge

            distance_squared = projectile_center.distance_squared_to(closest_point)
            radius_squared = projectile.radius * projectile.radius

            if distance_squared <= radius_squared:
                return True

        return inside

    def split(self) -> None:
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        if self.log_events:
            log_event("asteroid_split")

        angle1 = random.uniform(0.0, 360)
        angle2 = random.uniform(0.0, 360)

        speed = self.velocity.length() * 1.2

        velocity1 = pygame.Vector2(speed, 0).rotate(angle1)
        velocity2 = pygame.Vector2(speed, 0).rotate(angle2)

        smaller_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid_one = Asteroid(self.position.x, self.position.y, smaller_radius, groups=self.sprite_groups, log_events=self.log_events)
        asteroid_two = Asteroid(self.position.x, self.position.y, smaller_radius, groups=self.sprite_groups, log_events=self.log_events)

        asteroid_one.velocity = velocity1
        asteroid_two.velocity = velocity2

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.angle = (self.angle + self.spin_direction * self.rotation_speed * dt) % 360
        frame_angle = self.angle
        self.points = [point.rotate(frame_angle) for point in self.original_points]
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