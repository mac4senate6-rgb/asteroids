import sys
import pygame
from constants import *
from logger import log_state
from player import Player
from asteroid import *
from asteroidfield import AsteroidField
from logger import log_event
from shot import Shot
from pathlib import Path
import ufo
import random
from ufo_shot import UFOShot


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
    ufos = pygame.sprite.Group()
    ufo_shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    ufo.UFO.containers = (ufos, updatable, drawable)
    UFOShot.containers = (ufo_shots, updatable, drawable)

    player = Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2, shots=shots)
    _asteroid_field = AsteroidField(asteroids)
    ufo_spawn_timer = UFO_SPAWN_INTERVAL

    score = 0
    lives = PLAYER_STARTING_LIVES


    def handle_player_hit(source: str, asteroid_radius: float | None = None) -> None:
        nonlocal lives

        if source == "asteroid":
            log_event("player_hit", lives_before=lives, source=source, asteroid_radius = asteroid_radius)
        else:
            log_event("player_hit", lives_before=lives, source=source)

        lives -= 1

        if lives == 0:
            log_event("player_dead", final_score=score, source=source)
            print("Game over, man..Game over!")
            sys.exit()

        player.position.x = SCREEN_WIDTH / 2
        player.position.y = SCREEN_HEIGHT / 2
        player.velocity = pygame.Vector2(0, 0)
        player.rotation = 0
        player.invulnerability_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS
        log_event("player_respawn",lives_remaining=lives,source=source)

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)
        if len(ufos) == 0:
            ufo_spawn_timer = max(0.0, ufo_spawn_timer - dt)

            if ufo_spawn_timer <= int(0):
                spawn_from_left = random.choice([True, False])
                spawn_y = random.uniform(UFO_RADIUS, SCREEN_HEIGHT - UFO_RADIUS)

                if spawn_from_left:
                    new_ufo = ufo.UFO(-UFO_RADIUS, spawn_y)
                    new_ufo.velocity = pygame.Vector2(UFO_SPEED, 0)
                else:
                    new_ufo = ufo.UFO(SCREEN_WIDTH + UFO_RADIUS, spawn_y)
                    new_ufo.velocity = pygame.Vector2(-UFO_SPEED, 0)

                ufo_spawn_timer = UFO_SPAWN_INTERVAL

        for asteroid in asteroids:
            if player.invulnerability_timer <= 0 and player.collides_with(asteroid):
                handle_player_hit("asteroid", asteroid.radius)
                break

        if player.invulnerability_timer <= 0:
            for ufo_shot in ufo_shots:
                if player.collides_with(ufo_shot):
                    ufo_shot.kill()
                    handle_player_hit("ufo_shot")
                    break

        if player.invulnerability_timer <= 0:
            for enemy_ufo in ufos:
                if player.collides_with(enemy_ufo):
                    enemy_ufo.kill()
                    handle_player_hit("ufo_collision")
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

        for shot in shots:
            for enemy_ufo in ufos:
                if shot.collides_with(enemy_ufo):
                    log_event("ufo_hit", score_before = score, ufo_radius = enemy_ufo.radius)
                    shot.kill()
                    enemy_ufo.kill()
                    score += UFO_SCORE
                    break
        for asteroid in asteroids:
            for enemy_ufo in ufos:
                if asteroid.collides_with(enemy_ufo):
                    log_event("ufo_destroyed_by_asteroid", ufo_radius = enemy_ufo.radius, asteroid_radius = asteroid.radius)
                    enemy_ufo.kill()
                    break

        screen.fill("black")
        score_surface = font.render(f"{score:05d}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 40, 20))
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