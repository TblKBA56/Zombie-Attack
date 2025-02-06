from config import *

class ParallaxRect:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.rect = pygame.rect.Rect(x, y, 400 * z, 800 * z)
        self.color = (int(255 * z // 1), 40, 40)
        self.speed = 20 * z / FPS * 60
        self.moving = 0

    def __lt__(self, other):
        if isinstance(other, ParallaxRect):
            return self.z < other.z
        return False

    def move_left(self):
        self.x += self.speed
        self.rect.x = self.x

    def move_right(self):
        self.x -= self.speed
        self.rect.x = self.x

    def move_up(self):
        self.y += self.speed
        self.rect.y = self.y

    def move_down(self):
        self.y -= self.speed
        self.rect.y = self.y

    def move(self, key_code):
        {119: self.move_up, 97: self.move_left, 115: self.move_down, 100: self.move_right}[key_code]()

    def stop_move(self, key_code):
        if self.moving == key_code:
            self.moving = 0

    def do_move(self, key_code):
        self.moving = key_code

    def update(self):
        if self.moving != 0:
            self.move(self.moving)

    def draw_rect(self):
        return self.color, self.rect
