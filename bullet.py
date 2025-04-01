import app
import math
import pygame
import app
import random

#Import all required items#

class Bullet: #denote bullet class, define variables required#
    def __init__(self, x, y, vx, vy, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        #Bullet draw defs#
        self.image = app.pygame.Surface((self.size, self.size), app.pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self): #update position by velocity and update hitbox#
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface): #Draw bullet#
        surface.blit(self.image, self.rect)

class Fireball: #Denote fireball class and required vars#
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


    def update(self): #Update projectile fireball#

    #update pos#
        self.x += self.vx
        self.y += self.vy
    #update timer at animation_speed interval#
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
        
        # Update rotated image with new frame
            self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        
    # Update rect position of small pixel. The small pixel attatched to the fireball is what is used as the fireballs rect. 
    #Using this allows for a much tighter and accurate hitbox, as the fireball sprite was massive#

        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        
        self.pixel_rect.center = (self.x, self.y)
            

#Draw def for fireball. drawws fireball onto screen#
    def draw(self, surface):
        surface.blit(self.rotated_image, self.rect)
  







class Lightning: #denote lighting class and important vars in init def#
    def __init__(self, start_x, start_y, enemies, mouse_pos,):
        self.start_x = start_x
        self.start_y = start_y
        self.enemies = enemies
        self.mouse_pos = mouse_pos
        self.chain_targets = []
        self.lightning_segments = []
        self.duration = 180  # 3 seconds at 60 FPS
        self.time_alive = 0
        self.max_chains = 10  

        



        # Find initial target
        self.find_chain_targets()

    def find_chain_targets(self):#find chain def#
        # Sort enemies by distance from mouse position
        sorted_enemies = sorted(
            self.enemies, 
            key=lambda e: math.dist((e.x, e.y), self.mouse_pos)
        )

        # Select up to max_chains closest enemies
        self.chain_targets = sorted_enemies[:self.max_chains]

    def generate_lightning_segment(self, start, end):
        # Create jagged lightning segment
        
        points = [start]
        segments = 5 #Denotes how many segments a single line should be cut into#
        for i in range(1, segments):
            # Interpolate between start and end
            x = start[0] + (end[0] - start[0]) * (i / segments)
            y = start[1] + (end[1] - start[1]) * (i / segments)

            # Add some randomness, this moves the segments randomly, and when reconnected makes it look jagged#
            x += random.uniform(-10, 10)
            y += random.uniform(-10, 10)
            points.append((x, y))
        points.append(end)
        return points

    def update(self, x, y): #lighting update def#
        self.x = x #Update pos#
        self.y = y

        self.time_alive += 1 # add to timer#
         
        # Generate lightning segments
        self.lightning_segments = []
        prev_point = (self.x, self.y)
        
        for enemy in self.chain_targets: 
            # Damage enemies
            enemy.take_damage(0.35 / 60)  # Damage per frame
            
            # Generate lightning segment
            segment = self.generate_lightning_segment(prev_point, (enemy.x, enemy.y))
            self.lightning_segments.append(segment)
            
            # Update previous point for next iteration
            prev_point = (enemy.x, enemy.y)
            

        # Check if duration is over
        return self.time_alive >= self.duration

    def draw(self, surface):
        # Draw lightning segments
        for segment in self.lightning_segments:
            if len(segment) > 1:
                # Draw multiple segments with thickness and color variation
                pygame.draw.lines(surface, (100, 100, 255), False, segment, 3)
                pygame.draw.lines(surface, (200, 200, 255), False, segment, 1)

        # Pulsate effect for targeted enemies
        for enemy in self.chain_targets:
            # Create a pulsating blue overlay
            pulsate_surface = pygame.Surface((enemy.rect.width, enemy.rect.height), pygame.SRCALPHA)
            alpha = int(100 + 50 * math.sin(self.time_alive * 0.5))
            pulsate_surface.fill((0, 0, 255, alpha))
            surface.blit(pulsate_surface, enemy.rect) #draw lightning#