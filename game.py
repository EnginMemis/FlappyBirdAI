import pygame as pg
import random
import sys
import numpy as np

pg.init()

class FlappyBirdAI:
    def __init__(self, w=576, h=900):
        self.w = w
        self.h = h
        self.screen = pg.display.set_mode((self.w, self.h))
        pg.display.set_caption("Flappy Bird AI")
        self.clock = pg.time.Clock()

        self.score = 0
        self.gravity = 0.25
        self.bird_movement = 0
        self.bird_jump_speed = 4
        self.objects_speed = 5
        self.game_speed = 200
        self.floor_x_pos = 0
        self.game_over = False
        self.frame_iteration = 0

        self.background = pg.image.load("sprites/background-day.png").convert()
        self.background = pg.transform.scale2x(self.background)

        self.bird = pg.image.load("sprites/yellowbird-midflap.png").convert_alpha()
        self.bird = pg.transform.scale2x(self.bird)

        self.bird_rect = self.bird.get_rect(center=(100, self.h // 2))

        self.floor_base = pg.image.load("sprites/base.png").convert()
        self.floor_base = pg.transform.scale2x(self.floor_base)

        self.message = pg.image.load("sprites/message.png").convert_alpha()
        self.message = pg.transform.scale2x(self.message)
        self.game_over_rect = self.message.get_rect(center=(self.w // 2, self.h // 2))

        self.bottom_pipe_surface = pg.image.load("sprites/pipe-green.png").convert_alpha()
        self.bottom_pipe_surface = pg.transform.scale2x(self.bottom_pipe_surface)

        self.top_pipe_surface = pg.image.load("sprites/pipe-green.png").convert_alpha()
        self.top_pipe_surface = pg.transform.scale2x(self.top_pipe_surface)
        self.top_pipe_surface = pg.transform.flip(self.top_pipe_surface, False, True)

        self.message = pg.image.load("sprites/message.png").convert_alpha()
        self.message = pg.transform.scale2x(self.message)
        self.game_over_rect = self.message.get_rect(center=(self.w // 2, self.h // 2))

        self.point_list = self.read_points()

        self.pipe_list = []

        bottom, top = self.create_pipe()
        self.pipe_list.append([bottom, top])

    def reset(self):
        self.bird_rect.center = (100, self.h // 2)
        self.bird_movement = 0
        self.pipe_list.clear()

        bottom, top = self.create_pipe()
        self.pipe_list.append([bottom, top])
        
        self.score = 0
        self.game_over = False

    def check_key(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                return True
        return False
            

    def read_points(self):
        point_list = []
        for i in range(10):
            point_image = pg.image.load("sprites/" + str(i) + ".png").convert_alpha()
            point_image = pg.transform.scale2x(point_image)
            point_list.append(point_image)
        return point_list
    
    def create_pipe(self):
        random_pipe_pos = random.randint(400, 700)
        top_pipe = self.top_pipe_surface.get_rect(midbottom = (600, random_pipe_pos - 150))
        bottom_pipe = self.bottom_pipe_surface.get_rect(midtop = (600, random_pipe_pos))
        return bottom_pipe, top_pipe
    
    def draw_pipe(self, pipes):
        for pipe in pipes:
            self.screen.blit(self.bottom_pipe_surface, pipe[0])
            self.screen.blit(self.top_pipe_surface, pipe[1])

    def check_pipe(self, pipes):
        for i in range(len(pipes)):
            if pipes[i][0].x + pipes[i][0].width < 0:
                pipes.pop(i)
                break

    def update(self):
        pg.display.update()

    def movement(self):
        self.bird_movement += self.gravity
        self.bird_rect.centery += self.bird_movement
        self.screen.blit(self.bird, self.bird_rect)

    def move_pipes(self, pipes):
        for pipe in pipes:
            pipe[0].centerx -= self.objects_speed
            pipe[1].centerx -= self.objects_speed
        return pipes

    def check_collision(self, pipes, point):
        point_check = True
        for pipe in pipes:
            if self.bird_rect.colliderect(pipe[0]) or self.bird_rect.colliderect(pipe[1]):
                return True, point
            if self.bird_rect.centerx == pipe[0].centerx and point_check:
                point += 1
                point_check = False
                bottom, top = self.create_pipe()
                pipes.append([bottom, top])
            elif self.bird_rect.centerx > pipe[0].centerx:
                point_check = True

        if self.bird_rect.top <= 0 or self.bird_rect.bottom >= self.h:
            return True, point
        return False, point
    
    def draw_point(self):
        total_width = 0
        digit_list = []
        if self.score == 0:
            digit_list.append(0)
        else:
            temp = self.score
            while temp != 0:
                digit_list.append(temp % 10)
                temp = temp // 10

        for digit in digit_list:
            total_width += self.point_list[digit].get_width()
            
        x = (self.w - total_width) // 2
        y = self.w // 3

        digit_list.reverse()
        
        for digit in digit_list:
            self.screen.blit(self.point_list[digit], (x, y))
            x += self.point_list[digit].get_width()
    
    def play_step(self, action):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        if np.array_equal(action, [0, 1]):
            self.bird_movement = 0
            self.bird_movement -= self.bird_jump_speed

        reward = 0        

        self.screen.blit(self.background, (0, 0))
        self.movement()
        self.draw_pipe(self.pipe_list)
        self.pipe_list = self.move_pipes(self.pipe_list)
        self.check_pipe(self.pipe_list)
        temp_score = self.score
        self.game_over, self.score = self.check_collision(self.pipe_list, self.score)
        if self.game_over == True:
            reward = -100
            
        elif temp_score != self.score:
            reward = 10
        
        self.draw_point()
        self.update()
        self.clock.tick(self.game_speed)

        return reward, self.game_over, self.score
    
