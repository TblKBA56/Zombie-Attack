from config import *

class Particle:
    def __init__(self, x, y, direction, min_radius=2, max_radius=4, lifetime: int = True,
                 speed: int = True, color=pygame.Color(100, 10, 10)):
        self.screen = screen
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

    def draw_shadow(self):
        circle_x, circle_y = self.center_coords
        pygame.draw.circle(screen, (0, 0, 0, 250), (circle_x - self.lifetime // 10, circle_y + self.lifetime // 10), self.radius)

    def draw(self):
        pygame.draw.circle(screen, self.color, self.center_coords, self.radius)
