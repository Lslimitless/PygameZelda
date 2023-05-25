import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('virtical')
        self.rect.center = self.hitbox.center
        
    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # 오른쪽으로 이동
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # 왼쪽으로 이동
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'virtical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # 아래쪽으로 이동
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # 위쪽으로 이동
                        self.hitbox.top = sprite.hitbox.bottom
    