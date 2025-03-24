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


  #  def update(self, player):
        #dx = player.x - self.x
        #dy = player.y = self.y
        #dist = math.sqrt(dx**2 + dy**2)
       # if dist < self.collect_range:
       #     if dist != 0:
       #         self.x += (dx / dist) * self.speed
       ##         self.y += (dy / dist) * self.speed
      #     self.rect.center = (self.x, self.y)
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    