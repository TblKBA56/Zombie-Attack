from config import *

class ShopButton:
    def __init__(self, player, x, y, weapon_index, cost):
        self.x, self.y, self.weapon, self.animation, self.w, self.h, self.cost, self.player_obj = (
            x, y, weapon_index, 0, 400, 80, cost, player)
        if self.player_obj.has_weapon(weapon_index):
            self.weapon *= -1

    def in_focus(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.x + self.w > mouse_x > self.x and self.y + self.h > mouse_y > self.y

    def buy_weapon(self):
        if self.player_obj.get_money() >= self.cost and not self.in_own():
            self.player_obj.buy(self.cost, self.get_weapon_index())
            self.weapon *= -1
            self.player_obj.select_weapon(self.get_weapon_index())
        elif self.in_own():
            self.player_obj.select_weapon(self.get_weapon_index())

    def in_own(self):
        return self.weapon < 0

    def get_weapon_index(self):
        return self.weapon if self.weapon > 0 else self.weapon * - 1

    def draw(self):
        anim_mod = self.animation // 30
        equipped = 20 if self.get_weapon_index() == self.player_obj.get_equip() else 0
        if self.weapon > 0:
            color = (170 + anim_mod, 60 + anim_mod, 60 + anim_mod)
        else:
            color = (30 + anim_mod + equipped, 30 + anim_mod + equipped, 30 + anim_mod + equipped)
        pygame.draw.rect(screen, color, (self.x - anim_mod - equipped, self.y - anim_mod, self.w + anim_mod * 2,
                                         self.h + anim_mod * 2))

    def update(self):
        if self.in_focus():
            if self.animation < 400:
                self.animation += 2
        else:
            if self.animation > 0:
                self.animation -= 1
        self.draw()
        return [self.cost, self.x, self.y, self.get_weapon_index() == self.player_obj.get_equip()]
