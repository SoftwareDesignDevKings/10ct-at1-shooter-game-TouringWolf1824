# game.py
import pygame
import random
import os

import app
import math
from player import Player
from enemy import Enemy
from coin import Coin

import state



class Game:
    def __init__(self):
        pygame.init()  
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Quinn's Shooter")
        self.clock = pygame.time.Clock()

        self.assets = app.load_assets()
        self.mana = 100

        
        self.mana_clock = 0


        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        # TODO: Set up game state variables
        self.running = True
        self.game_over = False
        
        self.coins = []

        self.targeted = {}
        self.hit = []
        self.check_interval = 50

        self.enemy_spawn_interval = 100


        self.reset_game()

        # TODO: Create a random background
        # self.background = ?
        
    def reset_game(self):
        
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.game_over = False
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 3
        self.coins = []


    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            
            self.clock.tick(app.FPS)
        
            self.handle_events()
            if not self.game_over:
                self.update()
            

                

            self.draw()

        pygame.quit()

    def handle_events(self):

        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
                if event.key == pygame.K_SPACE:
                    nearest_enemy = self.find_nearest_enemy()
                    if nearest_enemy:
                        self.player.shoot_toward_enemy(nearest_enemy)
                        
                        self.mana = max(0, self.mana - 1)


                    

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.player.shoot_toward_mouse(event.pos)
                    self.mana = max(0, self.mana - 1)

            
                elif event.button == 3:    
                    state.FireBall = True
                    self.player.shoot_toward_mouse(event.pos)
                    self.mana = max(0, self.mana - 3)

                    state.FireBall = False




    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            if enemy not in self.targeted:
                dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy


                    
                    
        self.targeted[nearest] = self.check_interval
        return nearest
    
    def update(self):
        self.player.handle_input()
        self.player.update()
        self.mana_clock += 1
        for enemy in self.enemies:
            enemy.update(self.player)
    
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.spawn_enemies()

        if self.player.health <= 0:
            self.game_over = True
            return
        if self.mana >= 100:
            pass
        else:
            if self.mana_clock >= 60:
                self.mana += 1
                self.mana_clock = 0
        for enemy in list(self.targeted):
            self.targeted[enemy] -= 1
            if self.targeted[enemy] <= 0:
                if enemy in self.enemies:
                    del self.targeted[enemy]
     #   for coin in self.coins:
       #     coin.update(self.player)


    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for coin in self.coins:
            coin.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen) 

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))
        self.Fire_img = self.assets["Fire"]
        mana_text = self.font_small.render(f"Mana: {self.mana}/100", True, (0, 100, 255))
        self.screen.blit(mana_text, (10, 50))

        if self.game_over:
            self.draw_game_over_screen()



        pygame.display.flip()

    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

                enemy_type = random.choice(list(self.assets["enemies"].keys()))
                enemy = Enemy(x, y, enemy_type, self.assets["enemies"])
                self.enemies.append(enemy)

    def check_player_enemy_collisions(self):
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break
    


        if collided:
            self.player.take_damage(1)
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def check_bullet_enemy_collisions(self):

        for bullet in self.player.projectiles:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    try:
                        self.player.projectiles.remove(bullet)
                    except ValueError:
                        pass
                    new_coin = Coin(enemy.x, enemy.y)
                    self.coins.append(new_coin)
                    self.enemies.remove(enemy)
                    break
       ####HERE PLS ####



    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        # Prompt to restart or quit
        prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

