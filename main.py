import pygame
from random import randint, choice
from math import cos, sin, pi, atan2
# python 3.11

pygame.init()
pygame.font.init()
WIDTH = 600
HEIGHT = 900
FPS = 90
BASE_HEALTH = 10
GAME_STATE = 0
DIFFICULT = 1
MOVEMENT_UPDATE = 0.05
BULLET_SPEED_UPDATE = 1
ACCURACY_UPDATE = 1
RECOIL_UPDATE = 0
DAMAGE_UPDATE = 1
weapons = {'pistol': [25, 15, 1], 'machine pistol': [20, 12, 2.5], 'assault rifle': [40, 12, 1.4],
           'sniper rifle': [120, 60, 0.2], 'shotgun': [25, 55, 2], 'machine gun': [30, 5, 3.5]}
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Attack")
clock = pygame.time.Clock()


def load_image(path):
    return pygame.image.load(path).convert_alpha()


class Player:
    player_img = load_image("player.png")

    def __init__(self):
        self.image = Player.player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        (self.damage, self.cooldown_time, self.weapon_accuracy, self.cooldown, self.money, self.all_income_moneys,
         self.income_multiple) = 0, 0, 0, 0, 1000, 0, 1
        self.weapons = [True, False, False, False, False, False]
        self.equip = 0
        self.select_weapon(self.equip)

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_damage(self):
        return self.damage * DAMAGE_UPDATE

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
        global weapons
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
            self.cooldown = self.cooldown_time - RECOIL_UPDATE
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
        self.rect.x += (target_x - self.rect.x) * MOVEMENT_UPDATE / FPS * 60
        self.rect.y += (target_y - self.rect.y) * MOVEMENT_UPDATE / FPS * 60
        self.rect.centerx = min(max(self.rect.centerx, 0), WIDTH)
        self.rect.centery = min(max(self.rect.centery, 0), HEIGHT)

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


