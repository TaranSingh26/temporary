# doesnt move out of bounds(includes boundary check condition in update fucntion of roomba class)

import pygame
import sys
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

class Pathfinder:
    def __init__(self, matrix):
        self.matrix = matrix
        self.grid = Grid(matrix=matrix)
        self.select_surf = pygame.image.load('pics/sct.png').convert_alpha()

        self.path = []

        self.roomba = pygame.sprite.GroupSingle(Roomba(self.empty_path))

    def empty_path(self):
        self.path = []

    def draw_active_cell(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        row = mouse_pos[1] // 32
        col = mouse_pos[0] // 32
        if 0 <= row < len(self.matrix) and 0 <= col < len(self.matrix[0]):
            current_cell_value = self.matrix[row][col]
            if current_cell_value == 1:
                rect = pygame.Rect((col * 32, row * 32), (32, 32))
                screen.blit(self.select_surf, rect)

    def create_path(self):
        self.grid = Grid(matrix=self.matrix)  # Reset grid to ensure accurate pathfinding

        start_x, start_y = self.roomba.sprite.get_coord()
        start = self.grid.node(start_x, start_y)

        mouse_pos = pygame.mouse.get_pos()
        end_x, end_y = mouse_pos[0] // 32, mouse_pos[1] // 32
        end = self.grid.node(end_x, end_y)

        finder = AStarFinder()
        self.path, _ = finder.find_path(start, end, self.grid)
        self.grid.cleanup()
        self.roomba.sprite.set_path(self.path)

    def draw_path(self, screen):
        if self.path:
            points = []
            for point in self.path:
                x = (point.x * 32) + 16
                y = (point.y * 32) + 16
                points.append((x, y))

            pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

    def update(self, screen):
        self.draw_active_cell(screen)
        self.draw_path(screen)
        self.roomba.update(screen)
        self.roomba.draw(screen)

class Roomba(pygame.sprite.Sprite):
    def __init__(self, empty_path):
        super().__init__()
        self.image = pygame.image.load('pics/roomba.png').convert_alpha()
        self.rect = self.image.get_rect(center=(60, 60))

        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 3
        self.direction = pygame.math.Vector2(0, 0)
        self.previous_direction = None

        self.path = []
        self.collision_rects = []
        self.empty_path = empty_path

    def get_coord(self):
        col = self.rect.centerx // 32
        row = self.rect.centery // 32
        return col, row

    def set_path(self, path):
        self.path = path
        self.create_collision_rects()
        self.get_direction()

    def create_collision_rects(self):
        if self.path:
            self.collision_rects = []
            for point in self.path:
                x = (point.x * 32) + 16
                y = (point.y * 32) + 16
                rect = pygame.Rect((x - 2, y - 2), (4, 4))
                self.collision_rects.append(rect)

    def get_direction(self):
        if self.collision_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center)
            # print(f"Start position: {start}, End position: {end}")

            # Calculate the direction vector
            direction = (end - start)
            if direction.length() != 0:
                self.direction = direction.normalize()
            else:
                self.direction = pygame.math.Vector2(0, 0)

            # print(f"New direction: {self.direction}")
        else:
            self.direction = pygame.math.Vector2(0, 0)
            self.path = []

    def print_direction(self):
        if self.previous_direction is None:
            self.previous_direction = self.direction
            return

        angle = self.direction.angle_to(self.previous_direction)
        if angle == 0:
            print("Moving forward")
        elif angle == 90:
            print("Turning right")
        elif angle == -90:
            print("Turning left")
        elif angle == 180 or angle == -180:
            print("Reversing")

        self.previous_direction = self.direction

    def check_collisions(self):
        if self.collision_rects:
            if self.collision_rects[0].collidepoint(self.pos):
                del self.collision_rects[0]
                self.get_direction()
        else:
            self.empty_path()

    def boundary_check(self, screen):
        screen_rect = screen.get_rect()
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.pos = pygame.math.Vector2(self.rect.center)
            self.direction = pygame.math.Vector2(0, 0)

    def update(self, screen):
        if self.path:
            self.pos += self.direction * self.speed
            # print(f"Updated position: {self.pos}")
            self.check_collisions()
            self.rect.center = self.pos
            self.boundary_check(screen)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 736))
clock = pygame.time.Clock()

bg_surf = pygame.image.load('pics/map2.png').convert()
matrix = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,0,0,0],
    [0,1,1,1,1,1,0,0,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,1,0,0,0],
    [0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1,0],
    [0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
pathfinder = Pathfinder(matrix)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pathfinder.create_path()

    screen.blit(bg_surf, (0, 0))
    pathfinder.update(screen)

    pygame.display.update()
    clock.tick(30)
