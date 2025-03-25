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

        self.image.set_alpha(128)
        
        
        # Calculate angle for rotation (in degrees)
        self.angle = math.degrees(math.atan2(vy, vx))
        
        # Create rotated image
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

        self.pixel = app.pygame.Surface((1, 1), app.pygame.SRCALPHA)
        self.pixel.fill((255,0,0,0))
        self.pixel_rect = self.pixel.get_rect(center=(self.x, self.y))

  
        #AOE ARGUMENTS/PROPERTIES#


    def update(self):

    
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
        
        self.pixel_rect.center = (self.x, self.y)
            


    def draw(self, surface):
        surface.blit(self.rotated_image, self.rect)
  



