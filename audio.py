import math
import random
import struct
import wave
from pathlib import Path
import pygame

SAMPLE_RATE = 44100
MAX_AMPLITUDE = 32767
BASE_DIR = Path(__file__).resolve().parent
SOUNDS_DIR = BASE_DIR / "assets"/ "sounds"

def initialize_audio() -> None:
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)


def write_wav(filename: str, samples: list[float]) -> Path:
    output_location = SOUNDS_DIR / filename

    with wave.open(str(output_location), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(SAMPLE_RATE)

        for sample in samples:
            sample = max(-1.0, min(1.0, sample))
            sample_value = int(sample * MAX_AMPLITUDE)
            sample_bytes = sample_value.to_bytes(2, byteorder="little", signed=True)
            wave_file.writeframesraw(sample_bytes)

    return output_location


def generate_tone(filename: str, frequency: float, duration: float, volume: float = 0.35) -> Path:
    output_path = SOUNDS_DIR / filename
    frame_count = int(SAMPLE_RATE * duration)

    with wave.open(str(output_path), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(SAMPLE_RATE)

        for frame in range(frame_count):
            time = frame / SAMPLE_RATE
            envelope = 1.0 - frame / frame_count
            sample = math.sin(2 * math.pi * frequency * time)
            sample_value = int(sample * envelope * volume * MAX_AMPLITUDE)
            wave_file.writeframesraw(sample_value.to_bytes(2, byteorder="little", signed=True))

    return output_path

def generate_heartbeat_sound(filename: str, control_value: int) -> None:
    sample_rate = SAMPLE_RATE
    duration = 4 / 62.5
    sample_count = round(sample_rate * duration)
    sample_period = 1.0 / sample_rate
    pitch_calibration = 1.14

    control_bits = control_value & 0x0F
    resistors = (220000.0, 100000.0, 47000.0, 22000.0)
    digital_high_voltage = 3.5
    bias_voltage = 4.3
    bias_resistance = 6800.0
    ground_resistance = 47000.0

    conductance_total = 1.0 / bias_resistance + 1.0 / ground_resistance
    weighted_voltage = bias_voltage / bias_resistance

    for bit in range(4):
        resistance = resistors[bit]
        conductance_total += 1.0 / resistance
        bit_mask = 1 << bit

        if control_bits & bit_mask:
            weighted_voltage += digital_high_voltage / resistance

    control_voltage = weighted_voltage / conductance_total

    supply_voltage = 5.0  # Set the 555 supply voltage.
    transistor_drop = 0.8  # Account for the documented transistor voltage
    current_resistance = 22000.0  # Set the oscillator's 22-kilohm resistor
    discharge_resistance = 18000.0 # Set the oscillator's additional 18-kilohm resistor.
    capacitance = 0.22e-6  # Convert the 0.22-microfarad timing capacitor into farads.

    charging_current = max(0.0, (supply_voltage - control_voltage - transistor_drop) / current_resistance)
    discharge_equilibrium = charging_current * discharge_resistance

    lower_threshold = supply_voltage / 3  #  Calculate the lower switching threshold.
    upper_threshold = supply_voltage * 2 / 3  #  Calculate the upper switching threshold.

    if charging_current <= 0.0 or discharge_equilibrium >= lower_threshold:
        raise ValueError("Heartbeat oscillator cannot complete a charge/discharge cycle.")

    capacitor_voltage = lower_threshold
    charging = True

    filter_resistance = 3300.0
    filter_capacitance = 0.1e-6
    filter_time_constant = filter_resistance * filter_capacitance
    filter_alpha = 1.0 - math.exp(-sample_period / filter_time_constant)

    filtered_output = 0.0
    samples = []

    for _ in range(sample_count):
        remaining_time = sample_period * pitch_calibration

        while remaining_time > 1e-12:
            if charging:
                time_to_threshold = (upper_threshold - capacitor_voltage) * capacitance / charging_current

                if time_to_threshold > remaining_time:
                    capacitor_voltage += charging_current * remaining_time / capacitance
                    remaining_time = 0.0

                else:
                    capacitor_voltage = upper_threshold
                    remaining_time -= time_to_threshold
                    charging = False

            else:
                time_to_threshold = discharge_resistance * capacitance * math.log(
                    (capacitor_voltage - discharge_equilibrium) / (lower_threshold - discharge_equilibrium))

                if time_to_threshold > remaining_time:
                    capacitor_voltage = discharge_equilibrium + (capacitor_voltage - discharge_equilibrium) * math.exp(-remaining_time / (discharge_resistance * capacitance))
                    remaining_time = 0.0

                else:
                    capacitor_voltage = lower_threshold
                    remaining_time -= time_to_threshold
                    charging = True

        oscillator_output = 1.0 if charging else -1.0
        filtered_output += filter_alpha * (oscillator_output - filtered_output)
        sample = int(filtered_output * 16000)
        sample = max(-32768, min(32767, sample))
        samples.append(sample)

    fade_samples = min(int(sample_rate * 0.005), len(samples))

    for index in range(fade_samples):
        sample_index = len(samples) - fade_samples + index
        fade_factor = (fade_samples - index - 1) / fade_samples
        samples[sample_index] = int(samples[sample_index] * fade_factor)

    output_path = SOUNDS_DIR / filename

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f"<{len(samples)}h", *samples))


