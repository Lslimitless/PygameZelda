import pygame
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-20, -20)

        # graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # movement input
            self.direction.y = 0
            if keys[pygame.K_UP]:
                self.direction.y -= 1
                self.status = 'up'
            if keys[pygame.K_DOWN]:
                self.direction.y += 1
                self.status = 'down'

            self.direction.x = 0
            if keys[pygame.K_RIGHT]:
                self.direction.x += 1
                self.status = 'right'
            if keys[pygame.K_LEFT]:
                self.direction.x -= 1
                self.status = 'left'

            # attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print('magic')

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                
                self.weapon = list(weapon_data.keys())[self.weapon_index]
                # self.attack_cooldown = weapon_data[self.weapon]['cooldown']

    def get_status(self):

        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            # in : 변수에 문자열이 들어있는지 ex) 'cde' in 'abcdefg' -> True
            # status에 'idle', 'attack'이 모두 들어있지 않을 때
            if not '_idle' in self.status and not '_attack' in self.status:
                self.status = self.status + '_idle'

        # attack status
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not '_attack' in self.status:
                if '_idle' in self.status:
                    # replace('a', 'b') : 'a' -> 'b' *포함된 문자열을 모두 바꿈*
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if '_attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def import_player_assets(self):
        character_path = './graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                           'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []}
        
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def move(self, speed):
        if self.direction.magnitude() != 0: # magnitude() : 피타고라스의 정리를 이용한 벡터의 길이를 반환함 sqrt(x^2 + y^2) -> r^2 = x^2 + y^2
            self.direction = self.direction.normalize() # normalize() : 방향이 같은 길이가 1인 벡터를 반환함

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('virtical')
        self.rect.center = self.hitbox.center
        
        # pygame.rect 는 실수를 표현할 수 없기 때문에 소수 대입 시 반올림으로 적용함
        # 예전에는 버림 처리 하였기에 좌,우 그리고 상,하 각각 이동거리가 달랐음
        # pos값을 따로 관리하고 rect에 pos값을 대입하는것이 좋겠음

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
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)