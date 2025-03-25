import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.
import math
from bullet import Bullet
from bullet import Fireball
import state


class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y

        self.invincible = False
        self.invincible_time = 20
        self.invincible_timer = 0

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
        self.FIRE_bullet_size = 1  # Increased size for better visibility
        self.FIRE_bullet_count = 1
        self.FIRE_shoot_cooldown = 20
        self.FIRE_shoot_timer = 0


        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False

        self.health = 50

        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.shoot_cooldown = 20
        self.shoot_timer = 0

        self.projectiles = []



    def shoot_toward_position(self, tx, ty):


        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return
        else:

            if state.FireBall == True:
                vx = (dx / dist) * self.FIRE_bullet_speed
                vy = (dy / dist) * self.FIRE_bullet_speed
            else:
                vx = (dx / dist) * self.bullet_speed
                vy = (dy / dist) * self.bullet_speed

            angle_spread = 10
            base_angle = math.atan2(vy, vx)
            mid = (self.bullet_count - 1) / 2

            for i in range(self.bullet_count):
                offset = i - mid
                spread_radians = math.radians(angle_spread * offset)
                angle = base_angle + spread_radians

            if state.FireBall == True:

                final_vx = math.cos(angle) * self.FIRE_bullet_speed
                final_vy = math.sin(angle) * self.FIRE_bullet_speed


                fire_frames = self.animations["Fire"]

                
                # Make sure fire_frames is not None before creating a Fireball
                fireball = Fireball(self.x, self.y, final_vx, final_vy, self.FIRE_bullet_size, fire_frames)
                self.projectiles.append(fireball)



            else:  

                final_vx = math.cos(angle) * self.bullet_speed
                final_vy = math.sin(angle) * self.bullet_speed

                bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
                self.projectiles.append(bullet)


        self.shoot_timer = self.shoot_cooldown

    def handle_input(self):
        """Check and respond to keyboard/mouse input."""

        keys = pygame.key.get_pressed()
        vel_x, vel_y = 0, 0

        if keys[pygame.K_a]:
            # Move character left
            vel_x -= self.speed
        if keys[pygame.K_d]:
            vel_x += self.speed
        if keys[pygame.K_w]:
            vel_y -= self.speed
        if keys[pygame.K_s]:
            vel_y += self.speed

        self.x += vel_x
        self.y += vel_y
        # TODO: 3. Clamp player position to screen bounds

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

    def update(self):
        
        for projectile in self.projectiles:
            projectile.update()

        self.update_animation()
        if self.invincible == True:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def update_animation(self):


        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center
        

    def draw(self, surface):
  
        if self.invincible and self.invincible_timer % 4 < 2:
            pass
        else:
            if self.facing_left:
                flipped_image = pygame.transform.flip(self.image, True, False)
                surface.blit(flipped_image, self.rect)
            else:
                surface.blit(self.image, self.rect)

        for bullet in self.projectiles:
            bullet.draw(surface)

    def take_damage(self, amount):
        if self.invincible == True:
            return


        self.health = max(0, self.health - amount)
        self.invincible = True
        self.invincible_timer = self.invincible_time 

    def shoot_toward_mouse(self, pos):
        mx, my = pos # m denotes mouse
        self.shoot_toward_position(mx, my)
    

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)
        