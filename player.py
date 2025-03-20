import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.
import math
from bullet import Bullet

class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y


        self.invincible = False  # Track if the player is invincible
        self.invincible_time = 20  # Duration of invincibility in frames (1 second if 60 FPS)
        self.invincible_timer = 0 



        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False

        self.health = 5

        self.FireBall_LIST = []

        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.shoot_cooldown = 20
        self.shoot_timer = 0
        self.bullets = []



    def shoot_toward_position(self, tx, ty):
        if self.shoot_timer >= self.shoot_cooldown:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        angle_spread = 10
        base_angle = math.atan2(vy, vx)
        mid = (self.bullet_count - 1) / 2

        for i in range(self.bullet_count):
            offset = i - mid
            spread_radians = math.radians(angle_spread * offset)
            angle = base_angle + spread_radians

            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed

            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
            self.bullets.append(bullet)
        self.shoot_timer = 0

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
        

    def update(self):
        self.update_animation()
        if self.invincible == True:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def update_animation(self):
        for bullet in self.bullets:
            bullet.update()
            if bullet.y < 0 or bullet.y > app.HEIGHT or bullet.x < 0 or bullet.x > app.WIDTH:
                self.bullets.remove(bullet)

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
  
        if self.facing_left:
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

        for bullet in self.bullets:
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
        