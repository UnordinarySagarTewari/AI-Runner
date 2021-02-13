import pygame
import os
import random
import math
import sys
import neat

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI by SAGAR TEWARI")


RUNNING0 = [pygame.image.load( "Run (1).png"),
           pygame.image.load( "Run (2).png"),
           pygame.image.load( "Run (3).png"),
           pygame.image.load( "Run (4).png"),
           pygame.image.load( "Run (5).png"),
           pygame.image.load( "Run (6).png"),
           pygame.image.load( "Run (7).png"),
           pygame.image.load( "Run (8).png")]
RUNNING = []
for i in RUNNING0:
    RUNNING.append(pygame.transform.scale(i,(80,90)))

JUMPING = pygame.transform.scale(pygame.image.load( "Jump (6).png"),(80,90))

SMALL_CACTUS0 = [pygame.image.load( "Cactus.png"),
                pygame.image.load( "Zombie(1).png"),
                pygame.image.load( "Zombie(3).png"),
                 pygame.image.load( "Zombie(4).png")]
SMALL_CACTUS=[]
for i in SMALL_CACTUS0:
    SMALL_CACTUS.append(pygame.transform.flip(pygame.transform.scale(i,(71,71)),True,False))
LARGE_CACTUS0 = [pygame.image.load( "NewCactus.png"),
                pygame.image.load( "NewCactus.png"),
                pygame.image.load( "Zombie(2).png")]

LARGE_CACTUS=[]
for i in LARGE_CACTUS0:
    LARGE_CACTUS.append(pygame.transform.scale(i,(100,90)))


BG = pygame.image.load("Track.png")
BG1 = pygame.transform.scale(pygame.image.load("Sky.png"),(1100,440))
SCREEN = win.blit(BG1,(0,0))

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Jack:
    X_POS = 80
    Y_POS = 300
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.jack_run = True
        self.jack_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.jack_run:
            self.run()
        if self.jack_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = JUMPING
        if self.jack_jump:
            self.rect.y -= int(self.jump_vel * 4)
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.jack_jump = False
            self.jack_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        win.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(win, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(win, self.color, (self.rect.x + 44, self.rect.y + 40), obstacle.rect.center, 2)
            pygame.draw.line(win, self.color, (self.rect.x + 58, self.rect.y + 40), obstacle.rect.center, 2)


class Obstacle:
    def __init__(self, image, number_of_obs):
        self.image = image
        self.type = number_of_obs
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        win.blit(self.image[self.type], self.rect)


class SmallObstacle(Obstacle):
    def __init__(self, image, number_of_obs):
        super().__init__(image, number_of_obs)
        self.rect.y = 325


class LargeObstacle(Obstacle):
    def __init__(self, image, number_of_obs):
        super().__init__(image, number_of_obs)
        self.rect.y = 300


def remove(index):
    jacks.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, obstacles, jacks, ge, nets, points
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    jacks = []
    ge = []
    nets = []

    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 30

    for genome_id, genome in genomes:
        jacks.append(Jack())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        win.blit(text, (950, 50))

    def statistics():
        global jacks, game_speed, ge
        text_0 = FONT.render(f'Statistics:', True, (0, 0, 0))
        text_1 = FONT.render(f'Jack o\' Lanterns Alive:  {str(len(jacks))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        win.blit(text_0, (50, 450))
        win.blit(text_1, (50, 480))
        win.blit(text_2, (50, 510))
        win.blit(text_3, (50, 540))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN = win.blit(BG1,(0,0))
        win.blit(BG, (x_pos_bg, y_pos_bg))
        win.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        

        win.fill((255, 255, 255))
        background()

        for jack in jacks:
            jack.update()
            jack.draw(SCREEN)

        if len(jacks) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallObstacle(SMALL_CACTUS, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(LargeObstacle(LARGE_CACTUS, random.randint(0, 2)))

        for obstacle in obstacles:
            obstacle.draw(win)
            obstacle.update()
            for i, jack in enumerate(jacks):
                if jack.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, jack in enumerate(jacks):
            output = nets[i].activate((jack.rect.y,
                                       distance((jack.rect.x, jack.rect.y),
                                        jack.rect.midtop)))
            if output[0] > 0.5 and jack.rect.y == jack.Y_POS:
                jack.jack_jump = True
                jack.jack_run = False

        statistics()
        score()
        
        clock.tick(20)
        pygame.display.update()


# Setup the NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = 'config.txt'
    run(config_path)
