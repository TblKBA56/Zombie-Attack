from config import *

class PlayerBase:
    base_img = load_image('base.png')

    def __init__(self, x, y):
        self.image = PlayerBase.base_img
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
