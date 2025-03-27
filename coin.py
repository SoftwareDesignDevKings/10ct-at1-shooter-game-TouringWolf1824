import app
import math


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = app.pygame.Surface((15, 15), app.pygame.SRCALPHA)
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed = 2
        self.collect_range = 100
        self.collect_distance = 30
        



    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < self.collect_distance:
            return True
        if dist < self.collect_range:
            
            attract_str = 1 - (dist / self.collect_range)
            speed_fact = self.speed * (1 + attract_str)

            if dist > 0:
                self.x += (dx / dist) * speed_fact
                self.y += (dy / dist) * speed_fact
                self.rect.center = (self.x, self.y)

        return False


    def draw(self, surface):
        surface.blit(self.image, self.rect)




    