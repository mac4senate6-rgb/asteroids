import sys
import pygame
from constants import *
from logger import log_state
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from logger import log_event
from shot import Shot
from pathlib import Path


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()

    base_dir = Path(__file__).resolve().parent
    font_path = base_dir / "assets" / "fonts" / "Hyperspace.otf"
    font = pygame.font.Font(font_path, 36)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()
    dt = 0.0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)

    player = Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2, shots=shots)
    _asteroid_field = AsteroidField(asteroids)

    score = 0
    lives = PLAYER_STARTING_LIVES
    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid in asteroids:
            if (player.invulnerability_timer <= 0 and player.collides_with(asteroid)):
                log_event("player_hit", lives_before = lives, asteroid_radius = asteroid.radius)
                lives -= 1

                if lives <= 0:
                    log_event("player_dead", final_score = score)
                    print("Game over!")
                    sys.exit()
                else:
                    player.position.x = SCREEN_WIDTH / 2
                    player.position.y = SCREEN_HEIGHT / 2
                    player.velocity = pygame.Vector2(0, 0)
                    player.rotation = 0
                    player.invulnerability_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS
                    log_event("player_respawn", lives_remaining = lives)
                    break

        for asteroid in asteroids:
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_hit", asteroid_radius = asteroid.radius, score_before = score)
                    if asteroid.radius == ASTEROID_MIN_RADIUS:
                        score += 100
                    elif asteroid.radius == ASTEROID_MIN_RADIUS * 2:
                        score += 50
                    else:
                        score += 20
                    shot.kill()
                    asteroid.split()
                    break

        screen.fill("black")
        score_surface = font.render(f"Score: {score:05d}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH -40, 20))
        screen.blit(score_surface, score_rect)

        reserve_lives = lives - 1

        for i in range(reserve_lives):
            icon_position = pygame.Vector2(30 + i * 25, 55)
            icon_forward = pygame.Vector2(0, -1)
            icon_right = pygame.Vector2(1, 0) * 7
            icon_nose = icon_position + icon_forward * 10
            icon_rear_left = (icon_position - icon_forward * 10 - icon_right)
            icon_rear_center = (icon_position - icon_forward * 4)
            icon_rear_right = (icon_position - icon_forward * 10 + icon_right)
            pygame.draw.polygon(screen, (255, 255, 255), [icon_nose, icon_rear_left, icon_rear_center, icon_rear_right], LINE_WIDTH)

        for sprite in drawable:
            sprite.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()