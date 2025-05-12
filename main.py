import pygame
import random
import csv
import time
import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load images
icon = pygame.image.load("assets/icon.png").convert_alpha()
arrow_img = pygame.image.load("assets/arrow.png").convert_alpha()
coin_img = pygame.image.load("assets/coin.png").convert_alpha()
health_box = pygame.image.load("assets/health.png").convert_alpha()
item_boxes = {
    'health': health_box,
    'coin': coin_img
}

pygame.display.set_caption("2D platformer")
pygame.display.set_icon(icon)

# set frame rate
clock = pygame.time.Clock()
FPS = 75

# define game variables
GRAVITY = 0.5
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 18
LEVEL = 1

# define player variables
moving_right = False
moving_left = False
shoot = False


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def Draw_BG():
    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 255, 255), (0, SCREEN_HEIGHT - 50),
                     (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
    pygame.draw.rect(screen, (0, 255, 0),
                     (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, char_type, scale=2, speed=5):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.direction = 1
        self.flip = False  # flip the image if moving left
        self.jump = False
        self.coins = 0
        self.in_air = False
        self.velocity_y = 0
        self.health = 100
        self.max_health = self.health
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.cooldown = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        # ai character vars
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)

        # load all images for the character
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'assets/{char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'assets/{char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.cooldown > 0:
            self.cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0
        # assign the image to the sprite based on the direction of movement
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jumping
        if self.jump and not self.in_air:
            self.velocity_y = -10
            self.jump = False
            self.in_air = True
        # apply gravity
        # self.velocity_y += GRAVITY
        # if self.velocity_y > 10:
        #     self.velocity_y = 10

        dy += self.velocity_y

        # check for collision with the ground
        if self.rect.bottom + dy > SCREEN_HEIGHT - 50:
            dy = SCREEN_HEIGHT - 50 - self.rect.bottom
            self.in_air = False
            self.velocity_y = 0
        else:
            self.velocity_y += GRAVITY
            if self.velocity_y > 10:
                self.velocity_y = 10

        # update the position of the sprite
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
            if self.index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.index = len(self.animation_list[self.action]) - 1
                else:
                    self.index = 0
            self.image = self.animation_list[self.action][self.index]

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0 and self.alive == True:
            self.alive = False
            self.health = 0
            self.speed = 0
            self.update_action(3)

    def Shoot(self):
        if self.cooldown == 0:
            self.cooldown = 40
            arrow = Arrow(self.rect.centerx + self.rect.width * 0.7 *
                          self.direction, self.rect.centery, self.direction)
            arrow_group.add(arrow)

    def ai(self):
        if self.alive and player.alive:
            # random idle pause for enemy
            if random.randint(1, 200) == 1 and self.idling == False:
                self.idling = True
                self.update_action(0)
                self.idling_counter = 50
            
            # check if the enemy is near the player
            if self.vision.colliderect(player.rect):
                # stop running
                self.update_action(0)
                self.Shoot()

            # move if enemy is not idling
            elif self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                else:
                    ai_moving_right = False
                ai_moving_left = not ai_moving_right
                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1)
                self.move_counter += 1

                # enemy vision implementation
                self.vision.center = (self.rect.centerx + (self.rect.width * self.direction), self.rect.centery)
                pygame.draw.rect(screen, (255, 0, 0), self.vision)

                if self.move_counter > TILE_SIZE:
                    self.direction *= -1
                    self.move_counter *= -1
            else:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False
                    self.move_counter = 0
                    self.update_action(1)

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has collided with the item box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'coin':
                player.coins += 1
                print("coin collected", player.coins)
            elif self.item_type == 'health':
                if player.health < player.max_health:
                    player.health += 10
                    if player.health > player.max_health:
                        player.health = player.max_health
                print("health increased", player.health)
            self.kill()


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 12
        self.image = arrow_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += self.speed * self.direction

        # check for collision with the wall
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            self.kill()

        # check for collision with the player
        if pygame.sprite.spritecollide(player, arrow_group, False):
            if player.alive:
                player.health -= 10
                self.kill()
        # check for collision with the enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, arrow_group, False):
                if enemy.alive:
                    enemy.health -= 10
                    self.kill()


# create sprite groups
arrow_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_boxes_group = pygame.sprite.Group()
player = Player(200, SCREEN_HEIGHT - 100, "player", 2, 4)
enemy = Player(300, SCREEN_HEIGHT - 100, "enemy", 2, 2)
enemy2 = Player(600, SCREEN_HEIGHT - 100, "enemy", 2, 2)
coin = ItemBox('coin', 400, 600)
coin1 = ItemBox('coin', 500, 600)
coin2 = ItemBox('coin', 600, 600)
coin3 = ItemBox('coin', 700, 600)
item_boxes_group.add(coin)
item_boxes_group.add(coin1)
item_boxes_group.add(coin2)
item_boxes_group.add(coin3)
enemy_group.add(enemy)
enemy_group.add(enemy2)


# create empty lists for the level
world_Data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_Data.append(r)
# load the level data from the csv file
with open(f'levels/level_{LEVEL}.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x,row in enumerate(reader):
        for y,tile in enumerate(row):
            world_Data[x][y] = int(tile)








run = True
while run:
    # drawing Things
    Draw_BG()

    # draw the enemy
    for en in enemy_group:
        en.draw()
        en.update()
        en.ai()

    # draw the player
    player.draw()
    player.update()
    arrow_group.update()
    arrow_group.draw(screen)
    item_boxes_group.update()
    item_boxes_group.draw(screen)
    draw_text(f'Coins: {player.coins}', pygame.font.SysFont('Bauhaus 93', 30),
              (255, 255, 255), screen, 10, 10)
    draw_text(f'Health: {player.health}', pygame.font.SysFont('Bauhaus 93', 30),
              (255, 255, 255), screen, 10, 50)

    # update the player animation and shooting mechanism
    if player.alive:
        if shoot:
            player.Shoot()
            shoot = False
        elif player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)
        player.move(moving_left, moving_right)

    # check for key presses
    for event in pygame.event.get():
        # check for quit event
        if event.type == pygame.QUIT:
            run = False

        # check for keydown event
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_f:
                shoot = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # check for keyup event
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_f:
                shoot = False

    # update the display and tick the clock
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
