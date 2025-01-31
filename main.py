import pygame
from random import randint, choice
from math import cos, sin, pi
# python 3.11

pygame.init()
pygame.font.init()
WIDTH = 600
HEIGHT = 900
FPS = 60
BASE_HEALTH = 10
GAME_STATE = 0
DIFFICULT = 1
MOVEMENT_UPDATE = 0.05
BULLET_SPEED_UPDATE = 1
ACCURACY_UPDATE = 1
RECOIL_UPDATE = 0
DAMAGE_UPDATE = 1
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
        self.damage = 25
        self.cooldown_time = 15 * FPS // 60
        self.cooldown = 0
        self.income_multiple = 1
        self.money = 0
        self.all_income_moneys = 0

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_damage(self):
        return self.damage * DAMAGE_UPDATE

    def get_money(self):
        return self.money

    def get_score(self):
        return self.all_income_moneys

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
    def __init__(self, x, y, direction, min_radius=2, max_radius=4, color=pygame.Color(100, 10, 10)):
        self.direction = direction
        self.speed = randint(0, 30) / 17 / FPS * 60
        self.color = color
        self.center_coords = x, y
        self.radius = randint(min_radius, max_radius)
        self.lifetime = 40 + randint(1, 30) * FPS // 60

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
            self.image = Enemy.enemy_basic_img
            self.health = 100
            self.damage = 1
            self.cost = 2
            self.speed = 2 + randint(-1, 1)
        elif enemy_type == 'fast':
            self.image = Enemy.enemy_fast_img
            self.health = 30
            self.damage = 1
            self.cost = 3
            self.speed = 3 + randint(-1, 2)
        elif enemy_type == 'strong':
            self.image = Enemy.enemy_strong_img
            self.health = 250
            self.damage = 2
            self.cost = 5
            self.speed = 1 + randint(0, 1)
        self.health, self.speed, self.cost = (self.health * DIFFICULT, self.speed * DIFFICULT / FPS * 60,
                                              int(self.cost * DIFFICULT // 1))
        self.daze = 0
        self.x = x
        self.y = y
        self.move_diagonal = 0
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

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
        if self.daze > 0:
            slow = 1.7
            if self.health >= 30:
                self.daze -= 1
        self.y += self.speed / slow
        self.rect.y = int(self.y // 1)
        random_diagonal = randint(1, 50)
        if self.enemy_type == 'smart' and random_diagonal == 50 and self.move_diagonal == 0:
            self.move_diagonal = randint(-2, 2)
        elif ((self.enemy_type == 'smart' and self.move_diagonal != 0 and randint(1, 80) == 80)
              or (self.move_diagonal < 0 and self.x < 32) or (self.move_diagonal > 0 and self.x > WIDTH - 32)):
            self.move_diagonal = 0
        self.x += self.move_diagonal * self.speed / slow / 1.3
        self.rect.x = self.x
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

    def __init__(self, x, y, accuracy, speed=20):
        self.image = Bullet.bullet_img
        self.speed = speed * BULLET_SPEED_UPDATE / FPS * 60
        self.direction = 90 + randint(-accuracy, accuracy)
        self.rect = self.image.get_rect(center=(x, y))

    def get_direction(self):
        return self.direction

    def update(self):
        x, y = (self.rect.x + self.speed * -cos(self.direction / 180 * pi),
                self.rect.y + self.speed * -sin(self.direction / 180 * pi))
        self.rect.y = y
        self.rect.x = x
        if self.rect.y < 10 or self.rect.y > HEIGHT or self.rect.x < -32 or self.rect.x > WIDTH:
            return False
        return True

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


def reset():
    global enemies, bullets, parallax, base, player, types_of_zombie, game_modifies, create_enemy_chance, DIFFICULT, \
        BASE_HEALTH, GAME_STATE
    BASE_HEALTH = 10
    GAME_STATE = 0
    DIFFICULT = 1
    enemies.clear()
    bullets.clear()
    parallax.clear()
    decays.clear()
    base.clear()
    types_of_zombie.clear()
    player.__init__()
    enemies = []
    bullets = []
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
                    bullets.append(Bullet(x_pl + 28, y_pl + 1, 1))
                elif event.dict.get('key') and event.dict['key'] == 98 and x_pl > WIDTH - 100 and y_pl > HEIGHT - 100:
                    GAME_STATE = 2

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
            enemies.append(Enemy(randint(32, WIDTH - 32), -32, enemy_type))
        elif create_enemy_chance > 1:
            create_enemy_chance -= 2.5 * DIFFICULT

        player.update()

        for enemy in enemies.copy():
            if not enemy.update():
                enemies.remove(enemy)
            else:
                enemy.draw()
            if enemy.rect.colliderect(player.rect):
                BASE_HEALTH = -1

        for bullet in bullets.copy():
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    x_enem, y_enem = enemy.coords()
                    bullets.remove(bullet)
                    particles.append(Particle(x_enem + 16, y_enem + 16, bullet.get_direction() + randint(-5, 5), 1, 3))
                    is_dead = enemy.shoot(player.get_damage())
                    if is_dead:
                        more_particles = 4 if enemy.enemy_type == 'strong' else 0
                        player.kill(is_dead)
                        particles.extend([Particle(x_enem + 16, y_enem + 16,
                                                   bullet.get_direction() + randint(-20, 20), 4, 7)
                                          for _ in range(2 + more_particles)])
                        particles.extend([Particle(x_enem + 16, y_enem + 16, bullet.get_direction() + randint(-20, 20))
                                          for _ in range(5 + more_particles)])
                        decays.append(Decay(x_enem, y_enem))
                        decays.sort()
                        if len(decays) > 50:
                            decays.remove(decays[0])
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

        if randint(0, 10000 * FPS // 60) == 10000 * FPS / 60:
            game_modifies[0] = 240 / FPS * 60
        elif randint(0, 10000 * FPS // 60) == 10000 * FPS / 60:
            game_modifies[1] = 240 / FPS * 60
        elif randint(0, 10000 * FPS // 60) == 10000 * FPS / 60:
            game_modifies[2] = 240 / FPS * 60
        if game_modifies[0] > 0:
            game_modifies[0] -= 1
        if game_modifies[1] > 0:
            game_modifies[1] -= 1
        if game_modifies[2] > 0:
            game_modifies[2] -= 1

        if x_pl > WIDTH - 100 and y_pl > HEIGHT - 100:
            font3 = pygame.font.Font(None, 16)
            shop_hint = font3.render('Пауза [b]', True, (120, 120, 10))
            screen.blit(shop_hint, (WIDTH - 90, WIDTH + 200))
        font1 = pygame.font.Font(None, 24)
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
        font1 = pygame.font.Font(None, 72)
        font2 = pygame.font.Font(None, 24)
        lose_text = font1.render('База разрушена', True, (255, 80, 80))
        hint_text = font2.render('WASD для 3D эффекта (Параллакс)', True, (40, 40, 40))
        hint_text2 = font2.render('Enter для новой игры', True, (40, 40, 40))
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

pygame.quit()
