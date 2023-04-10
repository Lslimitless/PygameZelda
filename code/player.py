import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.obstacle_sprites = obstacle_sprites

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.y = 0
        if keys[pygame.K_UP]:
            self.direction.y -= 1
        if keys[pygame.K_DOWN]:
            self.direction.y += 1

        self.direction.x = 0
        if keys[pygame.K_RIGHT]:
            self.direction.x += 1
        if keys[pygame.K_LEFT]:
            self.direction.x -= 1

    def move(self, speed):
        if self.direction.magnitude() != 0: # magnitude() : 피타고라스의 정리를 이용한 벡터의 길이를 반환함 sqrt(x^2 + y^2) -> r^2 = x^2 + y^2
            self.direction = self.direction.normalize() # normalize() : 방향이 같은 길이가 1인 벡터를 반환함
        
        self.rect.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * speed
        self.collision('virtical')
        # self.rect.center += self.direction * speed
        
        # pygame.rect 는 실수를 표현할 수 없기 때문에 이동에 오차가 발생함

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0: # 오른쪽으로 이동
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0: # 왼쪽으로 이동
                        self.rect.left = sprite.rect.right

        if direction == 'virtical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0: # 아래쪽으로 이동
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: # 위쪽으로 이동
                        self.rect.top = sprite.rect.bottom

    def update(self):
        self.input()
        self.move(self.speed)