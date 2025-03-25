# game.py
import pygame
import random
import os

import app
import math
from player import Player
from enemy import Enemy
from coin import Coin
from bullet import Bullet
from bullet import Fireball

import state



class Game:
    def __init__(self):
        pygame.init()  
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Quinn's Shooter")
        self.clock = pygame.time.Clock()

        self.assets = app.load_assets()
        self.mana = 100

        self.is_aoe_active = False
        self.aoe_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.aoe_pos = None
        self.aoe_radius = 60
        self.aoe_opacity = 100  # Initial opacity
        self.is_aoe_active = False
        self.aoe_time = 0
        self.aoe_timer = 300
        self.wait_time = 0

        self.active_explosions = []
        self.active_aoe_effects = []

        
        self.explosion_frames = self.assets['boom']
        
          
            
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

        
        self.wait_time = 0
        self.aoe_time = 0
        self.aoe_timer = 300

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
        self.xp = 0
        self.lvl = 1
        self.mana = 100


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



        self.update_coins()
    
        self.check_bullet_enemy_collisions()
        self.check_player_enemy_collisions()

        self.spawn_enemies()

        if self.player.health <= 0:
            self.game_over = True
            return
        if self.mana <= 100 and self.mana_clock >= 60:
            
        
            self.mana += 1
            self.mana_clock = 0
            
        for enemy in list(self.targeted):
            self.targeted[enemy] -= 1
            if self.targeted[enemy] <= 0:
                if enemy in self.enemies:
                    del self.targeted[enemy]
        for enemy in self.enemies:
            if enemy.health <= 0:
                new_coin = Coin(enemy.x, enemy.y)
                self.coins.append(new_coin)
                self.enemies.remove(enemy)



        for explosion in list(self.active_explosions):
            explosion['frame_timer'] += 1
            if explosion['frame_timer'] >= explosion['frame_delay']:
                explosion['frame_timer'] = 0
                explosion['current_frame'] += 1
                
                # Remove explosion if animation is complete
                if explosion['current_frame'] >= len(explosion['frames']):
                    self.active_explosions.remove(explosion)

        for aoe_effect in list(self.active_aoe_effects):
            aoe_effect['time'] += 1

            aoe_effect['opacity'] = max(0, 100 - (aoe_effect['time'] * 0.3)) 
            
            for enemy in list(self.enemies):
                distance = math.dist((enemy.x, enemy.y), aoe_effect['pos'])
                if distance <= aoe_effect['radius']:
                    enemy.take_damage(0.01)
                    
            if aoe_effect['time'] >= aoe_effect['duration'] or aoe_effect['opactiy'] <= 0:
                self.active_aoe_effects.remove(aoe_effect)
        

        
       


                
            

    def update_coins(self):
        for coin in list(self.coins):
            if coin.update(self.player):
                self.coins.remove(coin)
                self.xp += 1

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if not self.game_over:
            self.player.draw(self.screen)

        for coin in self.coins:
            coin.draw(self.screen)

        

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))
        self.Fire_img = self.assets["Fire"]
        mana_text = self.font_small.render(f"Mana: {self.mana}/100", True, (0, 100, 255))
        self.screen.blit(mana_text, (10, 50))
        
        # Draw mana bar visual
        mana_bar_width = 200
        mana_bar_height = 20
        mana_bar_x = 10
        mana_bar_y = 80
        
        # Background (empty)
        pygame.draw.rect(self.screen, (50, 50, 100), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
        
        # Filled portion
        filled_width = int((self.mana / 100) * mana_bar_width)
        if filled_width > 0:
            pygame.draw.rect(self.screen, (50, 50, 255), (mana_bar_x, mana_bar_y, filled_width, mana_bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 2)
        
        # Draw XP counter
        xp_text = self.font_small.render(f"XP: {self.xp}", True, (255, 215, 0))
        self.screen.blit(xp_text, (10, 110))

        for aoe_effect in self.active_aoe_effects:
            # Create a surface for each AOE effect
            aoe_surface = pygame.Surface((aoe_effect['radius'] * 2, aoe_effect['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                aoe_surface, 
                (255, 0, 0, aoe_effect['opacity']), 
                (aoe_effect['radius'], aoe_effect['radius']), 
                aoe_effect['radius']
            )
            
            # Draw the AOE surface centered on the effect position
            draw_pos = (
                aoe_effect['pos'][0] - aoe_effect['radius'], 
                aoe_effect['pos'][1] - aoe_effect['radius']
            )
            self.screen.blit(aoe_surface, draw_pos)

        for explosion in self.active_explosions:
            frame = explosion['frames'][explosion['current_frame']]
            frame_rect = frame.get_rect(center=(explosion['x'], explosion['y']))
            self.screen.blit(frame, frame_rect)


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
        for projectile in list(self.player.projectiles):
            # Check if it's a Fireball and has a pixel_rect
            if hasattr(projectile, 'pixel_rect'):
                for enemy in list(self.enemies):
                    # Use the tiny pixel rect for precise collision
                    if projectile.pixel_rect.colliderect(enemy.rect):
                        try:
                            self.player.projectiles.remove(projectile)
                        except ValueError:
                            pass
                        
                        enemy.take_damage(2)
                        # AOE damage to nearby enemies
                        death_pos = (enemy.x, enemy.y)
                        
                        # Find all enemies within AOE radius
                        for nearby_enemy in list(self.enemies):
                            if math.dist((nearby_enemy.x, nearby_enemy.y), death_pos) <= 100:
                                nearby_enemy.take_damage(0.6)

                        explosion_data = {
                            'x': death_pos[0],
                            'y': death_pos[1],
                            'frames': self.explosion_frames,
                            'current_frame': 0,
                            'frame_timer': 0,
                            'frame_delay': 4  # Adjust speed of animation
                        }
                        self.active_explosions.append(explosion_data)

                        new_aoe_effect = {
                            'pos': death_pos,
                            'radius': 100,
                            'time': 0,
                            'duration': 300,
                            'opactiy': 150
                        }

                        # Set up AOE circle
                        self.active_aoe_effects.append(new_aoe_effect)

                        

                        # Handle active AOE circle
                        if self.is_aoe_active:
                            # Redraw surface with current opacity
                            self.aoe_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                            pygame.draw.circle(
                                self.aoe_surface, 
                                (255, 0, 0, self.aoe_opacity), 
                                (60, 60), 
                                60
                            )
                        
                        
                            

 

            else:  # Regular bullet
                for enemy in list(self.enemies):
                    if projectile.rect.colliderect(enemy.rect):
                        try:
                            self.player.projectiles.remove(projectile)
                        except ValueError:
                            pass
                        
                        enemy.take_damage(1)
                





    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        score_surf = self.font_small.render(f"Final XP: {self.xp}", True, (255, 215, 0))
        score_rect = score_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2))
        self.screen.blit(score_surf, score_rect)

        # Prompt to restart or quit
        prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

