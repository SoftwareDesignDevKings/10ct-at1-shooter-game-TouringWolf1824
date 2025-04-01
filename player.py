import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.
import math
import random
from bullet import Bullet
from bullet import Fireball
from bullet import Lightning

import state

#Import all required items#

class Player: # player classes#
    def __init__(self, x, y, assets): #define important vars#
        self.x = x
        self.y = y

        self.level = 1

        self.invincible = False
        self.invincible_time = 20
        self.invincible_timer = 0

        self.lightning_abilities = []
        self.lightning_cooldown = 300
        self.lightning_timer = 0

        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
    
    # Add fire animations to player animations for easy access
        if "Fire" in assets:
            self.animations["Fire"] = assets["Fire"]
        
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.FIRE_frame_index = 0
        self.FIRE_animation_timer = 0
        self.FIRE_animation_speed = 8
        self.FIRE_bullet_speed = 2
        self.FIRE_bullet_size = 1  
        self.FIRE_bullet_count = 1
        self.FIRE_shoot_cooldown = 20
        self.FIRE_shoot_timer = 0

        #image of an fireball animation#
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False

        self.health = 5

        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.shoot_cooldown = 20
        self.shoot_timer = 0

        self.projectiles = []



    def shoot_toward_position(self, tx, ty): #Shoot toward def#

        #Get pos#
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: #if shooting on you, dont shoot#
            return
        else:

            if state.FireBall == True: #If shooting a fireball, use fireball vars#
                vx = (dx / dist) * self.FIRE_bullet_speed
                vy = (dy / dist) * self.FIRE_bullet_speed
            else: #Else use bullet vars#
                vx = (dx / dist) * self.bullet_speed
                vy = (dy / dist) * self.bullet_speed
            #calc angle for multiple bullet shootings#
            angle_spread = 10
            base_angle = math.atan2(vy, vx)
            mid = (self.bullet_count - 1) / 2

            for i in range(self.bullet_count):
                offset = i - mid
                spread_radians = math.radians(angle_spread * offset)
                angle = base_angle + spread_radians
        #Calc angle with fire ball speed#
            if state.FireBall == True:

                final_vx = math.cos(angle) * self.FIRE_bullet_speed
                final_vy = math.sin(angle) * self.FIRE_bullet_speed


                fire_frames = self.animations["Fire"]

                
                # Make sure fire_frames is not None before creating a Fireball
                fireball = Fireball(self.x, self.y, final_vx, final_vy, self.FIRE_bullet_size, fire_frames)
                self.projectiles.append(fireball)



            else:  #Else use bullet vars#

                final_vx = math.cos(angle) * self.bullet_speed
                final_vy = math.sin(angle) * self.bullet_speed

                bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
                self.projectiles.append(bullet)


        self.shoot_timer = self.shoot_cooldown #reset timer to prevent spam shooting#

    def handle_input(self): #Handle movement inputs#
  

        keys = pygame.key.get_pressed() 
        vel_x, vel_y = 0, 0 
        #Move based on wasd keys pressed#
        if keys[pygame.K_a]: 
            # Move character left
            vel_x -= self.speed
        if keys[pygame.K_d]:
            vel_x += self.speed
        if keys[pygame.K_w]:
            vel_y -= self.speed
        if keys[pygame.K_s]:
            vel_y += self.speed

        self.x += vel_x #Get new pos#
        self.y += vel_y
        # Clamp player position to screen bounds

        self.x = max(0, min(self.x, app.WIDTH) ) 

        self.y = max(0, min(self.y, app. HEIGHT) )

        self. rect.center = (self.x, self.y)

        # animation state
        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        # direction
        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def update(self): #Update self#
        
        for projectile in self.projectiles: #Update all fireball/bullets#
            projectile.update()

        self.update_animation() #Update self#
        if self.invincible == True: #add Invincibile frames to stop double damage glitch#
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False 

        for lightning in list(self.lightning_abilities): #Update lightning ability#
            if lightning.update(self.x, self.y):  #if lightning done remove lightning#
                self.lightning_abilities.remove(lightning)
        if self.lightning_timer > 0: #time lightning to prevent spam#
            self.lightning_timer -= 1

    def update_animation(self): #update player anmimations#


        self.animation_timer += 1  #add to timer to slow animation cycles#
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0 #Reset timer#
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center
            #update player hitbox and animation#
        

    def draw(self, surface): #draw def#
  #while invincible, only draw 2 frames and then skip 2 frames to add flicker effect#
        if self.invincible and self.invincible_timer % 4 < 2:
            pass
        else: #otherwise draw player left/right#
            if self.facing_left:
                flipped_image = pygame.transform.flip(self.image, True, False)
                surface.blit(flipped_image, self.rect)
            else:
                surface.blit(self.image, self.rect)
#draw bullets and lightning#
        for bullet in self.projectiles:
            bullet.draw(surface)

        for lightning in self.lightning_abilities:
            lightning.draw(surface)

    def take_damage(self, amount): #Take damage def#
        if self.invincible == True: #If you are invincible, dont take damage#
            return


        self.health = max(0, self.health - amount) #define health#
        self.invincible = True #Make player invincible post damage#
        self.invincible_timer = self.invincible_time  #reset timer#

    def shoot_toward_mouse(self, pos): #shoot towards mouse pos def#
        mx, my = pos # m denotes mouse
        self.shoot_toward_position(mx, my)
        return True #if you can shoot toward mouse return true#
    

    def shoot_toward_enemy(self, enemy): #shoot toward enemy def as shoot toward position for enemys pos#
        self.shoot_toward_position(enemy.x, enemy.y)

#Def cast lightning. if cooldown up and there are enemies to target, fire lighting, stop enemy speed and add to lightning list#
    def cast_lightning(self, enemies, mouse_pos):
        if self.lightning_timer <= 0 and enemies:
            lightning = Lightning(self.x, self.y, enemies, mouse_pos)
            self.lightning_abilities.append(lightning)
            self.lightning_timer = self.lightning_cooldown
            for enemy in lightning.chain_targets:
                enemy.speed = 0
            
            return True #Return true to check if fired. prevent mana deduction when not being able to fire lightning#
        
    def pick_random_upgrades(self, num):
        possible_upgrades = [
            {"name": "Bigger Bullet",  "desc": "Bullet size +5"},
            {"name": "Faster Bullet",  "desc": "Bullet speed +2"},
            {"name": "Extra Bullet",   "desc": "Fire additional bullet"},
            {"name": "Shorter Cooldown", "desc": "Shoot more frequently"},
            {"name": "Up Lightning chain", "desc": "Attack 1 more enemy in Lightning strike"},
            {"name": "Faster Fireball", "desc": "Shoot Fireballs Faster"},       
        ]
        return random.sample(possible_upgrades, k=num)
#all upgrades possible, and define what they do, such as speed increase #
    def apply_upgrade(self, player, upgrade):
        name = upgrade["name"]
        if name == "Bigger Bullet":
            player.bullet_size += 5
        elif name == "Faster Bullet":
            player.bullet_speed += 2
        elif name == "Extra Bullet":
            player.bullet_count += 1
        elif name == "Shorter Cooldown":
            player.shoot_cooldown = max(1, int(player.shoot_cooldown * 0.8))
        elif name == "Up Lightning chain":
            lighning.max_chains = max(1, int(lightning.max_chains + 20))
        elif name == "Faster Fireball":
            player.FIRE_bullet_speed = max(1, int(player.FIRE_bullet_speed + 2))


