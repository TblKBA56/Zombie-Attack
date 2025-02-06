from config import *

class Modify:
    fast_spawn = load_image('fast_spawn.png')

    def __init__(self, img_index, x, y):
        self.x, self.y = x, y
        if img_index == 0:
            self.image = Modify.fast_spawn
        self.rect = self.image.get_rect()
        self.rect.move(x, y)
        self.rect.x, self.rect.y = self.x, self.y

    def draw(self):
        screen.blit(self.image, self.rect)
