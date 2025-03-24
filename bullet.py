import app
import math
import pygame
import app



class Bullet:
    def __init__(self, x, y, vx, vy, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size

        self.image = app.pygame.Surface((self.size, self.size), app.pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Fireball:
    def __init__(self, x, y, vx, vy, size,frames):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size

        self.frames = frames
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 4

        self.image = self.frames[self.frame_index]
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.rect.width = size // 2  # reduce hitbox size
        self.rect.height = size // 2
        self.opacity = 128  # reduce opacity
        self.image.set_alpha(self.opacity)
        
        
        # Calculate angle for rotation (in degrees)
        self.angle = math.degrees(math.atan2(vy, vx))
        
        # Create rotated image
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

        self.exploded = False
        self.explosion = app.load_sprite_sheet("Explosion.png", 32, 32, 1)
        self.explosion_frame_index = 0


    def update(self):
        if self.exploded == False:
            self.x += self.vx
            self.y += self.vy
        
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
            
            # Update rotated image with new frame
                self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
            
        # Update rect position
        
            self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
            if self.x < 0 or self.x > app.WIDTH or self.y < 0 or self.y > app.HEIGHT:
                self.exploded = True
        else:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.explosion_frame_index += 1
                if self.explosion_frame_index >= len(self.explosion):
                    return False  # Explosion finished
        return True

        
        
    def draw(self, surface):
        if not self.exploded:
            surface.blit(self.rotated_image, self.rect)
        else:
            if self.explosion_frame_index < len(self.explosion):
                explosion_image = self.explosion[self.explosion_frame_index]
                explosion_rect = explosion_image.get_rect(center=(self.x, self.y))
                surface.blit(explosion_image, explosion_rect)