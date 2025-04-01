# app.py
import pygame
import os

#GIVEN CODE BELOW AND ABOVE#

# --------------------------------------------------------------------------
#                               CONSTANTS
# --------------------------------------------------------------------------

WIDTH = 1200
HEIGHT = 900
FPS = 60

PLAYER_SPEED = 3
DEFAULT_ENEMY_SPEED = 1

SPAWN_MARGIN = 50

ENEMY_SCALE_FACTOR = 2
PLAYER_SCALE_FACTOR = 2
FLOOR_TILE_SCALE_FACTOR = 2
HEALTH_SCALE_FACTOR = 3

PUSHBACK_DISTANCE = 80
ENEMY_KNOCKBACK_SPEED = 5

# --------------------------------------------------------------------------
#                       ASSET LOADING FUNCTIONS
# --------------------------------------------------------------------------

def load_frames(prefix, frame_count, scale_factor=1, folder="assets"):
    frames = []
    for i in range(frame_count):
        image_path = os.path.join(folder, f"{prefix}_{i}.png")
        img = pygame.image.load(image_path).convert_alpha()

        if scale_factor != 1:
            w = img.get_width() * scale_factor
            h = img.get_height() * scale_factor
            img = pygame.transform.scale(img, (w, h))

        frames.append(img)
    return frames

def load_floor_tiles(folder="assets"):
    floor_tiles = []
    for i in range(8):
        path = os.path.join(folder, f"floor_{i}.png")
        tile = pygame.image.load(path).convert()

        if FLOOR_TILE_SCALE_FACTOR != 1:
            tw = tile.get_width() * FLOOR_TILE_SCALE_FACTOR
            th = tile.get_height() * FLOOR_TILE_SCALE_FACTOR
            tile = pygame.transform.scale(tile, (tw, th))

        floor_tiles.append(tile)
    return floor_tiles

def load_assets():
    assets = {}

    # Enemies
    assets["enemies"] = {
        "orc":    load_frames("orc",    4, scale_factor=ENEMY_SCALE_FACTOR),
        "undead": load_frames("undead", 4, scale_factor=ENEMY_SCALE_FACTOR),
        "demon":  load_frames("demon",  4, scale_factor=ENEMY_SCALE_FACTOR),
    }

    # Player
    assets["player"] = {
        "idle": load_frames("player_idle", 4, scale_factor=PLAYER_SCALE_FACTOR),
        "run":  load_frames("player_run",  4, scale_factor=PLAYER_SCALE_FACTOR),
    }

    # Floor tiles
    assets["floor_tiles"] = load_floor_tiles()

    # Health images
    assets["health"] = load_frames("health", 6, scale_factor=HEALTH_SCALE_FACTOR)

    #Fireball assets#
    assets["Fire"] = load_frames("Fire", 4, scale_factor=0.08)

    assets["boom"] = load_sprite_sheet("Explosion.png", 32, 32, 5)

    assets["rock"] = load_sprite_sheet("Asteroids.png", 64, 64, 1)

    


    # Example coin image (uncomment if you have coin frames / images)
    # assets["coin"] = pygame.image.load(os.path.join("assets", "coin.png")).convert_alpha()

    return assets

def load_sprite_sheet(filename, frame_width, frame_height, scale_factor=1, folder="assets"): #def to convert sprite sheets into frames.#

    path = os.path.join(folder, filename)
    sheet = pygame.image.load(path).convert_alpha()
    
    # Calculate scaled dimensions
    scaled_width = int(frame_width * scale_factor)
    scaled_height = int(frame_height * scale_factor)
    
    # Get the dimensions of the sheet
    sheet_width, sheet_height = sheet.get_width(), sheet.get_height()
    
    # Calculate number of frames
    cols = sheet_width // frame_width
    rows = sheet_height // frame_height
    
    frames = []
    
    # Extract each frame
    for row in range(rows):
        for col in range(cols):
            # Location of the frame on the sprite sheet
            x = col * frame_width
            y = row * frame_height
            
            # Extract the frame
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            
            # Scale if needed
            if scale_factor != 1:
                frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
                
            frames.append(frame)
    
    return frames