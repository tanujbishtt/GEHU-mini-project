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

# background images
bg_img_1 = pygame.image.load("assets/background/1.png").convert_alpha()
bg_img_2 = pygame.image.load("assets/background/2.png").convert_alpha()
bg_img_3 = pygame.image.load("assets/background/3.png").convert_alpha()
bg_img_4 = pygame.image.load("assets/background/4.png").convert_alpha()
bg_img_5 = pygame.image.load("assets/background/5.png").convert_alpha()

# scale background images
bg_img_1 = pygame.transform.scale(bg_img_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img_2 = pygame.transform.scale(bg_img_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img_3 = pygame.transform.scale(bg_img_3, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img_4 = pygame.transform.scale(bg_img_4, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img_5 = pygame.transform.scale(bg_img_5, (SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("2D platformer")
pygame.display.set_icon(icon)

# set frame rate
clock = pygame.time.Clock()
FPS = 75

# define game variables
GRAVITY = 0.5
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_TYPES = 50
TILE_SIZE = SCREEN_HEIGHT // ROWS
LEVEL = 1
screen_scroll = 0
bg_scroll = 0

# define player variables
moving_right = False
moving_left = False
shoot = False

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/tiles/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

def DrawBackground():
    width = bg_img_1.get_width()
    for i in range(5):
        screen.blit(bg_img_5, ((i*width) - bg_scroll * 0.4, 0))
        screen.blit(bg_img_4, ((i*width) - bg_scroll*0.5,SCREEN_HEIGHT - bg_img_4.get_height() - 30))
        screen.blit(bg_img_3, ((i*width) - bg_scroll*0.6,SCREEN_HEIGHT - bg_img_3.get_height() - 30))
        screen.blit(bg_img_2, ((i*width) - bg_scroll*0.7,SCREEN_HEIGHT - bg_img_2.get_height() - 30))
        screen.blit(bg_img_1, ((i*width) - bg_scroll*0.8,SCREEN_HEIGHT - bg_img_1.get_height() - 30))

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, char_type, scale=2, speed=5):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
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
        self.vision = pygame.Rect(0, 0, 250, 10)

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
        s_scroll = 0
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
            self.velocity_y = -12
            self.jump = False
            self.in_air = True

        # apply gravity
        self.velocity_y += GRAVITY
        if self.velocity_y > 10:
            self.velocity_y = 10

        dy += self.velocity_y

        # check for collision
        for tile in world.obstacle_list:
            # check for collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # check if the player is jumping
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if the player is falling
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if self.char_type == 'player':
            # check for collision with water
            if pygame.sprite.spritecollide(self, water_group, False):
                    player.alive = False
                    screen_scroll = 0
                    dx = 0
                    dy = 0
                    self.update_action(3)
        
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update the position of the sprite
        self.rect.x += dx
        self.rect.y += dy

        # update the scroll based on the player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and \
                bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or \
                (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                s_scroll = -dx
        return s_scroll

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
            self.cooldown = 20
            arrow = Arrow(self.rect.centerx + self.rect.width * 0.7 *
                          self.direction, self.rect.centery, self.direction)
            arrow_group.add(arrow)

    def ai(self):
        if self.alive and player.alive:
            # random idle pause for enemy
            if random.randint(1, 200) == 45 and self.idling == False:
                self.idling = True
                self.update_action(0)
                self.idling_counter = 50

            # check if the enemy is near the player
            # Draw enemy vision rectangle for debugging
            pygame.draw.rect(screen, (0, 255, 0), self.vision, 2)
            if self.vision.colliderect(player.rect):
                # stop running
                self.update_action(0)
                self.Shoot()

            # move if enemy is not idling
            elif self.idling == False:
                if self.direction == 1:
                    ai_moving_right = True
                    ai_moving_left = False
                else:
                    ai_moving_right = False
                    ai_moving_left = True

                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1)
                self.move_counter += 1

                # enemy vision implementation
                self.vision.center = (self.rect.centerx + (self.rect.width * self.direction), self.rect.centery)

                if self.move_counter > TILE_SIZE:
                    self.direction *= -1
                    self.move_counter = 0
            else:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False

        # scroll the screen with the player
        self.rect.x += screen_scroll

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for x, row in enumerate(data):
            for y, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = y * TILE_SIZE
                    img_rect.y = x * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 30:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 31 and tile <= 42:
                        decor = Decoration(img, y * TILE_SIZE, x * TILE_SIZE)
                        decoration_group.add(decor)
                    elif tile >= 43 and tile <= 44:
                        water = Water(img, y * TILE_SIZE, x * TILE_SIZE)
                        water_group.add(water)
                    elif tile == 45:
                        player = Player(y * TILE_SIZE, x * TILE_SIZE, "player", 2.25, 5)
                    elif tile == 46:
                        enemy = Player(y * TILE_SIZE, x * TILE_SIZE, "enemy" , 2.15 , 2)
                        enemy_group.add(enemy)
                    elif tile == 47:
                        exit = Exit(img, y * TILE_SIZE, x * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 48:
                        health = ItemBox('health', y * TILE_SIZE, x * TILE_SIZE)
                        item_boxes_group.add(health)
                    elif tile == 49:
                        coin = ItemBox('coin', y * TILE_SIZE, x * TILE_SIZE)
                        item_boxes_group.add(coin)
        return player

    def draw(self):
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        # check if the player has collided with the item box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'coin':
                player.coins += 1
            elif self.item_type == 'health':
                if player.health < player.max_health:
                    player.health += 10
                    if player.health > player.max_health:
                        player.health = player.max_health
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
        self.rect.x += self.speed * self.direction + screen_scroll

        # check if bullet is off the screen
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            self.kill()

        # check for collision with the environment
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
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
enemy_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_boxes_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# create empty lists for the level
world_Data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_Data.append(r)
# load the level data from the csv file
with open(f'levels/level_{LEVEL}.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_Data[x][y] = int(tile)

world = World()
player = world.process_data(world_Data)
run = True
while run:
    # drawing Things
    DrawBackground()
    world.draw()

    arrow_group.draw(screen)
    item_boxes_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)
    decoration_group.draw(screen)
    player.draw()

    arrow_group.update()
    item_boxes_group.update()
    water_group.update()
    exit_group.update()
    decoration_group.update()
    player.update()
    for en in enemy_group:
        en.draw()
        en.update()
        en.ai()

    draw_text(f'Coins: {player.coins}', pygame.font.SysFont('Bauhaus 93', 30),
              'red', screen, 50, 10)
    draw_text(f'Health: {player.health}', pygame.font.SysFont('Bauhaus 93', 30),
              'red', screen, 50, 50)

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
        screen_scroll = player.move(moving_left, moving_right)
        bg_scroll -= screen_scroll

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
