from config import *

class Player:
    player_img = load_image("player.png")

    def __init__(self):
        self.image = Player.player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        (self.damage, self.cooldown_time, self.weapon_accuracy, self.cooldown, self.money, self.all_income_moneys,
         self.income_multiple) = 0, 0, 0, 0, 0, 0, 1
        self.weapons = [True, False, False, False, False, False]
        self.equip = 0
        self.select_weapon(self.equip)

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_damage(self):
        return self.damage # * DAMAGE_UPDATE

    def get_money(self):
        return self.money

    def get_score(self):
        return self.all_income_moneys

    def get_equip(self):
        return self.equip

    def get_accuracy(self):
        return self.weapon_accuracy

    def has_weapon(self, index):
        return self.weapons[index]

    def select_weapon(self, index):
        if self.has_weapon(index):
            self.damage, self.cooldown_time, self.weapon_accuracy = weapons[list(weapons.keys())[index]]
            self.equip = index

    def buy(self, cost, index):
        self.money -= cost
        self.weapons[index] = True

    def in_shop(self) -> bool:
        x, y = self.get_coords()
        return x > WIDTH - 200 and y > HEIGHT - 200

    def do_shoot(self):
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_time # - RECOIL_UPDATE
            return True
        return False

    def kill(self, cost):
        self.all_income_moneys += self.income_multiple * cost
        self.money += self.income_multiple * cost

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        mouse_pos = pygame.mouse.get_pos()
        target_x, target_y = mouse_pos[0] - 16, mouse_pos[1] - 16

        if target_x < 0:
            target_x = 0
        elif target_x > WIDTH - 32:
            target_x = WIDTH - 32
        if target_y > HEIGHT - 48:
            target_y = HEIGHT - 48
        elif target_y < HEIGHT - 360:
            target_y = HEIGHT - 360
        self.rect.x += (target_x - self.rect.x) / FPS * 60 * MOVEMENT_UPDATE
        self.rect.y += (target_y - self.rect.y) / FPS * 60 * MOVEMENT_UPDATE
        self.rect.centerx = min(max(self.rect.centerx, 0), WIDTH)
        self.rect.centery = min(max(self.rect.centery, 0), HEIGHT)

    def draw(self):
        screen.blit(self.image, self.rect.topleft)