#Import tools for inspecting the caller, writing JSON, doing time math,
#and describing dictionary shapes
import inspect
import json
import math
from datetime import datetime
from typing import NotRequired, TypedDict

#Define what one sprite's logged information can contain.
class SpriteInfo(TypedDict):
    type: str
    pos: NotRequired[list[float]]
    vel: NotRequired[list[float]]
    rad: NotRequired[float]
    rot: NotRequired[float]

#Define what one sprite group's logged information contains.
class GroupInfo(TypedDict):
    count: int
    sprites: list[SpriteInfo]

#Expose only the two logging functions from this module.
__all__ = ["log_state", "log_event"]

#Set the logger's constants
_FPS = 60
_MAX_SECONDS = 16
_SPRITE_SAMPLE_LIMIT = 10

#Create module-level variables
_frame_count = 0
_state_log_initialized = False
_event_log_initialized = False
_start_time = datetime.now()

#Define log_state:(Change the module-level frame counter and state-log flag.)
def log_state():
    global _frame_count, _state_log_initialized

    #If we have passed the maximum logging time return immediately.
    if _frame_count > _FPS * _MAX_SECONDS:
        return

    #Increase the frame counter by 1.
    _frame_count += 1

    #If this is NOT an exact 60-frame interval return immediately.
    if _frame_count % _FPS != 0:
        return

    # Record the current time
    now = datetime.now()
    # Get the current Python stack frame
    frame = inspect.currentframe()

    #If that failed return
    if frame is None:
        return

    #Move backward to the function that called log_state
    frame_back = frame.f_back
    #If there is no caller return
    if frame_back is None:
        return

    #Copy the caller's local variables
    local_vars = frame_back.f_locals.copy()

    #Create an empty place for the screen dimensions
    screen_size: list[int] = []
    #Create an empty dictionary for the discovered game state
    game_state: dict[str, object] = {}

    # For every local variable found in the caller, if the variable looks
    # like a pygame object and has a get_size method, then save its dimensions
    for key, value in local_vars.items():
        if "pygame" in str(type(value)) and hasattr(value, "get_size"):
            screen_size = list(value.get_size())
        #If the variable looks like a sprite Group create an empty list of sprite data
        if hasattr(value, "__class__") and "Group" in value.__class__.__name__:
            sprites_data: list[SpriteInfo] = []

            # Loop through the sprites with both an index and sprite:
            # If we have already sampled 10 sprites stop this loop.
            for i, sprite in enumerate(value):
                if i >= _SPRITE_SAMPLE_LIMIT:
                    break

                #Start a dictionary containing the sprite's class name
                sprite_info: SpriteInfo = {
                    "type": sprite.__class__.__name__
                }

                #If the sprite has position save rounded x and y coordinates
                if hasattr(sprite, "position"):
                    sprite_info["pos"] = [
                        round(sprite.position.x, 2),
                        round(sprite.position.y, 2),
                    ]

                #If the sprite has velocity save rounded x and y velocity
                if hasattr(sprite, "velocity"):
                    sprite_info["vel"] = [
                        round(sprite.velocity.x, 2),
                        round(sprite.velocity.y, 2),
                    ]
                # If the sprite has radius save it
                if hasattr(sprite, "radius"):
                    sprite_info["rad"] = round(sprite.radius)

                # If the sprite has rotation save it
                if hasattr(sprite, "rotation"):
                    sprite_info["rot"] = round(sprite.rotation, 2)

                # Append that sprite dictionary to the list
                sprites_data.append(sprite_info)

            # Build one dictionary describing the whole group
            # and save the total count and the sampled sprite list
            group_info: GroupInfo = {
                "count": len(value),
                "sprites": sprites_data,
            }

            # Store that group in game_state under its variable name
            game_state[key] = group_info

        # If no group information has been stored yet
        # and this variable itself has a position
        if len(game_state) == 0 and hasattr(value, "position"):
            # Treat it as an individual sprite and save its type
            single_sprite_info: SpriteInfo = {
                "type": value.__class__.__name__
            }
            # Save its position
            single_sprite_info["pos"] = [
                round(value.position.x, 2),
                round(value.position.y, 2),
            ]

            # If it has velocity, save velocity
            if hasattr(value, "velocity"):
                single_sprite_info["vel"] = [
                    round(value.velocity.x, 2),
                    round(value.velocity.y, 2),
                ]
            # If it has radius save radius
            if hasattr(value, "radius"):
                single_sprite_info["rad"] = round(value.radius)

            # If it has rotation, save rotation
            if hasattr(value, "rotation"):
                single_sprite_info["rot"] = round(value.rotation, 2)

            # Store that sprite in game_state
            game_state[key] = single_sprite_info

    # Build one complete log entry w/ timestamp, elapsed seconds,
    # current frame number, screen size, and all
    # collected game-state information
    entry: dict[str, object] = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "screen_size": screen_size,
        **game_state,
    }

    # If this is the first state log entry open the file in
    # write mode, otherwise open it in append mode
    mode = "w" if not _state_log_initialized else "a"

    # Convert the dictionary to JSON and write one JSON object per line
    with open("game_state.jsonl", mode) as f:
        f.write(json.dumps(entry) + "\n")

    # Mark the state log as initialized
    _state_log_initialized = True

# Define log_event
def log_event(event_type: str, **details: object) -> None:
    # Tell Python we are changing the module-level event-log flag
    global _event_log_initialized

    # Record the current time
    now = datetime.now()

    # Build an event dictionary timestamp, elapsed seconds, frame number,
    # event type, any extra event details supplied by the caller.
    event: dict[str, object] = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "type": event_type,
        **details,
    }

    # If this is the first event, open the event file in write mode
    # otherwise append to it
    mode = "w" if not _event_log_initialized else "a"
    with open("game_events.jsonl", mode) as f:
        # Write the event as one JSON line
        f.write(json.dumps(event) + "\n")

    # Mark the event log as initialized
    _event_log_initialized = True