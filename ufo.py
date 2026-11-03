import pygame
from constants import *
from circleshape import CircleShape
import random
from ufo_shot import UFOShot

class UFO(CircleShape):
    def __init__(
            self, x: float, y: float, radius: float,
            ufo_sound: pygame.mixer.Sound,
            ufo_channel: pygame.mixer.Channel,
            groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_speed: float | None = None,
            shot_lifetime: float | None = None,
            targeting: CircleShape | None = None
            ) -> None:

        super().__init__(x, y, radius, groups=groups)

        self.shot_groups = shot_groups
        self.targeting = targeting
        self.shot_speed = UFO_SHOT_SPEED if shot_speed is None else shot_speed
        self.shot_lifetime = UFO_SHOT_LIFETIME_SECONDS if shot_lifetime is None else shot_lifetime
        self.ufo_sound = ufo_sound
        self.ufo_channel = ufo_channel
        self.ufo_channel.play(self.ufo_sound, loops=-1)

        self.shoot_timer = random.uniform(UFO_SHOOT_INTERVAL_MIN_SECONDS, UFO_SHOOT_INTERVAL_MAX_SECONDS)

        self.vertices: dict[str, tuple[float, float]] = {
            "A": (-5, -10),
            "B": (5, -10),
            "C": (-10, -4),
            "D": (10, -4),
            "E": (-20, 2),
            "F": (20, 2),
            "G": (-10, 10),
            "H": (10, 10),
        }

        self.line_pairs: list[tuple[str, str]] = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
            ("E", "F"),
            ("C", "E"),
            ("D", "F"),
            ("E", "G"),
            ("F", "H"),
            ("C", "G"),
            ("D", "H"),

        ]
        self.scale = self.radius / 20

        self.direction_change_timer = random.uniform(UFO_DIRECTION_CHANGE_MIN_SECONDS, UFO_DIRECTION_CHANGE_MAX_SECONDS)

    def shoot(self) -> None:
        shot = UFOShot(
            self.position.x,
            self.position.y,
            groups=self.shot_groups,
            lifetime=self.shot_lifetime
        )
        if isinstance(self, SmallUFO) and self.targeting is not None:
            aim_vector = self.targeting.position - self.position

            if aim_vector.length_squared() > 0:
                shot_direction = aim_vector.normalize().rotate(random.uniform(-10, 10))
            else:
                shot_direction = pygame.Vector2(0, 1).rotate(random.uniform(0.0, 360.0))
        else:
            shot_direction = pygame.Vector2(0, 1).rotate(random.uniform(0.0, 360.0))

        shot.velocity = shot_direction * self.shot_speed

    def kill(self) -> None:
        self.ufo_channel.stop()
        super().kill()

    def draw(self, screen: pygame.Surface) -> None:
        glow = (120, 120, 120)
        white = (255, 255, 255)

        for start_key, end_key in self.line_pairs:
            local_start = self.vertices[start_key]
            local_end = self.vertices[end_key]

            start_pos = (self.position.x + local_start[0] * self.scale,
                         self.position.y + local_start[1] * self.scale)

            end_pos = (self.position.x + local_end[0] * self.scale,
                       self.position.y + local_end[1] * self.scale)

            pygame.draw.aaline(screen, glow, start_pos, end_pos)
            pygame.draw.line(screen, white, start_pos, end_pos, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.shoot_timer -= dt

        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = random.uniform(UFO_SHOOT_INTERVAL_MIN_SECONDS, UFO_SHOOT_INTERVAL_MAX_SECONDS)

        self.direction_change_timer -= dt

        if self.direction_change_timer <= 0:
            vertical_direction = random.choice([-1, 0, 1])

            self.velocity.y = (vertical_direction * UFO_VERTICAL_SPEED)
            self.direction_change_timer = random.uniform(UFO_DIRECTION_CHANGE_MIN_SECONDS, UFO_DIRECTION_CHANGE_MAX_SECONDS)

        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y = UFO_VERTICAL_SPEED

        elif self.position.y > SCREEN_HEIGHT - self.radius:
            self.position.y = SCREEN_HEIGHT - self.radius
            self.velocity.y = -UFO_VERTICAL_SPEED

        if self.position.x < -self.radius or self.position.x > SCREEN_WIDTH + self.radius:
            self.kill()


class LargeUFO(UFO):
    def __init__(
            self,
            x: float,
            y: float,
            ufo_sound: pygame.mixer.Sound,
            ufo_channel: pygame.mixer.Channel,
            groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_speed: float | None = None,
            shot_lifetime: float | None = None,
            targeting: CircleShape | None = None,
    ) -> None:

        super().__init__(x, y, UFO_LARGE_RADIUS, ufo_sound,
                         ufo_channel, groups=groups, shot_groups=shot_groups,
                         shot_speed=shot_speed, shot_lifetime=shot_lifetime,
                         targeting=targeting,
                         )


class SmallUFO(UFO):
    def __init__(
            self, x: float, y: float, ufo_sound: pygame.mixer.Sound,
            ufo_channel: pygame.mixer.Channel, groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_groups: tuple[pygame.sprite.Group, ...] | None = None,
            shot_speed: float | None = None,
            shot_lifetime: float | None = None,
            targeting: CircleShape | None = None,
    ) -> None:

        super().__init__(x, y, UFO_SMALL_RADIUS, ufo_sound,
                         ufo_channel, groups=groups, shot_groups=shot_groups,
                         shot_speed=shot_speed, shot_lifetime=shot_lifetime,
                         targeting=targeting
                         )
