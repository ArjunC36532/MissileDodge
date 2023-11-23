import itertools
import random
import sys
import random
import threading
import time
from threading import Thread

import pygame

pygame.font.init()
pygame.mixer.init()


player_missiles = []
enemy_missiles = []

fire_sound = pygame.mixer.Sound("TIE fighter fire 1.mp3")

GAME_WIDTH, GAME_HEIGHT = 1128, 480
VEL = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_WIDTH, PLAYER_HEIGHT = 55, 40
ENEMY_WIDTH, ENEMY_HEIGHT = 55, 40
MISSILE_WIDTH, MISSILE_HEIGHT = 56.9, 44

PLAYER_IMAGE = pygame.image.load("spaceship_yellow.png")
ENEMY_IMAGE = pygame.image.load("spaceship_red.png")

BACKGROUND = pygame.transform.scale(pygame.image.load("space.png"), (1128, 480))

WINDOW = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
FPS = 250
clock = pygame.time.Clock()
MISSILE_IMAGE = pygame.image.load("missile.png")
PlayerObjects = []
EnemyObjects = []


def combinations(list_1, list_2):
    unique_combinations = []
    permutations = itertools.permutations(list_1, len(list_2))

    for combination in permutations:
        zipped = zip(combination, list_2)
        unique_combinations.append(list(zipped))
    return unique_combinations


