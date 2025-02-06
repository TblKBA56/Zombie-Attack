import pygame

import config
from config import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from shop_button import ShopButton
from base_health import BaseHealth
from decay import Decay
from modify import Modify
from parallax_rect import ParallaxRect
from particle import Particle
from player_base import PlayerBase


def reset():
    global enemies, bullets, parallax, base, player, types_of_zombie, game_modifies, create_enemy_chance, particles,\
        buttons, DIFFICULT, BASE_HEALTH, GAME_STATE
    set_base_health(10)
    set_game_state(0)
    set_difficult(1)
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
    buttons = [ShopButton(player, 100, 100 * (i + 1), i, weapons_cost[i]) for i in range(6)]
    game_modifies = [0, 0, 0]
    create_enemy_chance = 500
    types_of_zombie = ["basic", "basic", "basic", "fast", "strong"]
    parallax = [ParallaxRect(randint(-60, WIDTH), randint(-60, HEIGHT), 1 / x) for x in range(120, 1, -2)]
    parallax.extend([ParallaxRect(WIDTH // 2, HEIGHT // 2, 1 / x) for x in range(10, 1, -2)])
    parallax.sort()
    base = [PlayerBase(x * 32, HEIGHT - 16) for x in range(WIDTH // 32 + 2)]


pygame.display.set_caption("Zombie Attack")
clock = pygame.time.Clock()

player = Player()


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
health_draw_obj = BaseHealth(24, 24)
fast_spawn_mode = Modify(0, 24, 256)
game_modifies = [0, 0, 0]
weapons_cost = [0, 50, 120, 300, 200, 400]
shoots = False
start_red, start_green, start_blue = 1500, 0, 0
buttons = [ShopButton(player, 100, 100 * (i + 1), i, weapons_cost[i]) for i in range(6)]
font1 = pygame.font.Font(None, 24)
font2 = pygame.font.Font(None, 72)


running = True
while running:
    GAME_STATE = config.GAME_STATE
    DIFFICULT = config.DIFFICULT
    BASE_HEALTH = config.BASE_HEALTH
    BEST_SCORE = config.BEST_SCORE
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
                        bullets.extend([Bullet(player, x_pl + 22, y_pl + 1, player.get_accuracy(),
                                               int(20 // (1 + randint(1, 3) / 4))) for _ in range(count_of_bullets)])
                    else:
                        bullets.append(Bullet(player, x_pl + 22, y_pl + 1, player.get_accuracy()))
                elif event.dict.get('key') and event.dict['key'] == 98 and player.in_shop():
                    set_game_state(2)
                elif event.dict.get('key') and event.dict['key'] == pygame.K_ESCAPE:
                    set_game_state(4)
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                if ((event.dict.get('button') and event.dict['button'] == 1) or
                    (event.dict.get('key') and event.dict['key'] == 32)):
                    shoots = False
        if shoots and player.do_shoot() and player.get_equip() not in [0, 3, 4]:
            bullets.append(Bullet(player, x_pl + 22, y_pl + 1, player.get_accuracy()))
        if player.get_equip() == 3:
            pl_x, pl_y = player.get_coords()
            color_line = pygame.Color(80, 0, 0, 50)
            pygame.draw.line(screen, color_line, (pl_x + 28, pl_y), (pl_x + 28, - HEIGHT))

        for decay in decays:
            decay.draw()

        for particle in particles:
            particle.draw_shadow()

        for particle in config.particles:
            particle.draw_shadow()

        for particle in particles:
            if particle.update():
                particles.remove(particle)

        for particle in config.particles:
            if particle.update():
                particles.remove(particle)

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
                set_base_health(-140000)

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
            set_game_state(1)
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
        set_difficult(DIFFICULT)
        pygame.display.flip()
        clock.tick(FPS)
    elif GAME_STATE == 1:
        screen.fill((0, 0, 0))
        if player.get_score() > BEST_SCORE:
            new_record(player.get_score())
            BEST_SCORE = player.get_score()
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
        pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.dict.get('key'):
                key = event.dict['key']
                if key == 27:
                    set_game_state(0)
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
    elif GAME_STATE == 3:
        screen.fill((start_red // 10, start_green // 10, start_blue // 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                set_game_state(0)
        if start_blue == 0 and start_red > 0 and start_green < 1800:
            start_red -= 1
            start_green += 1
        elif start_blue < 1800 and start_red == 0 and start_green > 0:
            start_green -= 1
            start_blue += 1
        elif start_blue > 0 and start_red < 1800 and start_green == 0:
            start_blue -= 1
            start_red += 1
        start_white = font2.render('Нажмите чтобы начать', True, (255, 255, 255))
        start_shadow = font2.render('Нажмите чтобы начать', True, (0, 0, 0))
        best_score = font1.render(f'Рекордный счёт: {BEST_SCORE}', True, (255, 255, 255))
        screen.blit(start_shadow, (20, 460))
        screen.blit(start_white, (25, 450))
        screen.blit(best_score, (25, 520))
        pygame.display.flip()
    elif GAME_STATE == 4:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.dict.get('key') and
                                             event.dict['key'] == 13):
                running = False
            elif event.type == pygame.KEYDOWN and event.dict.get('key') and event.dict['key'] == pygame.K_ESCAPE:
                set_game_state(0)
        exit_text = font1.render('Выйти? ESC - отмена. ENTER - выход.', True, (255, 255, 255))
        screen.blit(exit_text, (75, 450))
        pygame.display.flip()


pygame.quit()