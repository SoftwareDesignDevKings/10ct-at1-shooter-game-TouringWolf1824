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

        self.exploded = False
        self.explosion = app.load_sprite_sheet("Explosion.png", 32, 32, 1)
        self.explosion_frame_index = 0

        #AOE ARGUMENTS/PROPERTIES#
        self.explosion_radius = 80
        self.explosion_pos = None
        self.aoe_timer = 0
        self.aoe_duration = 300  # 5 seconds at 60 FPS
        self.aoe_damage_interval = 20  # Apply damage every 20 frames (1/3 sec)
        self.aoe_damage_timer = 0
        self.aoe_active = False

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
            
            self.pixel_rect.center = (self.x, self.y)
            

        


            if self.x < 0 or self.x > app.WIDTH or self.y < 0 or self.y > app.HEIGHT:
                self.exploded = True
        else:
            if not self.aoe_active and self.explosion_pos:
                self.aoe_active = True
            if self.aoe_active == True:
                self.aoe_timer += 1
                self.aoe_damage_timer += 1
            
                if self.aoe_timer >= self.aoe_duration:
                    self.aoe_active = False
                    
            self.animation_timer += 1
            
            if self.animation_timer >= self.animation_speed and self.explosion_pos:
                self.animation_timer = 0
                self.explosion_frame_index += 1
                if self.explosion_frame_index >= len(self.explosion):
                    if not self.aoe_active:
                        return False    
                    self.explosion_frame_index = len(self.explosion)
        return True

        
    def explode(self, x, y):
        self.exploded = True
        self.explosion_pos = x, y
        self.x = x
        self.y = y
        self.explosion_frame_index = 0

    def get_aoe_enemies(self, enemies):
        if not self.aoe_active or not self.explosion_pos:
            return []
        
        affected_enemies = {}
        for enemy in enemies:
            
            dx = enemy.x - self.explosion_pos[0]
            dy = enemy.y - self.explosion_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= self.explosion_radius:
                affected_enemies[enemy] = 60
    
            elif enemy in affected_enemies:
                affected_enemies[enemy] -= 1
        
            if affected_enemies[enemy] <= 0:
                del affected_enemies[enemy]
            
        return affected_enemies
                
    def apply_aoe_damage(self, enemies):
        if not self.aoe_active:
            return False

        for enemy in self.get_aoe_enemies(enemies):
            enemy.take_damage(0.006)
            
    

        


    def draw(self, surface):
        if not self.exploded:
            surface.blit(self.rotated_image, self.rect)
        else:
            if self.explosion_frame_index < len(self.explosion):
                explosion_image = self.explosion[self.explosion_frame_index]
                explosion_rect = explosion_image.get_rect(center=(self.x, self.y))
                surface.blit(explosion_image, explosion_rect)

            if self.aoe_active and self.explosion_pos:

                aoe_surf = pygame.Surface((self.explosion_radius*2, self.explosion_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(aoe_surf, (255, 100, 0, ), (self.explosion_radius, self.explosion_radius), self.explosion_radius)
                surface.blit(aoe_surf, (self.explosion_pos[0] - self.explosion_radius, self.explosion_pos[1] - self.explosion_radius))