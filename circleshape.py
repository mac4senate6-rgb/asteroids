import pygame

#Base class for objects in game

class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]
    def __init__(self, x: float, y: float, radius: float) -> None:
        #to be used later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def Draw(self, surface: pygame.Surface) -> None:
        pass

    def collides_with(self, other: "CircleShape") -> bool:
        distance = self.position.distance_to(other.position)
        return distance <= self.radius + other.radius

    def Update(self, dt: float) -> None:
        pass