from config import *

class Bullet:
    bullet_img = load_image('bullet.png')

    def __init__(self, player, x, y, accuracy, speed=20, check_type=True):
        self.speed = speed * BULLET_SPEED_UPDATE / FPS * 60
        self.type = player.get_equip() if check_type else 0
        self.x, self.y = x, y
        self.direction = 90 + randint(-accuracy * 20, accuracy * 20) / 20
        self.image = pygame.transform.rotate(Bullet.bullet_img, 90 - self.direction)
        self.rect = self.image.get_rect(center=(x, y))

    def get_direction(self):
        return self.direction

    def get_type(self):
        return True if self.type == 3 else False

    def copy(self):
        return Bullet(self.x, self.y - 40, 2.5, int(self.speed - 3 // 1), False)

    def update(self):
        self.x, self.y = (self.x + self.speed * -cos(self.direction / 180 * pi),
                          self.y + self.speed * -sin(self.direction / 180 * pi))
        self.rect.y = self.y
        self.rect.x = self.x
        if self.rect.y < -32 or self.rect.y > HEIGHT or self.rect.x < -32 or self.rect.x > WIDTH:
            return False
        return True

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
