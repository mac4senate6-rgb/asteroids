import pygame
import math

class ShipExplosion:
    TICKS_PER_SECOND = 61.5  # Approximate original Asteroids game tick rate.

    TICKS_PER_STAGE = 32  # Each disappearance stage lasts 32 original ticks.

    TOTAL_STAGES = 6  # The explosion has six stages.

    TOTAL_TICKS = TICKS_PER_STAGE * TOTAL_STAGES  # Six stages of 32 ticks produce 192 ticks.
    SCALE = 0.5  # Matches our existing pygame ship drawing scale.
    FRAGMENT_LENGTH_MULTIPLIER = 6.0
    COLOR = (220, 220, 220)  # Bright gray lines resembling the vector display.

    FRAGMENT_LINES = (  # Original Atari fragment line displacements.
        (-8, -12),  # Fragment 1: left 8, down 12 in Atari coordinates.
        (4, -8),  # Fragment 2: right 4, down 8.
        (6, 2),  # Fragment 3: right 6, up 2.
        (-8, 8),  # Fragment 4: left 8, up 8.
        (-6, 2),  # Fragment 5: left 6, up 2.
        (4, -4),  # Fragment 6: right 4, down 4.

    )

    FRAGMENT_VELOCITIES = (  # Original Atari signed movement values.
        (-40, 30),  # Fragment 1 moves to the left and upward.
        (50, -20),  # Fragment 2 moves right and downward.
        (0, -60),  # Fragment 3 moves downward.
        (60, 20),  # Fragment 4 moves right and upward.
        (10, 70),  # Fragment 5 moves right and upward.
        (-40, -40),  # Fragment 6 moves left and downward.

    )

    def __init__(self, position: pygame.Vector2) -> None:

        self.position = position.copy()
        self.elapsed_time = 0.0
        self.processed_ticks = 0
        self.fragment_positions = list()

        for velocity in self.FRAGMENT_VELOCITIES:

            velocity_x, velocity_y = velocity

            start_x = self._initial_offset(velocity_x)
            start_y = self._initial_offset(velocity_y)

            self.fragment_positions.append(pygame.Vector2(start_x, -start_y))

    @staticmethod
    def _initial_offset(velocity: int) -> int:

        unsigned_byte = velocity & 0xFF
        high_nibble = unsigned_byte >> 4

        result = ((high_nibble + 0xF8) & 0xFF) ^ 0xF8

        if result >= 128:
            result -= 256

        return result

    def update(self, dt: float) -> None:
        if self.is_finished:
            return

        self.elapsed_time = self.elapsed_time + dt

        target_ticks = math.floor(self.elapsed_time * self.TICKS_PER_SECOND)

        remaining_ticks = target_ticks - self.processed_ticks

        for _ in range(remaining_ticks):
            if self.processed_ticks >= self.TOTAL_TICKS:
                break

            self._advance_one_tick()
            self.processed_ticks += 1

    def _advance_one_tick(self) -> None:
        stage = self.processed_ticks // self.TICKS_PER_STAGE
        visible_count = self.TOTAL_STAGES - stage

        for index in range(visible_count):
            velocity_x, velocity_y = self.FRAGMENT_VELOCITIES[index]

            move_x = velocity_x / 256
            move_y = -velocity_y / 256

            self.fragment_positions[index] += pygame.Vector2(move_x, move_y)

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_finished:
            return

        stage = self.processed_ticks // self.TICKS_PER_STAGE
        visible_count = self.TOTAL_STAGES - stage

        for index in range(visible_count):
            line_x, line_y = self.FRAGMENT_LINES[index]
            offset = self.fragment_positions[index]
            start = self.position + offset * self.SCALE
            end = start + pygame.Vector2(line_x * self.SCALE * self.FRAGMENT_LENGTH_MULTIPLIER, -line_y * self.SCALE * self.FRAGMENT_LENGTH_MULTIPLIER)

            pygame.draw.aaline(screen, self.COLOR, start, end)

    @property
    def is_finished(self) -> bool:
        return self.processed_ticks >= self.TOTAL_TICKS