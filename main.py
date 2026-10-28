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
import audio


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    audio.initialize_audio()
    audio.build_test_sounds()
    pygame.display.set_caption("Asteroids")

    pygame.mixer.set_num_channels(9)
    pygame.mixer.set_reserved(2)

    ufo_channel = pygame.mixer.Channel(0)
    large_ufo_sound = audio.load_large_ufo_sound()
    small_ufo_sound = audio.load_small_ufo_sound()
    small_explosion_sound = audio.load_small_explosion_sound()
    medium_explosion_sound = audio.load_medium_explosion_sound()
    large_explosion_sound = audio.load_large_explosion_sound()

    player_shot_sound = audio.load_player_shot_sound()
    thrust_sound = audio.load_thrust_sound()
    bonus_life_sound = audio.load_extra_life_sound()

    heartbeat_low_sound = pygame.mixer.Sound(str(audio.SOUNDS_DIR/"heartbeat_low.wav"))
    heartbeat_high_sound = pygame.mixer.Sound(str(audio.SOUNDS_DIR/"heartbeat_high.wav"))
    heartbeat_sounds = [heartbeat_low_sound, heartbeat_high_sound]

    heartbeat_channel = pygame.mixer.Channel(1)
    heartbeat_index = 0
    heartbeat_frame_accumulator = 0.0
    heartbeat_frame_counter = 0
    heartbeat_off_reload = 48
    heartbeat_off_timer = 4
    heartbeat_on_timer = 0
    heartbeat_wave_number = 0


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

    player = Player(
        x=SCREEN_WIDTH / 2,
        y=SCREEN_HEIGHT / 2,
        shots=shots,
        shot_sound=player_shot_sound,
        thrust_sound=thrust_sound
    )

    asteroid_field = AsteroidField(asteroids)
    ufo_spawn_timer = UFO_SPAWN_INTERVAL

    score = 0
    lives = PLAYER_STARTING_LIVES
    next_bonus_score = PLAYER_BONUS_LIFE_SCORE

    def play_asteroid_boom(asteroid_type: float) -> None:  # Accept the asteroid's radius.
        if asteroid_type == ASTEROID_MIN_RADIUS:  # Check for a small asteroid.
            small_explosion_sound.play()  # Play the small explosion.
        elif asteroid_type == ASTEROID_MIN_RADIUS * 2:  # Check for a medium asteroid.
            medium_explosion_sound.play()  # Play the medium explosion.
        else:  # Otherwise, it's a large asteroid.
            large_explosion_sound.play()  # Play the large explosion.

    def play_ufo_boom(ufo_type: ufo.UFO) -> None:  # Accept the actual UFO object.
        if isinstance(ufo_type, ufo.SmallUFO):  # Check whether it's a small UFO.
            medium_explosion_sound.play()  # Play the small UFO's explosion.
        else:  # Otherwise, it's a large UFO.
            large_explosion_sound.play()  # Play the large UFO's explosion.

    def handle_player_hit(source: str, asteroid_radius: float | None = None) -> None:
        nonlocal lives

        if source == "asteroid":
            log_event("player_hit", lives_before=lives, source=source, asteroid_radius = asteroid_radius)
        else:
            log_event("player_hit", lives_before=lives, source=source)

        lives -= 1
        heartbeat_channel.stop()
        small_explosion_sound.play()

        if lives == 0:
            log_event("player_dead", final_score=score, source=source)
            print("Game over, man...Game over!")
            sys.exit()

        player.position.x = SCREEN_WIDTH / 2
        player.position.y = SCREEN_HEIGHT / 2
        player.velocity = pygame.Vector2(0, 0)
        player.rotation = 0
        player.invulnerability_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS
        log_event("player_respawn",lives_remaining=lives,source=source)

    def check_bonus_lives() -> None:
        nonlocal lives, next_bonus_score
        while score >= next_bonus_score:
            lives += 1
            log_event("bonus_life_awarded", score=score, lives_remaining=lives)
            bonus_life_sound.play()
            next_bonus_score += PLAYER_BONUS_LIFE_SCORE

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        updatable.update(dt)

        if asteroid_field.wave_number != heartbeat_wave_number:
            heartbeat_wave_number = asteroid_field.wave_number
            heartbeat_off_reload = 48
            heartbeat_off_timer = 4
            heartbeat_on_timer = 0
            heartbeat_index = 0
            heartbeat_frame_counter = 0
            heartbeat_frame_accumulator = 0.0
            heartbeat_channel.stop()

        if not asteroids:
            heartbeat_channel.stop()
            heartbeat_on_timer = 0
            heartbeat_off_timer = 4
            heartbeat_frame_accumulator = 0.0
        else:
            heartbeat_frame_accumulator += dt

            while heartbeat_frame_accumulator >= 1.0 / 62.5:
                heartbeat_frame_accumulator -= 1.0 / 62.5
                heartbeat_frame_counter += 1

                if heartbeat_frame_counter % 64 == 0:
                    if heartbeat_off_reload > 8:
                        heartbeat_off_reload -= 1

                if heartbeat_on_timer > 0:
                    heartbeat_on_timer -= 1

                    if heartbeat_on_timer == 0:
                        heartbeat_channel.stop()
                        heartbeat_off_timer = heartbeat_off_reload

                elif heartbeat_off_timer > 0:
                    heartbeat_off_timer -= 1

                    if heartbeat_off_timer == 0:
                        heartbeat_channel.play(heartbeat_sounds[heartbeat_index])
                        heartbeat_index = (heartbeat_index + 1) % 2
                        heartbeat_on_timer = 4


        if len(ufos) == 0:
            ufo_spawn_timer = max(0.0, ufo_spawn_timer - dt)

            if ufo_spawn_timer <= int(0):
                spawn_from_left = random.choice([True, False])

                ufo_class = random.choice([ufo.SmallUFO, ufo.LargeUFO])
                ufo_sound = (large_ufo_sound if ufo_class is ufo.LargeUFO else small_ufo_sound)

                spawn_radius = (UFO_LARGE_RADIUS if ufo_class is ufo.LargeUFO else UFO_SMALL_RADIUS)
                spawn_y = random.uniform(spawn_radius, SCREEN_HEIGHT - spawn_radius)

                if spawn_from_left:
                    new_ufo = ufo_class(-spawn_radius, spawn_y, ufo_sound, ufo_channel)
                    new_ufo.velocity = pygame.Vector2(UFO_SPEED, 0)
                else:
                    new_ufo = ufo_class(SCREEN_WIDTH + spawn_radius, spawn_y, ufo_sound, ufo_channel)
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
                    play_ufo_boom(enemy_ufo)
                    enemy_ufo.kill()
                    handle_player_hit("ufo_collision")
                    break

        for asteroid in asteroids:
            for shot in list(shots):
                if asteroid.collides_with(shot):
                    log_event("asteroid_hit", asteroid_radius = asteroid.radius, score_before = score)
                    if asteroid.radius == ASTEROID_MIN_RADIUS:
                        score += 100
                    elif asteroid.radius == ASTEROID_MIN_RADIUS * 2:
                        score += 50
                    else:
                        score += 20
                    shot.kill()
                    play_asteroid_boom(asteroid.radius)
                    asteroid.split()
                    break

        for shot in shots:
            for enemy_ufo in ufos:
                if shot.collides_with(enemy_ufo):
                    log_event("ufo_hit", score_before = score, ufo_radius = enemy_ufo.radius)
                    shot.kill()
                    play_ufo_boom(enemy_ufo)
                    enemy_ufo.kill()

                    if isinstance(enemy_ufo, ufo.SmallUFO):
                        score += UFO_SMALL_SCORE
                    else:
                        score += UFO_LARGE_SCORE
                    break

        check_bonus_lives()

        for asteroid in asteroids:
            for enemy_ufo in ufos:
                if asteroid.collides_with(enemy_ufo):
                    log_event("ufo_destroyed_by_asteroid", ufo_radius = enemy_ufo.radius, asteroid_radius = asteroid.radius)
                    play_ufo_boom(enemy_ufo)
                    enemy_ufo.kill()
                    break

        screen.fill("black")
        score_surface = font.render(f"{score:05d}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 40, 20))
        screen.blit(score_surface, score_rect)

        reserve_lives = lives - 1

        for i in range(reserve_lives):
            icon_position = pygame.Vector2(30 + i * 16, 55)

            point_a = icon_position + pygame.Vector2(-4, 6)
            point_b = icon_position + pygame.Vector2(4, 6)
            point_c = icon_position + pygame.Vector2(8, 10)
            point_d = icon_position + pygame.Vector2(0, -14)
            point_e = icon_position + pygame.Vector2(-8, 10)

            pygame.draw.aaline(screen, (140, 140, 140), point_a, point_b)
            pygame.draw.aaline(screen, (140, 140, 140), point_b, point_c)
            pygame.draw.aaline(screen, (140, 140, 140), point_c, point_d)
            pygame.draw.aaline(screen, (140, 140, 140), point_d, point_e)
            pygame.draw.aaline(screen, (140, 140, 140), point_e, point_a)

        for sprite in drawable:
            sprite.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()