PLAYER_SHOT_FILENAME = "player_shot.wav"
def generate_player_shot() -> Path:
    output_path = SOUNDS_DIR / PLAYER_SHOT_FILENAME

    duration = 0.267
    tonal_duration = 0.18
    volume = 0.28
    frame_count = int(SAMPLE_RATE * duration)

    with wave.open(str(output_path), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(SAMPLE_RATE)

        phase = 0.0
        crossfade_duration = 0.025
        crossfade_start = tonal_duration - crossfade_duration

        for frame in range(frame_count):
            time = frame / SAMPLE_RATE

            if time < tonal_duration:
                frequency = 918.0 - (2188.0 * time) - (5905.0 * time ** 2)

                if frequency < 120.0:
                    frequency = 120.0

                phase += 2 * math.pi * frequency / SAMPLE_RATE
                attack = min(1.0, time / 0.008)
                decay = math.exp((-time / 0.13))

                tonal_gain = attack * decay
                noise_gain = 0.0

                if time >= crossfade_start:
                    crossfade_progress = (time - crossfade_start) / crossfade_duration
                    tonal_gain *= 1.0 - crossfade_progress
                    noise_gain = 0.06 * crossfade_progress

                sample = math.sin(phase)
                sample += 0.55 * math.sin(phase * 2)
                sample += 0.22 * math.sin(phase * 3)
                sample += 0.10 * math.sin(phase * 4)
                sample += random.uniform(-0.08, 0.08)

                sample *= tonal_gain

                if noise_gain > 0.0:
                    sample += random.uniform(-1.0, 1.0) * noise_gain

            else:
                tail_progress = (time - tonal_duration) / (duration - tonal_duration)
                noise_gain = 0.06 * (1.0 - tail_progress) ** 2
                sample = random.uniform(-1.0, 1.0) * noise_gain

            final_fade = min(1.0, max(0.0, (duration - time) / 0.015))
            sample *= final_fade

            sample_value = int(sample * volume * MAX_AMPLITUDE)
            sample_value = max(-MAX_AMPLITUDE, min(MAX_AMPLITUDE, sample_value))

            wave_file.writeframesraw(sample_value.to_bytes(2, byteorder="little", signed=True))

    return output_path



THRUST_FILENAME = "thrust.wav"
def generate_thrust_sound() -> Path:
    output_path = SOUNDS_DIR / THRUST_FILENAME
    duration = 0.50
    cutoff_hz = 650.0
    volume = 0.30
    frame_count = int(SAMPLE_RATE * duration)

    rng = random.Random(1979)
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff_hz / SAMPLE_RATE)
    filtered_sample = 0.0
    samples = []

    for _ in range(frame_count):
        noise_sample = rng.uniform(-1.0, 1.0)
        filtered_sample += alpha * (noise_sample - filtered_sample)
        samples.append(filtered_sample)

    crossfade_frames = int(SAMPLE_RATE * 0.05)

    for frame in range(crossfade_frames):
        fade = frame / crossfade_frames
        start_sample = samples[frame]

        end_index = (frame_count - crossfade_frames + frame)
        end_sample = samples[end_index]

        blended_sample = (end_sample * (1.0 - fade) + start_sample * fade)

        samples[end_index] = blended_sample

    with wave.open(str(output_path), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(SAMPLE_RATE)

        for sample in samples:
            sample_value = int(sample * volume * MAX_AMPLITUDE)
            sample_value = max(-MAX_AMPLITUDE, min(MAX_AMPLITUDE, sample_value))
            wave_file.writeframesraw(sample_value.to_bytes(2, byteorder="little", signed=True))

    return output_path



EXTRA_LIFE_FILENAME = "extra_life.wav"
def generate_extra_life_sound() -> Path:
    output_path = SOUNDS_DIR / EXTRA_LIFE_FILENAME

    master_clock = 12_096_000.0
    oscillator_frequency = master_clock / 4096.0
    interrupt_rate = oscillator_frequency / 12.0
    timer = 0xB0

    interrupt_index = 0
    frame_timer = 0

    oscillator_phase = 0.0

    samples: list[float] = []

    samples_per_interrupt = SAMPLE_RATE / interrupt_rate
    sample_position = 0

    while timer > 0:
        frame_index = interrupt_index // 4
        if interrupt_index % 4 == 0:
            frame_timer = frame_index & 0xFF

        accumulator = frame_timer
        carry = 0

        for rotation in range(4):  # Reproduce the four 6502 ROR instructions.
            next_carry = accumulator & 0x01  # Save the bit that will move into carry.
            accumulator = accumulator >> 1  # Shift all accumulator bits to one position right.
            accumulator |= carry << 7 # Move the previous carry into bit seven.
            accumulator &= 0xFF  # Keep the accumulator within eight bits.
            carry = next_carry  # Update the carry flag for the next rotation.

            if rotation == 0 and carry == 1:  # The original timer test follows the first ROR.
                timer -= 1  # Decrease the extra-life timer.

        sound_enabled = bool(accumulator & 0x80)

        next_sample_position = round((interrupt_index + 1) * samples_per_interrupt)

        while sample_position < next_sample_position:

            oscillator_phase += oscillator_frequency / SAMPLE_RATE  # Advance the 3 kHz oscillator.
            oscillator_phase %= 1.0  # Wrap the oscillator after one complete cycle.

            if sound_enabled:
                if oscillator_phase > 0.5:
                    sample = 1.0
                else:
                    sample = -1.0
            else:
                sample = 0.0

            sample *= 0.25
            samples.append(sample)
            sample_position += 1

        interrupt_index += 1

    with wave.open(str(output_path), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(SAMPLE_RATE)

        for sample in samples:
            sample = max(-1.0, min(1.0, sample))
            sample_value = int(sample * MAX_AMPLITUDE)
            sample_bytes = sample_value.to_bytes(2, byteorder="little", signed=True)
            wave_file.writeframesraw(sample_bytes)

    return output_path


def generate_ufo_samples(modulation_hz: float, duration: float = 1.0) -> list[float]:  # Generate samples using our simplified 555/566 oscillator model.
    supply_voltage = 12.0  # The 566 oscillator receives a 12-volt supply.
    control_center = 6.0  # Assume the oscillator's average control voltage is 6 volts.
    control_swing = 1.0  # Allow the control voltage to vary one volt above and below center.
    timing_resistance = 10_000.0  # Represent the original 10-kilohm timing resistor.
    timing_capacitance = 0.047e-6  # Convert the 0.047-microfarad capacitor into farads.
    frame_count = int(SAMPLE_RATE * duration)  # Calculate how many audio samples we need.
    phase = 0.0  # Start the oscillator at the beginning of its waveform.

    samples: list[float] = []  # Create an empty list to hold our generated audio.

    for frame in range(frame_count):  # Generate one audio sample for every frame.
        time = frame / SAMPLE_RATE  # Calculate the current position in seconds.
        cycle = (time * modulation_hz) % 1.0  # Track our position within the repeating modulation cycle.
        modulation = 4.0 * abs(cycle - 0.5) - 1.0  # Generate a triangular modulation waveform.
        control_voltage = control_center + control_swing * modulation  # Calculate the changing oscillator control voltage.
        frequency = 2.4 * (supply_voltage - control_voltage) / (  # Calculate the oscillator's instantaneous frequency.
            timing_resistance * timing_capacitance * supply_voltage)  # Complete the denominator using the circuit values.


        phase = (phase + frequency / SAMPLE_RATE) % 1.0  # Advance the oscillator phase and wrap after one cycle.
        sample = (4.0 * abs(phase - 0.5) - 1.0) * 0.22  # Produce a triangle-wave audio sample at 22% volume.
        fade = min(1.0, time / 0.01, (duration - time) / 0.01)  # Apply a short fade at both ends.
        samples.append(sample * max(0.0, fade))  # Add the completed sample to our recording.

    return samples  # Return the finished list of audio samples.


def generate_large_ufo_sound() -> Path:
    return write_wav("large_ufo.wav", generate_ufo_samples(5.64))


def generate_small_ufo_sound() -> Path:
    return write_wav("small_ufo.wav", generate_ufo_samples(8.20))


def generate_explosion_samples(initial_timer: int) -> list[float]:
    noise_clock = 12000
    update_rate = 62.5
    rc_seconds = 3042.0 * 0.000001
    filter_alpha = 1.0 - math.exp(-1.0 / (rc_seconds * SAMPLE_RATE))
    noise_register = 0x0001
    timer = initial_timer & 0xFF
    noise_phase = 0.0
    sample_divider_counter = 0
    held_noise = 0.0
    filtered = 0.0
    samples: list[float] = []
    frame_count = 0
    sample_index = 0

    while timer & 0x3F:
        frame_boundary = round((frame_count + 1) * SAMPLE_RATE / update_rate)

        while sample_index < frame_boundary:  # Generate audio samples until the current game frame ends.
            pitch = (timer >> 6) & 0b11  # Extract the two pitch-control bits.
            volume = (timer >> 2) & 0b1111  # Extract the four volume-control bits.
            divider = (12, 6, 3, 5)[pitch]  # Select corresponding noise-sampling divider.

            noise_phase += noise_clock / SAMPLE_RATE  # Advance the 12 kHz noise clock.

            while noise_phase >= 1.0:  # Process each completed noise-clock tick.
                noise_phase -= 1.0  # Remove the completed tick while preserving the remainder.
                feedback = ((noise_register >> 6) ^ (noise_register >> 14)) & 1  # Calculate the feedback bit.
                noise_register = ((noise_register << 1) | feedback) & 0xFFFF  # Update the 16-bit noise register.
                sample_divider_counter += 1  # Count another noise-clock tick.

                if sample_divider_counter >= divider:  # Check whether the sampling divider has reached its limit.
                    sample_divider_counter = 0  # Restart the sampling divider.
                    held_noise = 1.0 if (noise_register & 1) else -1.0  # Capture the current noise bit.

            target = held_noise * (volume / 15.0) * 0.35  # Apply the selected explosion volume.
            filtered += filter_alpha * (target - filtered)  # Smooth the signal through our RC filter.
            samples.append(filtered)  # Store the completed audio sample.
            sample_index += 1  # Advance the audio-sample counter.

        timer = (timer - 1) & 0xFF  # Decrease the explosion timer once per game frame.
        frame_count += 1  # Advance the game-frame counter.

    return samples  # Return the finished explosion waveform.


def generate_explosion_sound(filename: str, initial_timer: int) -> Path:
    samples = generate_explosion_samples(initial_timer)
    return write_wav(filename, samples)


def build_test_sounds() -> None:
    heartbeat_low = SOUNDS_DIR / "heartbeat_low.wav"
    heartbeat_high = SOUNDS_DIR / "heartbeat_high.wav"
    player_shot = SOUNDS_DIR / PLAYER_SHOT_FILENAME
    thrust_sound = SOUNDS_DIR / THRUST_FILENAME
    extra_life = SOUNDS_DIR / EXTRA_LIFE_FILENAME
    large_ufo = SOUNDS_DIR / "large_ufo.wav"
    small_ufo = SOUNDS_DIR / "small_ufo.wav"
    explosion_low = SOUNDS_DIR / "explosion_low.wav"
    explosion_medium = SOUNDS_DIR / "explosion_medium.wav"
    explosion_high = SOUNDS_DIR / "explosion_high.wav"

    if not thrust_sound.exists():
        generate_thrust_sound()
    if not heartbeat_low.exists():
        generate_heartbeat_sound("heartbeat_low.wav", 0x00)
    if not heartbeat_high.exists():
        generate_heartbeat_sound("heartbeat_high.wav", 0x04)
    if not player_shot.exists():
        generate_player_shot()
    if not extra_life.exists():
        generate_extra_life_sound()
    if not large_ufo.exists():
        generate_large_ufo_sound()
    if not small_ufo.exists():
        generate_small_ufo_sound()
    if not explosion_low.exists():
        generate_explosion_sound("explosion_low.wav", 0x3F)
    if not explosion_medium.exists():
        generate_explosion_sound("explosion_medium.wav", 0xFF)
    if not explosion_high.exists():
        generate_explosion_sound("explosion_high.wav", 0xBF)

def load_player_shot_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / PLAYER_SHOT_FILENAME))

