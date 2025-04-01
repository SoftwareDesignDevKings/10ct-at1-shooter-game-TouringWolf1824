import app
import math

#Import all required items#

class Coin: #Define Coin class#
    def __init__(self, x, y): #get its position with x and y#
        self.x = x
        self.y = y
        self.image = app.pygame.Surface((15, 15), app.pygame.SRCALPHA) #Create a coin object#
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed = 2   #Define the speed of a coin when close to player#
        self.collect_range = 100 #Distance at which coins float to you#
        self.collect_distance = 30 #Distance at which you can collect coins#
        



    def update(self, player): #Coin attraction feature#
        dx = player.x - self.x #Get distance from player#
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2) 
        if dist < self.collect_distance: #if within pickup range, return true to pickup#
            return True
        if dist < self.collect_range:  #if within drag range, run code#
            
            attract_str = 1 - (dist / self.collect_range) #Calculate increasing speed of drag as it gets closer#
            speed_fact = self.speed * (1 + attract_str)

            if dist > 0: #as long as its not on you, pickup. prevents divide by 0 error#
                self.x += (dx / dist) * speed_fact
                self.y += (dy / dist) * speed_fact #Gets its correct position after it moves relative to its speed#
                self.rect.center = (self.x, self.y) #Update its positions#

        return False #If not in range to drag to you, return false. this causes the coin to remain still.


    def draw(self, surface):
        surface.blit(self.image, self.rect) #Draw the coin.#




    