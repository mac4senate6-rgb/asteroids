import pygame

ASTEROID_VECTORS = (  # Outer tuple containing all four Atari asteroid patterns.

    (  # Pattern 1: Atari vector ROM address $11E6.
        (0, 16),      # Invisible movement: 0 right, 16 up.
        (16, 16),     # Move 16 right and 16 up.
        (16, -16),    # Move 16 right and 16 down.
        (-8, -16),    # Move 8 left and 16 down.
        (8, -16),     # Move 8 right and 16 down.
        (-24, -16),   # Move 24 left and 16 down.
        (-24, 0),     # Move 24 left.
        (-16, 16),    # Move 16 left and 16 up.
        (0, 32),      # Move 32 up.
        (16, 16),     # Move 16 right and 16 up.
        (16, -16),    # Move 16 right and 16 down.
    ),

    (  # Pattern 2: Atari vector ROM address $11FE.
        (16, 8),      # Invisible movement: 16 right, 8 up.
        (16, 8),      # Move 16 right and 8 up.
        (-16, 16),    # Move 16 left and 16 up.
        (-16, -8),    # Move 16 left and 8 down.
        (-16, 8),     # Move 16 left and 8 up.
        (-16, -16),   # Move 16 left and 16 down.
        (8, -16),     # Move 8 right and 16 down.
        (-8, -16),    # Move 8 left and 16 down.
        (16, -16),    # Move 16 right and 16 down.
        (8, 8),       # Move 8 right and 8 up.
        (24, -8),     # Move 24 right and 8 down.
        (16, 24),     # Move 16 right and 24 up.
        (-16, 16),    # Move 16 left and 16 up.
    ),

    (  # Pattern 3: Atari vector ROM address $121A.
        (-16, 0),     # Invisible movement: 16 left.
        (-16, -8),    # Move 16 left and 8 down.
        (16, -24),    # Move 16 right and 24 down.
        (16, 24),     # Move 16 right and 24 up.
        (0, -24),     # Move 24 down.
        (16, 0),      # Move 16 right.
        (16, 24),     # Move 16 right and 24 up.
        (0, 16),      # Move 16 up.
        (-16, 24),    # Move 16 left and 24 up.
        (-24, 0),     # Move 24 left.
        (-24, -24),   # Move 24 left and 24 down.
        (16, -8),     # Move 16 right and 8 down.
    ),

    (  # Pattern 4: Atari vector ROM address $1234.
        (8, 0),       # Invisible movement: 8 right.
        (24, 8),      # Move 24 right and 8 up.
        (0, 8),       # Move 8 up.
        (-24, 16),    # Move 24 left and 16 up.
        (-24, 0),     # Move 24 left.
        (8, -16),     # Move 8 right and 16 down.
        (-24, 0),     # Move 24 left.
        (0, -24),     # Move 24 down.
        (16, -24),    # Move 16 right and 24 down.
        (24, 8),      # Move 24 right and 8 up.
        (8, -8),      # Move 8 right and 8 down.
        (16, 16),     # Move 16 right and 16 up.
        (-24, 16),    # Move 24 left and 16 up.
    ),
)

def build_asteroid_points(pattern: tuple[tuple[int, int], ...]) -> list[pygame.Vector2]:
    position = pygame.Vector2(0, 0)
    points = []
    start_dx, start_dy = pattern[0]
    position.x += start_dx
    position.y -= start_dy
    points.append(position.copy())

    for dx, dy in pattern[1:]:
        position.x += dx
        position.y -= dy
        points.append(position.copy())

    if points[0] == points[-1]:
        points.pop()

    maximum_distance = max((point.length() for point in points))
    normalized_points = [point / maximum_distance for point in points]
    return normalized_points


ASTEROID_SHAPES = tuple(build_asteroid_points(pattern) for pattern in ASTEROID_VECTORS)
