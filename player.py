import pygame
import circleshape
from constants import *
from shot import Shot
from logger import log_event


class Player(circleshape.CircleShape):
    def __init__(self, x: float, y: float, shots: pygame.sprite.Group, shot_sound: pygame.mixer.Sound, thrust_sound: pygame.mixer.Sound) -> None:
        circleshape.CircleShape.__init__(self, x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0.0
        self.fire_was_pressed = False
        self.thrusting = False # The spacecraft begins without thrust.
        self.thrust_animation_time = 0.0 # Tracks elapsed time for the flashing exhaust.
        self.invulnerability_timer = 0.0

        self.shots = shots
        self.shot_sound = shot_sound
        self.thrust_sound = thrust_sound
        self.thrust_channel = None


    def distance_to_segment(self, point: pygame.Vector2, start: pygame.Vector2, end: pygame.Vector2) -> float:
        segment = end - start
        point_vector = point - start

        segment_length_squared = segment.length_squared()

        if segment_length_squared == 0:
            return point.distance_to(start)

        t = point_vector.dot(segment) / segment_length_squared
        t = max(0.0, min(1.0, t))

        closest_point = start + segment * t

        return point.distance_to(closest_point)

    def point_inside_polygon(self, point: pygame.Vector2, polygon: list[pygame.Vector2]) -> bool:
        inside = False

        for i in range(len(polygon)):
            current_polygon = polygon[i]
            previous_polygon = polygon[i - 1]

            if (current_polygon.y > point.y) != (previous_polygon.y > point.y):
                intersection_x = ((previous_polygon.x - current_polygon.x) * (point.y - current_polygon.y) / (previous_polygon.y - current_polygon.y) + current_polygon.x)

                if point.x < intersection_x:
                    inside = not inside

        return inside

    def collides_with(self, other: circleshape.CircleShape) -> bool:
        ship_points = self.triangle()

        for i in range(len(ship_points)):
            start = ship_points[i]
            end = ship_points[(i + 1) % len(ship_points)]

            distance = self.distance_to_segment(other.position, start, end)

            if distance <= other.radius:
                return True

        return self.point_inside_polygon(other.position, ship_points)

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)

        scale = 0.5

        rom_points = [(56, 0),(-40, 32),(-24, 16),(-24, -16),(-40, -32)]
        return [self.position + forward * (x * scale) + right * (y * scale) for x, y in rom_points]


    def draw(self, screen: pygame.Surface) -> None:
        if self.invulnerability_timer > 0:
            blink = int(self.invulnerability_timer / PLAYER_BLINK_INTERVAL_SECONDS)
            if blink % 2:
                return

        points = self.triangle()
        bright = (240, 240, 240)
        dim = (220, 220, 220)

        pygame.draw.aaline(screen, bright, points[2], points[3])
        pygame.draw.aaline(screen, dim, points[3], points[4])
        pygame.draw.aaline(screen, bright, points[4], points[0])
        pygame.draw.aaline(screen, bright, points[0], points[1])
        pygame.draw.aaline(screen, dim, points[1], points[2])

        if self.thrusting and int(self.thrust_animation_time * 60) >= 4:  # Draw exhaust only during its illuminated four-frame phase.
            forward = pygame.Vector2(0, 1).rotate(self.rotation)  # Find the direction the spacecraft faces.
            right = pygame.Vector2(0, 1).rotate(self.rotation + 90)  # Find the sideways direction.

            flame_left = self.position - forward * 12 - right * 8
            flame_tip = self.position - forward * 28
            flame_right = self.position - forward * 12 + right * 8

            pygame.draw.aaline(screen, bright, flame_left, flame_tip)
            pygame.draw.aaline(screen, bright, flame_tip, flame_right)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()  # Read the keyboard.
        self.thrusting = keys[pygame.K_w]  # Determine whether thrust is active.
        self.thrust_animation_time += dt  # Advance the animation clock.
        self.thrust_animation_time %= 8 / 60  # Repeat the animation every eight 60 Hz frames.

        if self.thrusting:
            if self.thrust_channel is None:
                self.thrust_channel = self.thrust_sound.play(loops=-1)
        else:
            if self.thrust_channel is not None:
                self.thrust_channel.stop()
                self.thrust_channel = None

        self.shoot_timer = max(0.0, self.shoot_timer - dt)

        self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)

        if keys[pygame.K_a]:
            self.rotate(-dt)

        if keys[pygame.K_d]:
            self.rotate(dt)

        if keys[pygame.K_w]:
            self.move(dt)
        else:
            drag = PLAYER_DRAG_SPEED ** (dt * 60)
            self.velocity *= drag

        fire_pressed = keys[pygame.K_SPACE] # Check whether Space is currently held.
        if fire_pressed and not self.fire_was_pressed: # Fire only when Space changes from released to pressed.
            self.shoot() # Attempt to create one projectile.
        self.fire_was_pressed = fire_pressed  # Remember the button state for the next frame.

        self.position += self.velocity * dt
        self.wrap_screen()

    def wrap_screen(self) -> None:
        self.position.x %= SCREEN_WIDTH
        self.position.y %= SCREEN_HEIGHT

    def move(self, dt: float) -> None:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = forward * PLAYER_ACCELERATION * dt
        self.velocity += acceleration

        self.velocity.x = max(-PLAYER_MAX_SPEED, min(self.velocity.x, PLAYER_MAX_SPEED))
        self.velocity.y = max(-PLAYER_MAX_SPEED, min(self.velocity.y, PLAYER_MAX_SPEED))

    def shoot(self) -> None:
        if self.shoot_timer > 0:
            return

        if len(self.shots) >= PLAYER_MAX_SHOTS:
            return

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

        forward = pygame.Vector2(0, 1).rotate(self.rotation)  # Calculate the direction the ship is pointing.
        shot_position = self.position + forward * 28  # Find the ship's nose, 28 pixels forward.
        shot = Shot(shot_position.x, shot_position.y)  # Create the projectile at the nose.

        log_event("shot_fired", x = shot_position.x, y = shot_position.y, rotation = self.rotation)
        shot.velocity = forward * PLAYER_SHOOT_SPEED + self.velocity
        shot.velocity.x = max(-PLAYER_SHOT_MAX_SPEED, min(shot.velocity.x, PLAYER_SHOT_MAX_SPEED))
        shot.velocity.y = max(-PLAYER_SHOT_MAX_SPEED, min(shot.velocity.y, PLAYER_SHOT_MAX_SPEED))

        self.shot_sound.play()

