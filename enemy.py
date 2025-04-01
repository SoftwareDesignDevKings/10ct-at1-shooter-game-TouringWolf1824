import pygame
import app
import math

#Import all required items#

class Enemy:
    def __init__(self, x, y, enemy_type, enemy_assets, speed=app.DEFAULT_ENEMY_SPEED): #Define enemy#
        self.x = x
        self.y = y #define its postition#
        
        self.speed = speed  #define its speed#
        
        
        self.frames = enemy_assets[enemy_type] #Get frames of the enemy, relative to what enemy it is#
        self.frame_index = 0 #Check which frame the enemy is on#
        self.animation_timer = 0 #Timer to cycle through frames#
        self.animation_speed = 8 #Speed at which it changes frames#
        self.image = self.frames[self.frame_index] #Which frame its on#
        self.rect = self.image.get_rect(center=(self.x, self.y)) #Define hitbox#
        
        self.enemy_type = enemy_type #Get enemy type (Which enemy it is)#
        self.facing_left = False #Whether or not enemy is facing left#
        


        self.knockback_dist_remaining = 0 #Knockback distnace it has left#
        self.knockback_dx = 0 #NEED TO LEARN#
        self.knockback_dy = 0

        self.max_health = 1.0 #How much HP each enemy has#
        self.health = self.max_health #Define HP as its max HP (1.0)#

    def update(self, player): #update enemy relative to player#

        if self.knockback_dist_remaining > 0: #If it has knockback dist remaining, run function apply_knockback#
            self.apply_knockback()
        else: #Otherwise move towards the player with fucntion move_toward_player#
            self.move_toward_player(player)
        self.animate() #Animate (cycle through frames@)




    def move_toward_player(self, player):
        # Calculates direction vector toward player#
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx**2 + dy**2) ** 0.5 #Get dist from player#
        
        if dist != 0: #Aslong as it still has a distance to go, run statment#
            self.x += (dx / dist) * self.speed #Update its position relative to speed#
            self.y += (dy / dist) * self.speed
        
        self.facing_left = dx < 0 #if its traveling towards the left (X is negative), face left = True#
        
        # Updates enemy position
        self.rect.center = (self.x, self.y) #Update its hitbox position#
        

    def apply_knockback(self): #Apply knockback function#
        step = min(app.ENEMY_KNOCKBACK_SPEED, self.knockback_dist_remaining) #NEED TO LEARN#
        self.knockback_dist_remaining -= step

        self.x += self.knockback_dx * step
        self.y += self.knockback_dy * step

        if self.knockback_dx < 0:
            self.facing_left = True
        else:
            self.facing_left = False

        self.rect.center = (self.x, self.y)

    def animate(self): #animate enemy#
        self.animation_timer += 1 #Add one to the timer#
        if self.animation_timer >= self.animation_speed: #If timer is Greater or equal to the speed, run code#
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = center
        #The above if bottlenecks speed of animation cycling by only doing it when timer is 8, making it 8 times slower then ruglar tick speed.
        #If it can update, make timer back to 0, update its animation and hitbox#
    def take_damage(self, amount): #Take damage function#
        self.health -= amount #Reduce health of enemy/player by amount#
        return self.health <= 0 #if health is less then/equal to 0, return True, use True for checks#

    def draw(self, surface): #Draw function#
        if self.facing_left: #If it is facing left, flip its image and then draw#
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, self.rect)
        else: #else draw without flipping#
            surface.blit(self.image, self.rect)


        if self.health < self.max_health: #If a enemy has taken damage, run statement#
            bar_width = 40 #Width of HP bar#
            bar_height = 5 #Height of HP bar#
            health_ratio = max(0, self.health / self.max_health) #Get its hp ratio of remaining hp to max hp#

            barX = self.x - bar_width//2 #Position of bar#
            barY = self.y - self.rect.height//2 - 10

            pygame.draw.rect(surface, (255, 0, 0), (barX, barY, bar_width, bar_height,)) #Draw Bar at position BarX, BarY, with given width and height#

            green_width = int(bar_width * health_ratio) #Amount HP remaining as width of the bar being green (Finds how much of bar should still be green)#
            if green_width > 0: #So long as it has HP/ it has width#
                pygame.draw.rect(surface, (0, 255, 0), (barX, barY, green_width, bar_height,)) #Draw bar#


            pygame.draw.rect(surface, (0,0,0), (barX, barY, bar_width, bar_height,), 1)  #else remove bar#

    def set_knockback(self, px, py, dist): #set the knockback to use in other function#
        dx = self.x - px #NEED TO LEARN#
        dy = self.y - py
        length = math.sqrt(dx*dx + dy*dy) 
        if length != 0:
            self.knockback_dx = dx / length
            self.knockback_dy = dy / length
            self.knockback_dist_remaining = dist
        