class Player():
    def __init__(self, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_IMAGE, VEL, GAME_WIDTH, GAME_HEIGHT):
        self.BLACK = (0, 0, 0)
        self.red = 0
        self.green = 255
        self.blue = 0
        self.vel = VEL
        self.player_width = PLAYER_WIDTH
        self.player_height = PLAYER_HEIGHT
        self.player_image = PLAYER_IMAGE
        self.player = pygame.transform.rotate(
            pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT)), 90)
        self.player_rect = pygame.Rect(50, 300, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.game_width = GAME_WIDTH
        self.game_height = GAME_HEIGHT
        self.health_bar_length = self.player_width
        self.health_bar_height = 10
        self.health = 100
        self.ratio = self.player_width / 100

    def keyboard_input(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a]:
            self.player_rect.x -= self.vel
        if keys_pressed[pygame.K_d]:
            self.player_rect.x += self.vel
        if keys_pressed[pygame.K_w]:
            self.player_rect.y -= self.vel
        if keys_pressed[pygame.K_s]:
            self.player_rect.y += self.vel

    def clamp(self):
        if self.player_rect.x <= 0:
            self.player_rect.x = 0
        if self.player_rect.x >= self.game_width / 2 - self.player_rect.width:
            self.player_rect.x = self.game_width / 2 - self.player_rect.width

        if self.player_rect.y >= 480 - self.player_rect.height - 20:
            self.player_rect.y = 480 - self.player_rect.height - 20
        if self.player_rect.y <= 0 + self.health_bar_height + 5:
            self.player_rect.y = 0 + self.health_bar_height + 5

    def lose_health(self):
        self.health -= 10
        if self.health > - 66.67:
            self.red, self.green, self.blue = 0, 255, 0
        if 33.33 <= self.health < 66.67:
            self.red, self.green, self.blue = 255, 255, 0
        if self.health < 33.33:
            self.red, self.green, self.blue = 255, 0, 0

    def tick(self):
        self.clamp()
        self.keyboard_input()

    def render(self):

        WINDOW.blit(self.player, (self.player_rect.x, self.player_rect.y))

        pygame.draw.rect(WINDOW, (self.red, self.green, self.blue),
                         pygame.Rect(self.player_rect.x, self.player_rect.y - 20, (self.ratio * self.health),
                                     self.health_bar_height))
        pygame.draw.rect(WINDOW, self.BLACK,
                         pygame.Rect(self.player_rect.x, self.player_rect.y - 20, self.health_bar_length,
                                     self.health_bar_height), 3)


class Enemy:
    def __init__(self, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_IMAGE, VEL, GAME_WIDTH, GAME_HEIGHT):
        self.enemy_image = pygame.image.load("spaceship_red.png")
        self.enemy_width = ENEMY_WIDTH
        self.enemy_height = ENEMY_HEIGHT
        self.vel = VEL
        self.game_height = GAME_HEIGHT
        self.enemy = pygame.transform.rotate(
            pygame.transform.scale(self.enemy_image, (self.enemy_width, self.enemy_height)), 270)
        self.enemy_coordinates = []
        self.enemy_active = [True, False, False, False, False]

        self.red = 0
        self.green = 255
        self.blue = 0
        self.BLACK = (0, 0, 0)

        self.ratio = self.enemy_width / 100
        self.health = None
        self.health_bar_length = self.enemy_width
        self.health_bar_height = 10

        self.enemy_healths = [100, 100, 100, 100, 100]

        for i in range(5):
            random_x = random.randint(500, 900)
            random_y = random.randint(0, 400)
            self.enemy_coordinates.append([random_x, random_y])

    def add_enemy(self):
        obj = self.enemy.get_rect()
        obj.x, obj.y = (1200, 230)
        EnemyObjects.append(obj)

    def tick(self):
        for enemy in EnemyObjects:
            pos = EnemyObjects.index(enemy)

            if self.enemy_active[pos]:
                # print("Current X: {} Current Y:{} Target X: {} Target Y: {}".format(enemy.x, enemy.y,
                #                                                                     self.enemy_coordinates[pos][0],
                #                                                                     self.enemy_coordinates[pos][1]))
                if enemy.x == self.enemy_coordinates[pos][0] and enemy.y == self.enemy_coordinates[pos][1]:
                    new_x = random.randint(500, 900)
                    new_y = random.randint(0, 400)

                    missile_handler.add_enemy_missile(enemy)

                    self.enemy_coordinates[pos] = [new_x, new_y]
                else:
                    if enemy.x < self.enemy_coordinates[pos][0]:
                        enemy.x += self.vel
                    if enemy.x > self.enemy_coordinates[pos][0]:
                        enemy.x -= self.vel
                    if enemy.y > self.enemy_coordinates[pos][1]:
                        enemy.y -= self.vel
                    if enemy.y < self.enemy_coordinates[pos][1]:
                        enemy.y += self.vel

    def render(self):
        for enemy in EnemyObjects:
            pos = EnemyObjects.index(enemy)
            WINDOW.blit(self.enemy, (enemy.x, enemy.y))



class Missiles:
    def __init__(self, MISSILE_WIDTH, MISSILE_HEIGHT, MISSILE_IMAGE, VEL, GAME_WIDTH, GAME_HEIGHT):
        self.MISSILE_IMAGE = pygame.image.load("missile.png")
        self.MISSILE = pygame.transform.rotate(pygame.transform.scale(MISSILE_IMAGE, (MISSILE_WIDTH, MISSILE_HEIGHT)),
                                               270)
        self.ENEMY_MISSILE = pygame.transform.rotate(
            pygame.transform.scale(MISSILE_IMAGE, (MISSILE_WIDTH, MISSILE_HEIGHT)),
            90)
        self.missile_width = MISSILE_WIDTH
        self.missile_height = MISSILE_HEIGHT
        self.missile_image = MISSILE_IMAGE
        self.vel = VEL
        self.game_width = GAME_WIDTH
        self.game_height = GAME_HEIGHT

    def add_player_missile(self, player):
        if len(player_missiles) <= 1:
            obj = self.MISSILE.get_rect()
            obj.x, obj.y = player.player_rect.x, player.player_rect.y
            player_missiles.append(obj)

    def add_enemy_missile(self, enemy):
        if len(enemy_missiles) <= 1:
            obj = self.ENEMY_MISSILE.get_rect()
            obj.x, obj.y = enemy.x, enemy.y
            enemy_missiles.append(obj)

    def tick(self):
        # remove missiles off-screen
        for missile in player_missiles:
            if missile.x >= 1128:
                player_missiles.remove(missile)
        for missile in enemy_missiles:
            if missile.x <= 0:
                enemy_missiles.remove(missile)

    def render(self):
        # render movement of missiles
        for missile in player_missiles:
            missile.x += self.vel
            WINDOW.blit(self.MISSILE, (missile.x, missile.y))
        for enemy_missile in enemy_missiles:
            enemy_missile.x -= self.vel
            WINDOW.blit(self.ENEMY_MISSILE, (enemy_missile.x, enemy_missile.y))


def collisions(player):
    # Check for collision between player and enemy_missiles

    for enemy_missile in enemy_missiles:
        if pygame.Rect.colliderect(player.player_rect, enemy_missile):
            player.lose_health()
            enemy_missiles.remove(enemy_missile)

    for enemy in EnemyObjects:
        for player_missile in player_missiles:
            if pygame.Rect.colliderect(enemy, player_missile):
                enemy.x = 2000
                enemy.y = 200

    # Check for collisions between two opposing missiles

    # check for death
    for player in PlayerObjects:
        if player.health <= 0:
            # change this code later
            print("Enemy Won!")
            sys.exit()




player = Player(PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_IMAGE, 2, GAME_WIDTH, GAME_HEIGHT)

missile_handler = Missiles(MISSILE_WIDTH, MISSILE_HEIGHT, MISSILE_IMAGE, 2, GAME_WIDTH, GAME_HEIGHT)

enemy_handler = Enemy(ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_IMAGE, 1, GAME_WIDTH, GAME_HEIGHT)

enemy_random_coordinates = []

for i in range(5):
    enemy_handler.add_enemy()

for i in range(5):
    new_x = random.randint(500, 900)
    new_y = random.randint(0, 400)
    enemy_handler.enemy_coordinates.append([new_x, new_y])


def main():
    i = 1
    run = True
    score_value = 0
    score_break = 1000
    font = pygame.font.Font(pygame.font.get_default_font(), 32)
    score = font.render("Score: {}".format(str(score_value)), True, (BLACK))
    player_wins = font.render("Game Over", True, WHITE)

    while run:
        clock.tick(FPS)
        WINDOW.blit(BACKGROUND, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    missile_handler.add_player_missile(player)
                    fire_sound.play()

        player.tick()
        player.render()

        missile_handler.tick()
        missile_handler.render()

        enemy_handler.tick()
        enemy_handler.render()

        collisions(player)

        WINDOW.blit(score, (0, 0))

        score_value += 1
        score = font.render("Score: {}".format(str(score_value)), True, (0, 0, 0))

        if player.health <= 0:
            while True:
                clock.tick(60)
                WINDOW.fill(BLACK)
                WINDOW.blit(player_wins, (564, 240))
                pygame.display.update()

        if score_value > score_break:
            enemy_handler.enemy_active[i] = True
            score_break += 1000
            if i < 2:
                i += 1

        pygame.display.update()


if __name__ == '__main__':
    main()