class ShopButton:
    def __init__(self, x, y, weapon_index, cost):
        self.x, self.y, self.weapon, self.animation, self.w, self.h, self.cost = x, y, weapon_index, 0, 400, 80, cost
        if player.has_weapon(weapon_index):
            self.weapon *= -1

    def in_focus(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.x + self.w > mouse_x > self.x and self.y + self.h > mouse_y > self.y

    def buy_weapon(self):
        if player.get_money() >= self.cost and not self.in_own():
            player.buy(self.cost, self.get_weapon_index())
            self.weapon *= -1
            player.select_weapon(self.get_weapon_index())
        elif self.in_own():
            player.select_weapon(self.get_weapon_index())

    def in_own(self):
        return self.weapon < 0

    def get_weapon_index(self):
        return self.weapon if self.weapon > 0 else self.weapon * - 1

    def draw(self):
        anim_mod = self.animation // 30
        equipped = 20 if self.get_weapon_index() == player.get_equip() else 0
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
        return [self.cost, self.x, self.y, self.get_weapon_index() == player.get_equip()]


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


class Particle:
    def __init__(self, x, y, direction, min_radius=2, max_radius=4, lifetime: int = True,
                 speed: int = True, color=pygame.Color(100, 10, 10)):
        self.direction = direction
        if isinstance(speed, bool):
            speed = randint(0, 30)
        if isinstance(lifetime, bool):
            lifetime = 40 + randint(1, 30)
        self.speed = speed / 17 / FPS * 60
        self.color = color
        self.center_coords = x, y
        self.radius = randint(min_radius, max_radius)
        self.lifetime = lifetime * FPS // 60

    def update(self):
        x, y = self.center_coords
        self.center_coords = (x + self.speed * -cos(self.direction / 180 * pi),
                              y + self.speed * -sin(self.direction / 180 * pi))
        self.lifetime -= 1
        self.draw()
        if self.lifetime <= 0:
            return True

    def draw(self):
        pygame.draw.circle(screen, self.color, self.center_coords, self.radius)


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
                    global particles
                    particles.append(Particle(self.x + 16, self.y + 16, 90 + randint(-6, 6), 3, 5, 80, 5))

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
            global BASE_HEALTH
            BASE_HEALTH -= self.damage
            return False
        return True

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


class PlayerBase:
    base_img = load_image('base.png')

    def __init__(self, x, y):
        self.image = PlayerBase.base_img
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


class Bullet:
    bullet_img = load_image('bullet.png')

    def __init__(self, x, y, accuracy, speed=20, check_type=True):
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


def reset():
    global enemies, bullets, parallax, base, player, types_of_zombie, game_modifies, create_enemy_chance, particles,\
        buttons, DIFFICULT, BASE_HEALTH, GAME_STATE
    BASE_HEALTH = 10
    GAME_STATE = 0
    DIFFICULT = 1
    particles.clear()
    enemies.clear()
    bullets.clear()
    parallax.clear()
    decays.clear()
    base.clear()
    buttons.clear()
    types_of_zombie.clear()
    player.__init__()
    enemies = []
    bullets = []
    particles = []
    buttons = [ShopButton(100, 100 * (i + 1), i, weapons_cost[i]) for i in range(6)]
    game_modifies = [0, 0, 0]
    create_enemy_chance = 500
    types_of_zombie = ["basic", "basic", "basic", "fast", "strong"]
    parallax = [ParallaxRect(randint(-60, WIDTH), randint(-60, HEIGHT), 1 / x) for x in range(120, 1, -2)]
    parallax.extend([ParallaxRect(WIDTH // 2, HEIGHT // 2, 1 / x) for x in range(10, 1, -2)])
    parallax.sort()
    base = [PlayerBase(x * 32, HEIGHT - 16) for x in range(WIDTH // 32 + 2)]


player = Player()
from_color = [64, 16, 16]
to_color = [0, 0, 0]
dynamic_colors = [from_color[i] - to_color[i] for i in range(3)]
health_draw_obj = BaseHealth(24, 24)
fast_spawn_mode = Modify(0, 24, 256)

enemies = []
bullets = []
decays = []
particles = []
types_of_zombie = ["basic", "basic", "basic", "fast", "strong"]
parallax = [ParallaxRect(randint(-60, WIDTH), randint(-60, HEIGHT), 1 / x) for x in range(120, 1, -2)]
parallax.extend([ParallaxRect(WIDTH // 2, HEIGHT // 2, 1 / x) for x in range(10, 1, -2)])
parallax.sort()
base = [PlayerBase(x * 32, HEIGHT - 16) for x in range(WIDTH // 32 + 2)]
create_enemy_chance = 500
game_modifies = [0, 0, 0]
weapons_cost = [0, 50, 120, 300, 200, 400]
shoots = False
buttons = [ShopButton(100, 100 * (i + 1), i, weapons_cost[i]) for i in range(6)]
font1 = pygame.font.Font(None, 24)
font2 = pygame.font.Font(None, 72)


running = True
while running:
    if GAME_STATE == 0:
        screen.fill((0, 0, 0))
        for y in range(HEIGHT):
            color = [0 + int((dynamic_colors[i] / (y / HEIGHT + 1)) // 1) for i in range(3)]
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        x_pl, y_pl = player.get_coords()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                if ((event.dict.get('button') and event.dict['button'] == 1) or
                    (event.dict.get('key') and event.dict['key'] == 32)) and player.do_shoot():
                    if player.get_equip() not in [0, 3, 4]:
                        shoots = True
                    count_of_bullets = 1
                    if player.get_equip() == 4:
                        count_of_bullets = 5
                        bullets.extend([Bullet(x_pl + 22, y_pl + 1, player.get_accuracy(),
                                               int(20 // (1 + randint(1, 3) / 4))) for _ in range(count_of_bullets)])
                    else:
                        bullets.append(Bullet(x_pl + 22, y_pl + 1, player.get_accuracy()))
                elif event.dict.get('key') and event.dict['key'] == 98 and player.in_shop():
                    GAME_STATE = 2
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                if ((event.dict.get('button') and event.dict['button'] == 1) or
                    (event.dict.get('key') and event.dict['key'] == 32)):
                    shoots = False
        if shoots and player.do_shoot() and player.get_equip() not in [0, 3, 4]:
            bullets.append(Bullet(x_pl + 22, y_pl + 1, player.get_accuracy()))
        if player.get_equip() == 3:
            pl_x, pl_y = player.get_coords()
            color_line = pygame.Color(80, 0, 0, 50)
            pygame.draw.line(screen, color_line, (pl_x + 28, pl_y), (pl_x + 28, - HEIGHT))

        for particle in particles:
            if particle.update():
                particles.remove(particle)

        for decay in decays:
            decay.draw()

        if game_modifies[0] > 0:
            fast_spawn_mode.draw()
            if create_enemy_chance > 1:
                create_enemy_chance = (create_enemy_chance - 1.5 * DIFFICULT) // 1
        if create_enemy_chance <= 1:
            create_enemy_chance = 1
        create_enemy = randint(0, int(create_enemy_chance // 1))
        if create_enemy == create_enemy_chance // DIFFICULT + 1:
            create_enemy_chance = 500 * FPS / 60
            enemy_type = choice(types_of_zombie)
            enemies.append(Enemy(randint(48, WIDTH - 48), -32, enemy_type))
        elif create_enemy_chance > 1:
            create_enemy_chance -= 2.5 * DIFFICULT

        player.update()

        for enemy in enemies.copy():
            if not enemy.update():
                enemies.remove(enemy)
            else:
                enemy.draw()
            if enemy.rect.colliderect(player.rect):
                BASE_HEALTH = -140000

        for bullet in bullets.copy():
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    x_enem, y_enem = enemy.coords()
                    if bullet.get_type():
                        bullets.append(bullet.copy())
                        particles.extend([Particle(x_enem + 16, y_enem + 16, bullet.get_direction() +
                                                   randint(-5, 5), 2, 4) for _ in range(3)])
                    else:
                        particles.append(Particle(x_enem + 16, y_enem + 16, bullet.get_direction() + randint(-5, 5), 1, 3))
                    bullets.remove(bullet)
                    is_dead = enemy.shoot(player.get_damage())
                    if is_dead:
                        more_particles = 4 if enemy.enemy_type == 'strong' else 0
                        player.kill(is_dead)
                        particles.extend([Particle(x_enem + 16, y_enem + 16,
                                                   bullet.get_direction() + randint(-20, 20), 4, 7)
                                          for _ in range(2 + more_particles)])
                        particles.extend([Particle(x_enem + 16, y_enem + 16, bullet.get_direction() + randint(-20, 20))
                                          for _ in range(5 + more_particles)])
                        if len(decays) > 50:
                            decays.remove(choice(decays))
                        decays.append(Decay(x_enem, y_enem))
                        decays.sort()
                        enemies.remove(enemy)
                    break

        player.draw()
        for bullet in bullets:
            if bullet.update():
                bullet.draw()
            else:
                bullets.remove(bullet)

        for wall in base:
            wall.draw()
        if BASE_HEALTH <= 0:
            GAME_STATE = 1
        for i in range(0, BASE_HEALTH):
            health_draw_obj.draw(i)

        if randint(0, 10000 * FPS // 60) == 10000 * FPS // 60:
            game_modifies[0] = 240 * FPS // 60
        elif randint(0, 10000 * FPS // 60) == 10000 * FPS // 60:
            game_modifies[1] = 240 * FPS // 60
        elif randint(0, 10000 * FPS // 60) == 10000 * FPS // 60:
            game_modifies[2] = 240 * FPS // 60
        if game_modifies[0] > 0:
            game_modifies[0] -= 1
        if game_modifies[1] > 0:
            game_modifies[1] -= 1
        if game_modifies[2] > 0:
            game_modifies[2] -= 1

        if player.in_shop():
            font3 = pygame.font.Font(None, 16)
            shop_hint = font3.render('Магазин [b]', True, (120, 120, 10))
            screen.blit(shop_hint, (WIDTH - 90, WIDTH + 200))

        moneys = font1.render(f'Денег: {player.get_money()}', True, (128, 128, 128))
        score = font1.render(f'Очки: {player.get_score()}', True, (128, 128, 128))
        screen.blit(moneys, (32, 72))
        screen.blit(score, (32, 92))

        DIFFICULT += 0.000015 / FPS * 60
        if 1.019 < DIFFICULT < 1.02:
            types_of_zombie.append("smart")
            DIFFICULT = 1.021
        pygame.display.flip()
        clock.tick(FPS)
    elif GAME_STATE == 1:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.dict.get('key'):
                key = event.dict['key']
                if key == 13:
                    reset()
                if key in [119, 97, 115, 100]:
                    for rect in parallax:
                        rect.do_move(key)
            elif event.type == pygame.KEYUP and event.dict.get('key'):
                key = event.dict['key']
                if key in [119, 97, 115, 100]:
                    for rect in parallax:
                        rect.stop_move(key)
        for rect in parallax:
            rect.update()
            rect_color, rect_obj = rect.draw_rect()
            pygame.draw.rect(screen, rect_color, rect_obj)
        if BASE_HEALTH == -140000:
            lose_text = 'Защитник погиб'
        else:
            lose_text = 'База разрушена'
        lose_text = font2.render(lose_text, True, (255, 80, 80))
        hint_text = font1.render('WASD для 3D эффекта (Параллакс)', True, (40, 40, 40))
        hint_text2 = font1.render('Enter для новой игры', True, (40, 40, 40))
        screen.blit(lose_text, (100, 200))
        screen.blit(hint_text, (32, 32))
        screen.blit(hint_text2, (32, 48))
        pygame.display.flip()
        clock.tick(FPS)
    elif GAME_STATE == 2:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.dict.get('key'):
                key = event.dict['key']
                if key == 27:
                    GAME_STATE = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.dict.get('button') and event.dict['button'] == 1:
                for button in buttons:
                    if button.in_focus():
                        button.buy_weapon()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            data = button.update()
            equip_str = ' *Экипировано*' if data[3] else ''
            weapon_name = ['Пистолет', 'Пистолет-пулемёт', 'Автомат', 'Снайперская винтовка', 'Дробовик', 'Пулемёт']
            weapon_name = font1.render(weapon_name[button.get_weapon_index()], True, (255, 255, 255))
            weapon_cost = font1.render(f'Стоимость: {data[0]}${equip_str}', True, (255, 255, 255))
            screen.blit(weapon_name, (data[1] + 10, data[2] + 10))
            screen.blit(weapon_cost, (data[1] + 10, data[2] + 40))
        moneys = font1.render(f'Денег: {player.get_money()}', True, (128, 128, 128))
        score = font1.render(f'Очки: {player.get_score()}', True, (128, 128, 128))
        screen.blit(moneys, (32, 72))
        screen.blit(score, (32, 92))
        pygame.display.flip()


pygame.quit()
