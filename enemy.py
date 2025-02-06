from particle import Particle
from config import *

class Enemy:
    enemy_basic_img = load_image("enemy_basic.png")
    enemy_fast_img = load_image("enemy_fast.png")
    enemy_strong_img = load_image("enemy_strong.png")

    def __init__(self, x, y, enemy_type='basic'):
        self.enemy_type = enemy_type
        if enemy_type == 'basic' or enemy_type == 'smart':
            self.orig_image = Enemy.enemy_basic_img
            self.health = 100
            self.damage = 1
            self.cost = 2
            self.speed = 2 + randint(-1, 1)
        elif enemy_type == 'fast':
            self.orig_image = Enemy.enemy_fast_img
            self.health = 30
            self.damage = 1
            self.cost = 3
            self.speed = 3 + randint(-1, 2)
        elif enemy_type == 'strong':
            self.orig_image = Enemy.enemy_strong_img
            self.health = 250
            self.damage = 2
            self.cost = 5
            self.speed = 1 + randint(0, 1)
        self.health, self.speed, self.cost = (self.health * DIFFICULT, self.speed * DIFFICULT / FPS * 60,
                                              int(self.cost * DIFFICULT // 1))
        self.image = self.orig_image
        self.daze = 0
        self.x = x
        self.y = y
        self.step = 0
        self.max_step = randint(40, 45)
        self.move_diagonal = 0
        self.rect = self.image.get_rect()
        self.rect.move(x, y)
        self.rect.x, self.rect.y = x, y

    def shoot(self, damage):
        self.health -= damage
        self.daze = 30 * FPS // 60
        if self.health <= 0:
            return self.cost
        return False

    def get_type(self):
        return self.enemy_type

    def coords(self):
        return self.rect.x, self.rect.y

    def update(self):
        slow = 1
        from_x, from_y = self.coords()
        self.x, self.y = self.coords()

        if self.step % 2 == 0:
            self.step += 2 / slow
        elif self.step % 2 == 1:
            self.step -= 2 / slow
        if self.step >= self.max_step / slow:
            self.step -= 3 / slow
        elif self.step <= -self.max_step / slow:
            self.step += 3 / slow

        if self.daze > 0:
            slow = 1.7
            if self.health >= 30:
                self.daze -= 1
            else:
                bleeding = randint(0, 500 * FPS // 60)
                if bleeding == 500 * FPS // 60:
                    self.health -= 3
                    new_particle(Particle(self.x + 16, self.y + 16, 90 + randint(-6, 6), 3, 5, 80, 5))

        if self.enemy_type == 'smart' and randint(1, 50) == 50 and self.move_diagonal == 0:
            if WIDTH - 48 > self.x > 48:
                self.move_diagonal = randint(-2, 2)
            elif self.x < 48:
                self.move_diagonal = randint(0, 2)
            elif self.x > WIDTH - 48:
                self.move_diagonal = randint(-2, 2)
        elif ((self.enemy_type == 'smart' and self.move_diagonal != 0 and randint(1, 80) == 80)
              or (self.move_diagonal < 0 and self.x < 48) or (self.move_diagonal > 0 and self.x > WIDTH - 32)):
            self.move_diagonal = 0
        self.x += round(self.move_diagonal * (self.speed / slow / 1.5), 2)
        self.y += round(self.speed / slow, 2)
        if from_y - self.y <= from_y - 0.1:
            self.y += 1
        self.rect.y = self.y
        self.rect.x = self.x
        self.image = pygame.transform.rotate(self.orig_image, 90 - int(atan2(self.y - from_y, self.x -
                                                                             from_x + self.step / 120) * (180 / pi) // 1))
        if self.rect.bottom > HEIGHT - 32:
            base_damage(self.damage)
            return False
        return True

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
