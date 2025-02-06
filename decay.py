from config import *

class Decay:
    decays_imgs = [load_image('zombie_decay1.png'), load_image('zombie_decay2.png'), load_image('zombie_decay3.png'),
                   load_image('zombie_decay4.png')]

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = choice(Decay.decays_imgs)
        self.rect = self.image.get_rect()
        self.rect.move(x, y)
        self.rect.x, self.rect.y = self.x, self.y

    def __lt__(self, other):
        if isinstance(other, Decay):
            return Decay.decays_imgs.index(self.image) < Decay.decays_imgs.index(other.image)

    def draw(self):
        screen.blit(self.image, self.rect)
