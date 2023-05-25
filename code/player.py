import pygame
from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-20, -20)

        # graphics setup
        self.import_player_assets()
        self.status = 'down'
        
        # movement
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

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.maigc = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.health = self.stats['health'] / 100 * 44.8
        self.energy = self.stats['energy'] / 100 * 70.12
        self.exp = 123
        self.speed = self.stats['speed']

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
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                
                self.weapon = list(weapon_data.keys())[self.weapon_index]
                # self.attack_cooldown = weapon_data[self.weapon]['cooldown']

            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                if self.magic_index < len(list(magic_data.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0
                
                self.magic = list(magic_data.keys())[self.magic_index]

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

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

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