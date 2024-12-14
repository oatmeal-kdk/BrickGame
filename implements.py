import math
import random
import time

import config

import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)


class Block(Basic):
    def __init__(self, color: tuple, pos: tuple = (0,0), alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive

    def draw(self, surface) -> None:
        if self.alive:  # alive가 True인 블록만 그림
            pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self):
        # ============================================
        # TODO: Implement an event when block collides with a ball
        
        self.alive = False
        # 블록이 공에 부딪혔을 때 블록이 없어지는 기능은 Block.draw에서 구현
        # if self.alive: 
        #     pygame.draw.rect(surface, self.color, self.rect)

class GrayBlock(Block):
    def __init__(self, pos: tuple = (0,0), hits_required: int = 3):
        super().__init__((128,128,128), pos)
        self.hits_required = hits_required
    
    def draw(self, surface) -> None:
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            font = pygame.font.SysFont(None,24)
            hits_text = font.render(str(self.hits_required), True, (255,255,255))
            surface.blit(hits_text, (self.rect.centerx - hits_text.get_width
                                     ()//2 ,self.rect.centery - hits_text.get_height()//2))

    def collide(self):
        self.hits_required -=1
        if self.hits_required <= 0:
            self.alive = False

class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)


class Ball(Basic):
    def __init__(self, pos: tuple = config.ball_pos):
        super().__init__(config.ball_color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        self.dir = 90 + random.randint(-45, 45)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks: list):
        # ============================================
        # TODO: Implement an event when the ball hits a block
        
        for block in blocks:
            if self.rect.colliderect(block.rect) and block.alive:
            # 충돌 방향 계산
                if abs(self.rect.bottom - block.rect.top) < abs(self.speed) or abs(self.rect.top - block.rect.bottom) < abs(self.speed):
                    self.dir = 360 - self.dir  # 위/아래 반사
                elif abs(self.rect.right - block.rect.left) < abs(self.speed) or abs(self.rect.left - block.rect.right) < abs(self.speed):
                    self.dir = 180 - self.dir  # 좌/우 반사

                block.collide()

                if isinstance(block, GrayBlock) and block.hits_required > 0:
                    continue
                
                if not block.alive:
                    blocks.remove(block)
                break

    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    def hit_wall(self):
        # ============================================
        # TODO: Implement a service that bounces off when the ball hits the wall

        # 좌우 벽 충돌
        if self.rect.left <= 0: 
            self.dir = 180 - self.dir
        if self.rect.right >= config.display_dimension[0]: 
            self.dir = 180 - self.dir
        
        # 상단 벽 충돌
        if self.rect.top <= 0:
            self.dir = 360 - self.dir
    
    def alive(self):
        # ============================================
        # TODO: Implement a service that returns whether the ball is alive or not
        
        if self.rect.bottom > 800: return False
        else: return True