def load_thrust_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / THRUST_FILENAME))

def load_extra_life_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / EXTRA_LIFE_FILENAME))

def load_large_ufo_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / "large_ufo.wav"))

def load_small_ufo_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / "small_ufo.wav"))

def load_small_explosion_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_high.wav"))

def load_medium_explosion_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_medium.wav"))

def load_large_explosion_sound() -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_low.wav"))


def play_test_sounds() -> None:
    initialize_audio()
    build_test_sounds()
    heartbeat_low = pygame.mixer.Sound(str(SOUNDS_DIR / "heartbeat_low.wav"))
    heartbeat_high = pygame.mixer.Sound(str(SOUNDS_DIR / "heartbeat_high.wav"))
    player_shot = pygame.mixer.Sound(str(SOUNDS_DIR / PLAYER_SHOT_FILENAME))

    heartbeat_low.play()
    pygame.time.wait(350)

    heartbeat_high.play()
    pygame.time.wait(350)

    player_shot.play()
    pygame.time.wait(350)

def play_test_thrust_sound() -> None:
    initialize_audio()
    build_test_sounds()
    thrust_sound = load_thrust_sound()
    channel = thrust_sound.play(loops=-1)

    pygame.time.wait(1500)
    if channel is not None:
        channel.stop()

