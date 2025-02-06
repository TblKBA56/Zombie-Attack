from config import *

class BaseHealth:
    shield = load_image('shield_icon.png')

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = BaseHealth.shield
        self.rect = self.image.get_rect()
        self.rect.move(x, y)
        self.rect.x, self.rect.y = self.x, self.y

    def draw(self, i):
        x, y, w, h = self.rect
        screen.blit(self.image, (x + i * 42, y, w, h))
