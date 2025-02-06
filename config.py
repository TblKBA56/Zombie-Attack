import os
from random import randint, choice
from math import pi, cos, sin, atan2
import pygame

WIDTH = 600
HEIGHT = 900
FPS = 90
BASE_HEALTH = 10
GAME_STATE = 3
DIFFICULT = 1
MOVEMENT_UPDATE = 0.05
BULLET_SPEED_UPDATE = 1
ACCURACY_UPDATE = 1
RECOIL_UPDATE = 0
DAMAGE_UPDATE = 1

particles = []

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

weapons = {
    'pistol': [25, 15, 1],
    'machine pistol': [20, 12, 2.5],
    'assault rifle': [40, 12, 1.4],
    'sniper rifle': [120, 60, 0.2],
    'shotgun': [25, 55, 2],
    'machine gun': [30, 5, 3.5]
}

from_color = [172, 48, 48]
to_color = [64, 16, 16]
dynamic_colors = [from_color[i] - to_color[i] for i in range(3)]


def set_base_health(num):
    global BASE_HEALTH
    BASE_HEALTH = num


def set_game_state(num):
    global GAME_STATE
    GAME_STATE = num


def set_difficult(num):
    global DIFFICULT
    DIFFICULT = num


def new_particle(obj):
    particles.append(obj)


def base_damage(damage):
    global BASE_HEALTH
    BASE_HEALTH -= damage


def load_image(path):
    cur_path = os.getcwd()
    images_dir = os.path.join(cur_path, 'images')
    if os.path.isdir(images_dir):
        return pygame.image.load(os.path.join(images_dir, path)).convert_alpha()
    else:
        parent_path = os.path.dirname(cur_path)
        images_dir = os.path.join(parent_path, 'images')
        if os.path.isdir(images_dir):
            return pygame.image.load(os.path.join(images_dir, path)).convert_alpha()
        else:
            return None


try:
    with open('score.txt', 'r') as file:
        if file.readable():
            BEST_SCORE = int(file.read())
        else:
            BEST_SCORE = 0
        file.close()
except:
    with open('score.txt', 'x') as file:
        file.write('0')
        file.close()
    BEST_SCORE = 0


def new_record(score):
    with open('score.txt', 'w') as file:
        file.write(str(score))
        file.close()