def play_extra_life_sound() -> None:
    initialize_audio()
    build_test_sounds()
    extra_life_sound = load_extra_life_sound()
    extra_life_sound.play()

    pygame.time.wait(int(extra_life_sound.get_length() * 1000) + 250)

if __name__ == "__main__":
    initialize_audio()
    build_test_sounds()

    #large_ufo = pygame.mixer.Sound(str(SOUNDS_DIR / "large_ufo.wav"))
    #small_ufo = pygame.mixer.Sound(str(SOUNDS_DIR / "small_ufo.wav"))

    #large_ufo.play()
    #pygame.time.wait(1250)
    #small_ufo.play()
    #pygame.time.wait(1250)

    #explosion_low_sound = pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_low.wav"))
    #explosion_medium_sound = pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_medium.wav"))
    #explosion_high_sound = pygame.mixer.Sound(str(SOUNDS_DIR / "explosion_high.wav"))

    #explosion_low_sound.play()  # Play the low-pitch explosion.
    #pygame.time.wait(1200)  # Wait 1.2 seconds before playing the next sound.

    #explosion_medium_sound.play()  # Play the medium-pitch explosion.
    #pygame.time.wait(1200)  # Wait another 1.2 seconds.

    #explosion_high_sound.play()  # Play the high-pitch explosion.
    #pygame.time.wait(1200)  # Allow the final recording to finish.

    heartbeat_low_sound = pygame.mixer.Sound(str(SOUNDS_DIR / "heartbeat_low.wav"))
    heartbeat_high_sound = pygame.mixer.Sound(str(SOUNDS_DIR / "heartbeat_high.wav"))

    heartbeat_low_sound.play()
    pygame.time.wait(1500)
    heartbeat_high_sound.play()
    pygame.time.wait(1500)