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

#Import all required items#

class Game: #Create class for game to import into Main#
    def __init__(self): #Create def to essentially store ALL variables used anywhere within gam#
        pygame.init()  
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT)) #Create game window#
        pygame.display.set_caption("Quinn's Shooter") #set window name#
        self.clock = pygame.time.Clock() #set clock#

        self.assets = app.load_assets()
        self.mana = 100

        self.in_level_up_menu = False
        self.upgrade_options = []

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

        self.background = self.create_random_background( #Create background as random tiles#
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
        
    def reset_game(self): #Run when game reset, resets player pos enemies mana lvl xp#
        
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.game_over = False
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 3
        self.coins = []
        self.xp = 0
        self.lvl = 1
        self.mana = 100


    def create_random_background(self, width, height, floor_tiles): # Def to create background, randomly rotates and picks tiles#
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self): #While the game is running, tick the clock at 60FPS , handle events and draw and update#
        while self.running:
            
            self.clock.tick(app.FPS)
        
            self.handle_events()
            if not self.game_over and not self.in_level_up_menu:
                self.update()

            

                

            self.draw()

        pygame.quit()

    def handle_events(self): #Handle keys and events pressed#

        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN: #If a key was pressed, check#
                if self.game_over: #If in game over screen, let user reset/end window and game#
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif not self.in_level_up_menu:
                    
            
                    if event.key == pygame.K_SPACE: #If hit space, run find nearest enemy and shoot towards. Deduct 1 mana if shot#
                        nearest_enemy = self.find_nearest_enemy()
                        if nearest_enemy:
                            self.player.shoot_toward_enemy(nearest_enemy)
                            
                            self.mana = max(0, self.mana - 1)
                    if event.key == pygame.K_q: #If Q is pressed, cast lightning. If you are able to and did cast, deduct 5 mana#
                        
                        
                        if self.player.cast_lightning(self.enemies, pygame.mouse.get_pos()):
                            self.mana = max(0, self.mana - 5)

                else:
                    #In upgrade menu#
                    # In upgrade menu
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        index = event.key - pygame.K_1  # 0,1,2
                        if 0 <= index < len(self.upgrade_options):
                            upgrade = self.upgrade_options[index]
                            self.apply_upgrade(self.player, upgrade)
                            self.in_level_up_menu = False
                     


                    

            elif event.type == pygame.MOUSEBUTTONDOWN: #Else if a mouse button was pressed, run#
                if event.button == 1:  # Left mouse button pressed, shoot bullet towards mouse and take 1 mana if bullet shot#
                    
                    if self.player.shoot_toward_mouse(event.pos): 
                        self.mana = max(0, self.mana - 1)

            
                elif event.button == 3:    #Right mouse button pressed, Alter state.fireball to True, then run as if it was a bullet. If fireball shot, deduct 3 mana.#
                    state.FireBall = True 
                    if self.player.shoot_toward_mouse(event.pos):
                        self.mana = max(0, self.mana - 3)

                    state.FireBall = False
                    #As fireball runs off the same logic as bullets in its travel and such, we may run off the same functions.#
                    #As such, we change state.Fireball to True then false, and check if Fireball == True in bullet to run a fireball instead of a bullet.#



    def find_nearest_enemy(self): #Find nearest enemy def#
        if not self.enemies:
            return None #If there are no enemies, return none#
        nearest = None #Set var nearest as none#
        min_dist = float('inf') #set var min_dist as a float#
        px, py = self.player.x, self.player.y #Get players pos#

        #For every enemy, so long as the enemy isnt targeted already by a find nearest enemy, get its distance to player, setting min_dist and enemy as that enemy if it was smaller then the last enemy.
        #This returns the closest enemy that isnt already targeted by a nearest enemy bullet#
        for enemy in self.enemies:
            if enemy not in self.targeted:
                dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy


                    
                    
        self.targeted[nearest] = self.check_interval #Set the key in self.targeted dictionary as the targeted enemy, and the check interval as its value#
        return nearest #Return nearest enemy#
    
    def update(self): #Update self function#
        self.player.handle_input() #Check for inputs#
        self.player.update() #update pos#
        self.mana_clock += 1 #Add 1 to mana#
        for enemy in self.enemies: #Update all enemies#
            enemy.update(self.player)


        #Update coins, check for collisions and spawn enemies#
        self.update_coins()
    
        self.check_bullet_enemy_collisions()
        self.check_player_enemy_collisions()

        self.spawn_enemies()
        self.check_for_level_up
        #check if player dead, if dead make game over#
        if self.player.health <= 0:
            self.game_over = True
            return #Return#

        if self.mana < 100 and self.mana_clock >= 60: # If mana is not maxxed out, and its been 1 second, add one mana and reset man clock#
            
        
            self.mana += 1
            self.mana_clock = 0
            
        #For enemy targeted by a auto target bullet, if its not dead in 1/3 of a second remove from targeted so it cna be targeted by another auto target bullet.#
        #This handles the cases where another enemy walked infront of the bullet/the bullet missed, so the enemy can be still auto targeted#
        for enemy in list(self.targeted):
            self.targeted[enemy] -= 1
            if self.targeted[enemy] <= 0:
                if enemy in self.enemies:
                    del self.targeted[enemy]

        for enemy in self.enemies: #If an enemy is dead, remove it and place a coin where it died#
            if enemy.health <= 0:
                new_coin = Coin(enemy.x, enemy.y)
                self.coins.append(new_coin)
                self.enemies.remove(enemy)
                
        for coin in self.coins: #update coins#
            coin.update(self.player)




        for explosion in list(self.active_explosions): #For each running explosion, add 1 to the counter at 'Frame_delay' intervals#
            #This slows the explosion down so it looks better instead of updating animation every frame#
            explosion['frame_timer'] += 1
            if explosion['frame_timer'] >= explosion['frame_delay']:
                explosion['frame_timer'] = 0
                explosion['current_frame'] += 1
                
                # Remove explosion if animation is complete#
                if explosion['current_frame'] >= len(explosion['frames']):
                    self.active_explosions.remove(explosion)

        #For every aoe effect active, add one to its time#
        for aoe_effect in list(self.active_aoe_effects):
            aoe_effect['time'] += 1
            #Reduce opactiy relative to its time remaining so it fades#
            aoe_effect['opacity'] = max(0, 100 - (aoe_effect['time'] * 0.3)) 
            #If enemy within a running aoes radius, take damage 0.01 every frame#
            for enemy in list(self.enemies):
                distance = math.dist((enemy.x, enemy.y), aoe_effect['pos'])
                if distance <= aoe_effect['radius']:
                    enemy.take_damage(0.01)
            #If its ran out of time or it fades completely, remove the aoe#
            if aoe_effect['time'] >= aoe_effect['duration'] or aoe_effect['opactiy'] <= 0:
                self.active_aoe_effects.remove(aoe_effect)


        

                
            
    #Update coins, check colisions, if player picked up add 1 to xp#
    def update_coins(self):
        for coin in list(self.coins):
            if coin.update(self.player):
                self.coins.remove(coin)
                self.xp += 1
    #Draw function#
    def draw(self):
        self.screen.blit(self.background, (0, 0)) #Draw background#

        if not self.game_over: #If game is still running, draw screen and player#
            self.player.draw(self.screen)

        for coin in self.coins: #Draw coins#
            coin.draw(self.screen)

        

        for enemy in self.enemies: #Draw player#
            enemy.draw(self.screen)

        #Draw mana xp and hp bar#
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
        
        # Filled portion of mana bar#
        filled_width = int((self.mana / 100) * mana_bar_width)
        if filled_width > 0:
            pygame.draw.rect(self.screen, (50, 50, 255), (mana_bar_x, mana_bar_y, filled_width, mana_bar_height))
        
        # Border of mana bar#
        pygame.draw.rect(self.screen, (255, 255, 255), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 2)
        
        # Draw XP counter
        xp_text = self.font_small.render(f"XP: {self.xp}", True, (255, 215, 0))
        self.screen.blit(xp_text, (10, 110))

        for aoe_effect in self.active_aoe_effects: #for every running aoe effect :#
            # Create a surface for each AOE effect
            aoe_surface = pygame.Surface((aoe_effect['radius'] * 2, aoe_effect['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle( #Draw red circle#
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
            self.screen.blit(aoe_surface, draw_pos) #Draw final #

        for explosion in self.active_explosions: #For every running explosion, draw it, and draw hitbox#
            frame = explosion['frames'][explosion['current_frame']]
            frame_rect = frame.get_rect(center=(explosion['x'], explosion['y']))
            self.screen.blit(frame, frame_rect)


        if self.game_over: #If its game over run and draw the game over screen#
            self.draw_game_over_screen()

        #determine how much xp 
        next_level_xp = self.player.level * self.player.level * 5
        xp_to_next = max(0, next_level_xp - self.xp)
        xp_next_surf = self.font_small.render(f"Next Lvl XP: {xp_to_next}", True, (255, 255, 255))
        self.screen.blit(xp_next_surf, (10, 100))

        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def spawn_enemies(self): #Spawn enemies randomy and the interval, from either top left bottom or right, with a random enemy type#
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
#Check if the player hitbox collided with a enemy hitbox. if it did, take a damage, then run knockback for enemies##
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
                
    def check_bullet_enemy_collisions(self): #Check for projectile hitting enemies#
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
                        
                        enemy.take_damage(2) #Take damage to immediate enemy#
                        # AOE damage to nearby enemies
                        death_pos = (enemy.x, enemy.y)
                        
                        # Find all enemies within AOE radius
                        for nearby_enemy in list(self.enemies):
                            if math.dist((nearby_enemy.x, nearby_enemy.y), death_pos) <= 100:
                                nearby_enemy.take_damage(0.6) #damage enemies within explosions radius#

                        explosion_data = { #Variables for the explosion#
                            'x': death_pos[0],
                            'y': death_pos[1],
                            'frames': self.explosion_frames,
                            'current_frame': 0,
                            'frame_timer': 0,
                            'frame_delay': 4  # Adjust speed of animation
                        }
                        self.active_explosions.append(explosion_data) #add explosion data to explosion list

                        new_aoe_effect = { #Vars for aoe#
                            'pos': death_pos,
                            'radius': 100,
                            'time': 0,
                            'duration': 300,
                            'opactiy': 150
                        }

                        # Set up AOE circle
                        self.active_aoe_effects.append(new_aoe_effect) #add aoe data$

                        

                        # Handle active AOE circle
                        if self.is_aoe_active:
                            # Redraw surface with current opacity
                            self.aoe_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                            pygame.draw.circle( #circle info#
                                self.aoe_surface, 
                                (255, 0, 0, self.aoe_opacity), 
                                (60, 60), 
                                60
                            )
                        
            

            else:  # if Regular bullet#
                for enemy in list(self.enemies): #For each enemy, if collide with bullet remove bullet and take 1 damage#
                    if projectile.rect.colliderect(enemy.rect):
                        try: #Use try, as occasionally it has a value error in removing bullet, creashing the game#
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
        # XP text#
        score_surf = self.font_small.render(f"Final XP: {self.xp}", True, (255, 215, 0))
        score_rect = score_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2))
        self.screen.blit(score_surf, score_rect)

        # Prompt to restart or quit
        prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

    def draw_upgrade_menu(self):
        # Dark overlay behind the menu
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_surf = self.font_large.render("Choose an Upgrade!", True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 3 - 50))
        self.screen.blit(title_surf, title_rect)

        # Options
        for i, upgrade in enumerate(self.upgrade_options):
            text_str = f"{i+1}. {upgrade['name']} - {upgrade['desc']}"
            option_surf = self.font_small.render(text_str, True, (255, 255, 255))
            line_y = app.HEIGHT // 3 + i * 40
            option_rect = option_surf.get_rect(center=(app.WIDTH // 2, line_y))
            self.screen.blit(option_surf, option_rect)

    def check_for_level_up(self):
        xp_needed = self.player.level * self.player.level * 5
        if self.player.xp >= xp_needed:
            # Leveled up
            self.player.level += 1
            self.in_level_up_menu = True
            self.upgrade_options = self.pick_random_upgrades(3)

            # Increase enemy spawns each time we level up
            self.enemies_per_spawn += 1