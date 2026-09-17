import pygame
import circleshape
from constants import *
from shot import Shot
from logger import log_event


class Player(circleshape.CircleShape):
    def __init__(self, x: float, y: float, shots: pygame.sprite.Group) -> None:
        circleshape.CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0.0
        self.thrusting = False
        self.shots = shots

    def collides_with(self, other: circleshape.CircleShape) -> bool:
        distance = self.position.distance_to(other.position)
        return distance <= PLAYER_COLLISION_RADIUS + other.radius

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5

        #"nose" point; sits one radius forward from ["player" object's position].
        nose = self.position + forward * self.radius

        # ["rear_left" point] sits one radius backward and then moves left.
        rear_left = self.position - forward * self.radius - right

        # sits only 45% of one radius backward b/c it is farther inward it creates the notch/divot
        rear_center = self.position - forward * (self.radius * .45)

        # ["rear_right" point] sits one radius backward and then moves right.
        rear_right = self.position - forward * self.radius + right

        return [nose, rear_left, rear_center, rear_right]

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

        if self.thrusting:
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            right = pygame.Vector2(0, 1).rotate(self.rotation + 90)

            flame_left = self.position - forward * (self.radius * .75) - right * (self.radius * .3)
            flame_tip = self.position - forward * (self.radius * 1.6)
            flame_right = self.position - forward * (self.radius * .75) + right * (self.radius * .3)

            pygame.draw.lines(screen, "white", False, [flame_left, flame_tip, flame_right], LINE_WIDTH)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        self.thrusting = keys[pygame.K_w]

        self.shoot_timer = max(0.0, self.shoot_timer - dt)

        if keys[pygame.K_a]:
            self.rotate(-dt)

        if keys[pygame.K_d]:
            self.rotate(dt)

        if keys[pygame.K_w]:
            self.move(dt)

        if keys[pygame.K_SPACE]:
            self.shoot()

        self.position += self.velocity * dt
        self.wrap_screen()

    def wrap_screen(self) -> None:
        self.position.x %= SCREEN_WIDTH
        self.position.y %= SCREEN_HEIGHT

    def move(self, dt: float) -> None:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = forward * PLAYER_ACCELERATION * dt
        self.velocity += acceleration

        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity = self.velocity.normalize() * PLAYER_MAX_SPEED

    def shoot(self) -> None:
        if self.shoot_timer > 0:
            return

        if len(self.shots) >= PLAYER_MAX_SHOTS:
            return

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

        shot = Shot(self.position.x, self.position.y)
        log_event("shot_fired")
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED


