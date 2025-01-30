import pygame
from random import randint, choice


pygame.init()
pygame.font.init()
WIDTH = 600
HEIGHT = 900
FPS = 60
BASE_HEALTH = 10
GAME_STATE = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Hell Game")
clock = pygame.time.Clock()


def load_image(path):
    return pygame.image.load(path).convert_alpha()


class Player:
    player_img = load_image("player.png")

    def __init__(self):
        self.image = Player.player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.damage = 25
        self.cooldown_time = 15
        self.cooldown = 0
        self.income_multiple = 1
        self.money = 0
        self.all_income_moneys = 0

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_damage(self):
        return self.damage

    def get_money(self):
        return self.money

    def get_score(self):
        return self.all_income_moneys

    def do_shoot(self):
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_time
            return True
        return False

    def kill(self, cost):
        self.all_income_moneys += self.income_multiple * cost
        self.money += self.income_multiple * cost

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        mouse_pos = pygame.mouse.get_pos()
        target_x = mouse_pos[0]

        if target_x < 0:
            target_x = 0
        elif target_x > WIDTH:
            target_x = WIDTH

        self.rect.x += (target_x - self.rect.x) * 0.1
        self.rect.centerx = min(max(self.rect.centerx, 0), WIDTH)

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


class ParallaxRect:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.rect = pygame.rect.Rect(x, y, 400 * z, 800 * z)
        self.color = (int(255 * z // 1), 40, 40)
        self.speed = 20 * z
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


class Enemy:
    enemy_basic_img = load_image("enemy_basic.png")
    enemy_fast_img = load_image("enemy_fast.png")
    enemy_strong_img = load_image("enemy_strong.png")

    def __init__(self, x, y, enemy_type='basic'):
        if enemy_type == 'basic':
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
        self.x = x
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

    def shoot(self, damage):
        self.health -= damage
        if self.health <= 0:
            return self.cost
        return False

    def update(self):
        self.rect.y += self.speed
        self.rect.x = self.x
        if self.rect.bottom > HEIGHT - 32:
            global BASE_HEALTH
            if self.rect.centerx + 32 > player.rect.centerx > self.rect.centerx - 32:
                BASE_HEALTH = -1
            else:
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

    def __init__(self, x, y):
        self.image = Bullet.bullet_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10
        if self.rect.top < 0:
            return False
        return True

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


def reset():
    global enemies, bullets, parallax, base, player, BASE_HEALTH, GAME_STATE
    BASE_HEALTH = 10
    GAME_STATE = 0
    enemies.clear()
    bullets.clear()
    parallax.clear()
    base.clear()
    player.__init__()
    enemies = []
    bullets = []
    parallax = [ParallaxRect(randint(-60, WIDTH), randint(-60, HEIGHT), 1 / x) for x in range(120, 1, -2)]
    parallax.extend([ParallaxRect(WIDTH // 2, HEIGHT // 2, 1 / x) for x in range(10, 1, -2)])
    parallax.sort()
    base = [PlayerBase(x * 32, HEIGHT - 16) for x in range(WIDTH // 32 + 2)]


player = Player()
enemies = []
bullets = []
parallax = [ParallaxRect(randint(-60, WIDTH), randint(-60, HEIGHT), 1 / x) for x in range(120, 1, -2)]
parallax.extend([ParallaxRect(WIDTH // 2, HEIGHT // 2, 1 / x) for x in range(10, 1, -2)])
parallax.sort()
base = [PlayerBase(x * 32, HEIGHT - 16) for x in range(WIDTH // 32 + 2)]
from_color = [64, 16, 16]
to_color = [0, 0, 0]
dynamic_colors = [from_color[i] - to_color[i] for i in range(3)]
create_enemy_chance = 500


running = True
while running:
    if GAME_STATE == 0:
        screen.fill((0, 0, 0))
        for y in range(HEIGHT):
            color = [0 + int((dynamic_colors[i] / (y / HEIGHT + 1)) // 1) for i in range(3)]
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        font1 = pygame.font.Font(None, 24)
        health = font1.render(f'Жизни базы: {BASE_HEALTH}', True, (128, 128, 128))
        moneys = font1.render(f'Денег: {player.get_money()}', True, (128, 128, 128))
        score = font1.render(f'Очки: {player.get_score()}', True, (128, 128, 128))
        screen.blit(health, (32, 32))
        screen.blit(moneys, (32, 52))
        screen.blit(score, (32, 72))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                if ((event.dict.get('button') and event.dict['button'] == 1) or
                        (event.dict.get('key') and event.dict['key'] == 32)) and player.do_shoot():
                        x, y = player.get_coords()
                        bullets.append(Bullet(x + 28, y + 1))

        create_enemy = randint(0, create_enemy_chance)
        if create_enemy == create_enemy_chance:
            create_enemy_chance = 500
            enemy_type = choice(["basic", "basic", "basic", "fast", "strong"])
            enemies.append(Enemy(randint(32, WIDTH - 32), -32, enemy_type))
        else:
            create_enemy_chance -= 1

        player.update()
        for enemy in enemies.copy():
            if not enemy.update():
                enemies.remove(enemy)
            else:
                enemy.draw()

        for bullet in bullets.copy():
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    is_dead = enemy.shoot(player.get_damage())
                    if is_dead:
                        player.kill(is_dead)
                        enemies.remove(enemy)
                    break

        player.draw()
        for bullet in bullets:
            bullet.update()
            bullet.draw()

        for wall in base:
            wall.draw()
        if BASE_HEALTH <= 0:
            GAME_STATE = 1

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
        lose_text = font1.render('База разрушена.', True, (255, 80, 80))
        hint_text = font2.render('WASD для 3D эффекта. (Параллакс)', True, (40, 40, 40))
        hint_text2 = font2.render('Enter для новой игры.', True, (40, 40, 40))
        screen.blit(lose_text, (100, 200))
        screen.blit(hint_text, (32, 32))
        screen.blit(hint_text2, (32, 48))
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
