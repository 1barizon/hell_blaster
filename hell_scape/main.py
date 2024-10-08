import pygame
import sys
import os
import math
import json
from pygame.locals import *
from data.bubbles import *
import data.fps as fps
import data.engine as e
from data.bubbles import bubbles
from data.bubbles import glow

from data.tileset_loader import load_tileset
import data.text as text


# Setup pygame ---------------------------------------------------------- #
mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Hell Scape')
screen = pygame.display.set_mode((894, 594), 0, 32)
window_size = [894, 594]

pygame.mouse.set_visible(False)

display = pygame.Surface((298, 198))


# Images ---------------------------------------------------------- #
tileset_images = load_tileset('data/images/')
e.load_particle_images('data/images/particles/')


e.set_global_colorkey((0, 0, 0))
e.load_animations('data/images/entities/')


def load_img(name):
    img = pygame.image.load('data/images/' + name + '.png').convert()
    img.set_colorkey((0, 0, 0))
    return img


cursor_img = load_img('aim')
turret_barrel_img = load_img('turret_barrel')
turret_shot = load_img('turret_shot')
core_img = load_img('core_img')
turret_img = load_img('turret_img')


pygame.display.set_icon(core_img)

controls_1 = load_img('controls_1')
controls_2 = load_img('controls_2')



# sounds ----------------------------------------------------------------#
explosion_s = pygame.mixer.Sound('data/sfx/explosion.wav')
shoot_s = pygame.mixer.Sound('data/sfx/shot.wav')
jump_s = pygame.mixer.Sound('data/sfx/jump.wav')
turret_shot_s = pygame.mixer.Sound('data/sfx/turret_shot.wav')
turret_shot_s.set_volume(0.3)
death_s = pygame.mixer.Sound('data/sfx/death.wav')


pygame.mixer.music.load('data/sfx/music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)


# Font ------------------------------------------------------- #
font_dat = {'A': [3], 'B': [3], 'C': [3], 'D': [3], 'E': [3], 'F': [3], 'G': [3], 'H': [3], 'I': [3], 'J': [3], 'K': [3], 'L': [3], 'M': [5], 'N': [3], 'O': [3], 'P': [3], 'Q': [3], 'R': [3], 'S': [3], 'T': [3], 'U': [3], 'V': [3], 'W': [5], 'X': [3], 'Y': [3], 'Z': [3],
            'a': [3], 'b': [3], 'c': [3], 'd': [3], 'e': [3], 'f': [3], 'g': [3], 'h': [3], 'i': [1], 'j': [2], 'k': [3], 'l': [3], 'm': [5], 'n': [3], 'o': [3], 'p': [3], 'q': [3], 'r': [2], 's': [3], 't': [3], 'u': [3], 'v': [3], 'w': [5], 'x': [3], 'y': [3], 'z': [3],
            '.': [1], '-': [3], ',': [2], ':': [1], '+': [3], '\'': [1], '!': [1], '?': [3],
            '0': [3], '1': [3], '2': [3], '3': [3], '4': [3], '5': [3], '6': [3], '7': [3], '8': [3], '9': [3],
            '(': [2], ')': [2], '/': [3], '_': [5], '=': [3], '\\': [3], '[': [2], ']': [2], '*': [3], '"': [3], '<': [3], '>': [3], ';': [1]}


def get_text_width(text, spacing, font_dat=font_dat):
    width = 0
    for char in text:
        if char in font_dat:
            width += font_dat[char][0] + spacing
        elif char == ' ':
            width += font_dat['A'][0] + spacing
    return width


font = text.generate_font('data/font/small_font.png',
                          font_dat, 5, 8, (255, 255, 255))

# Others ---------------------------------------------------------- #

entity_info = {
    15: [20, 20, 'core', 2, 7],
    16: [20, 5, 'turret', 0, 6],
}


def normalize(val, rate):
    if val > rate:
        val -= rate
    elif val < -rate:
        val += rate
    else:
        val = 0
    return val


def cap(val, val2):
    if val > val2:
        val = val2
    if val < -val2:
        val = -val2
    return val


def dtf(dt):
    return dt / 1000 * 60


def xy2str(pos):
    return str(pos[0]) + ";" + str(pos[1])


def load_level(number):
    f = open('data/levels/level_'+str(number)+'.txt', 'r')
    dat = f.read()
    f.close()
    tile_map = json.loads(dat)
    max_height = -99999
    min_height = 99999
    spawnpoint = [0, 0]
    remove_list = []
    final_tile_map = {}
    entities = []
    total_cores = 0
    limits = [99999, -99999]
    for tile in tile_map:
        min_height = min(min_height, tile_map[tile][1][1])
        max_height = max(max_height, tile_map[tile][1][1])
        limits[0] = min(limits[0], tile_map[tile][1][0])
        limits[1] = max(limits[1], tile_map[tile][1][0])
    for tile in tile_map:
        tile_map[tile][1][1] -= min_height
        final_tile_map[xy2str(tile_map[tile][1])] = tile_map[tile].copy()

    for tile in final_tile_map:

        if final_tile_map[tile][0] == 14:
            spawnpoint = [final_tile_map[tile][1][0] * 20, final_tile_map[tile]
                          [1][1] * 20 - 40 + (max_height - min_height + 1) * 60]
            remove_list.append(tile)

        elif (final_tile_map[tile][0] >= 15) and (final_tile_map[tile][0] < 17):
            remove_list.append(tile)

            entity_dat = [e.entity(final_tile_map[tile][1][0] * 20 + entity_info[final_tile_map[tile][0]][3], final_tile_map[tile][1][1] * 20 + entity_info[final_tile_map[tile]
                                   [0]][4], entity_info[final_tile_map[tile][0]][0], entity_info[final_tile_map[tile][0]][1], entity_info[final_tile_map[tile][0]][2]), False]
            if final_tile_map[tile][0] == 16:
                entity_dat += [0, 0]
            if final_tile_map[tile][0] == 15:
                total_cores += 1

            entities.append(entity_dat)
    for tile in remove_list:
        del final_tile_map[tile]

    limits = [limits[0]*20, limits[1]*20]
    return final_tile_map, entities, max_height - min_height + 1, spawnpoint, total_cores, limits


top_tile_list = []

level = 0
tile_map, entities, map_height, spawnpoint, total_cores, limits = load_level(
    level)


current_fps = 0
dt = 0  # delta time
last_frame = pygame.time.get_ticks()
game_speed = 1


player = e.entity(spawnpoint[0] + 4, spawnpoint[1] - 17, 18, 27, 'player')
player.set_offset([-3, -2])
player_grav = 0
player_speed = 2
air_timer = 0
last_movement = [0, 0]
shoot_timer = 0
dead = False
win = 0
moved = False
player_velocity = [0, 0]
glow_size = [20, 6]

bullets = []
explosion_particles = []
particles = []
flashes = []


bar_height = 100
camera_sources = []

left = False
right = False
click = False
background_timer = 0

scroll_target = [player.get_center()[0] - 10, player.get_center()[1] - 10]
scroll = scroll_target.copy()
true_scroll = scroll.copy()

controls_timer = 0


shoot_s_cooldown = 0


while True:
    # Background ----------------------------------------------------------------#
    dt = pygame.time.get_ticks() - last_frame
    print(dt)
    last_frame = pygame.time.get_ticks()
    fps.get_time()


    display.fill((32, 25, 44))
    bubbles(window_size, display)

    if shoot_s_cooldown > 0:
        shoot_s_cooldown -= 1

    # change level ---------------------------------------------- #
    if win != 0:
        win += 1

    game_speed += (1 - game_speed) / 20

    if win < 50:
        bar_height += ((1 - game_speed) * 40 - bar_height) / 10
    elif win >= 50:
        bar_height += (110 - bar_height) / 10
        if bar_height > 100:
            level += 1
            try:
                tile_map, entities, map_height, spawnpoint, total_cores, limits = load_level(
                    level)
            except FileNotFoundError:
                break
            player = e.entity(
                spawnpoint[0]+4, spawnpoint[1] - 17, 18, 27, 'player')
            player.set_offset([-3, -2])
            bullets = []
            explosion_particles = []
            particles = []
            bullets = []
            flashes = []
            scroll_target = [player.get_center()[0], player.get_center()[1]]
            scroll = scroll_target.copy()
            true_scroll = scroll.copy()
            win = 0
            moved = False
            left = False
            right = False
            player_velocity = [0, 0]

    if abs(1 - game_speed) < 0.05:
        game_speed = 1

    scroll = [int(true_scroll[0]), int(true_scroll[1])]

    lowest = [10, None]
    for i, source in enumerate(camera_sources):
        if source[0] < lowest[0]:
            lowest = [source[0], i]

    if lowest[1] != None:
        if not dead:
            scroll_target = camera_sources[lowest[1]][1]
            game_speed = lowest[0]

    true_scroll[0] += (scroll_target[0] - display.get_width() /
                       2 - true_scroll[0]) / 10 * dtf(dt)
    true_scroll[1] += (scroll_target[1] - display.get_height() /
                       2 - true_scroll[1]) / 10 * dtf(dt)

    mx, my = pygame.mouse.get_pos()
    mx = int(mx / 3)
    my = int(my / 3)

    camera_sources = []

    cores_left = 0

    for entity in entities:
        if entity[0].type == 'core':
            cores_left += 1
    if (cores_left == 0) and (win == 0):
        win = 1

    # Render Tiles ------------------------------------------- #
    vertical_cycle = round((scroll[1] / 20) / map_height - 0.5, 0)
    top_tiles = []
    collision_tiles = []
    for tile in tile_map:

        if tile_map[tile][0] in top_tile_list:
            top_tiles.append(tile_map[tile][1])
        tile_x = tile_map[tile][1][0]
        tile_y = tile_map[tile][1][1]
        tile_y += vertical_cycle * map_height
        if tile_y < int(scroll[1] / 20 - 1):
            tile_y += map_height
        if tile_map[tile][0] < 13:
            collision_tiles.append(pygame.Rect(
                tile_x * 20, tile_y * 20, 20, 20))

        if tile_map[tile][0] == 13:
            display.blit(tileset_images[tile_map[tile][0]],
                         (tile_x * 20 - scroll[0], tile_y * 20 - scroll[1] + 3))
        else:
            display.blit(tileset_images[tile_map[tile][0]],
                         (tile_x * 20 - scroll[0], tile_y * 20 - scroll[1]))

    # Entities ----------------------------------------------- #
    for i, entity in sorted(list(enumerate(entities)), reverse=True):

        new_y = entity[0].original_y
        new_y += vertical_cycle * (map_height*20)

        if new_y < int(scroll[1] - 20):
            new_y += (map_height * 20)
        entity[0].set_pos(entity[0].x, new_y)
        entity[0].change_frame(1)
        if entity[0].type == 'turret':
            projectile_speed = 2
            player_dis = player.get_distance(entity[0].get_center())
            time_dis = player_dis / projectile_speed
            player_target_pos = [player.get_center(
            )[0] + time_dis * last_movement[0], player.get_center()[1] + time_dis * last_movement[1]]
            angle = entity[0].get_point_angle(player_target_pos)
            entity[2] += ((((math.degrees(angle) - entity[2]) + 180) %
                          360) - 180) / 20 * dtf(dt) * game_speed
            entity[3] += game_speed * dtf(dt)

            if entity[3] > 20:
                if moved:
                    if int(player_dis) <= 200:
                        if shoot_s_cooldown == 0:
                            turret_shot_s.play()
                        if int(player_dis) > 150:
                            shoot_s_cooldown = 20
                        shoot_s_coolsdown = 10
                        entity[3] = 0
                        rot = math.radians(
                            entity[2] + random.randint(0, 20) - 10)
                        bullets.append(['turret', [entity[0].get_center()[0] + math.cos(rot) * 10,
                                                   entity[0].get_center()[1] + 10 + math.sin(rot) * 10], rot, projectile_speed])
                        for i2 in range(3):
                            rot_offset = random.randint(0, 50) - 25

            e.blit_center(display, pygame.transform.rotate(turret_barrel_img, -entity[2]), [
                          entity[0].get_center()[0] - scroll[0], entity[0].get_center()[1] - scroll[1] + 10])

        if (entity[0].type == 'core') and (entity[0].animation_frame > 40):
            if entity[0].animation_frame == 41:
                for i2 in range(5):
                    rot = math.radians(-random.randint(20, 160))
                    speed = random.randint(1, 3)
                    particles.append(e.particle(entity[0].x + random.randint(0, entity[0].size_x), entity[0].y + 3, 'p', [
                                     math.cos(rot) * speed, math.sin(rot) * speed], 0.07, random.randint(20, 35) / 10, (255, 25, 10)))

        entity[0].display(display, [scroll[0], scroll[1]])
        if entity[0].type == 'core':
            glow_size[0] -= 0.1
            if glow_size[0] <= 15:
                glow_size[0] = 20
            glow((entity[0].get_center()[0] - 22, entity[0].get_center()[1] - 20),
                 display, scroll, glow_size[0], (20, 0, 15))
            glow((entity[0].get_center()[0] - 22, entity[0].get_center()[1] - 20),
                 display, scroll, glow_size[0] - 5, (20, 0, 15))

        if entity[1]:
            if entity[0].type == 'core':

                for i2 in range(30):
                    rot = math.radians(-random.randint(20, 160))
                    speed = random.randint(3, 6)
                    particles.append(e.particle(entity[0].x + random.randint(0, entity[0].size_x), entity[0].y + 3, 'p', [
                                     math.cos(rot) * speed, math.sin(rot) * speed], 0.04, random.randint(20, 35) / 10, (255, 25, 10)))
            if entity[0].type == 'turret':
                for i2 in range(40):
                    rot = math.radians(-random.randint(20, 160))
                    speed = random.randint(2, 4)
                    particles.append(e.particle(entity[0].x + random.randint(0, entity[0].size_x), entity[0].y + random.randint(
                        0, entity[0].size_y), 'p', [math.cos(rot) * speed, math.sin(rot) * speed], 0.03, random.randint(10, 35) / 10, (255, 25, 10)))
            entities.pop(i)

    # Player ------------------------------------------------- #
    player_movement = [0, 0]
    player_grav += 0.3 * dtf(dt) * game_speed
   
   
    player_grav = min(3, player_grav)
    player.change_frame(1)
    player_movement[1] = player_grav * game_speed * dtf(dt)
    
    if right:
        moved = True
        player_movement[0] += player_speed * dtf(dt) * game_speed
      
        
    if left:
        moved = True
        player_movement[0] -= player_speed * dtf(dt) * game_speed

    if mx > player.x - scroll[0]:
        player.set_flip(False)
    else:
        player.set_flip(True)
    player_movement[0] += player_velocity[0] * dtf(dt) * game_speed
    player_movement[1] += player_velocity[1] * dtf(dt) * game_speed
    player_velocity = [normalize(player_velocity[0], 0.15 * dtf(dt) * game_speed),
                       normalize(player_velocity[1], 0.15 * dtf(dt) * game_speed)]
   
    if player_movement[1] < -6:
        player_movement[1] = -6
    player_movement[0] = cap(player_movement[0], 14)
    player_movement[1] = cap(player_movement[1], 14)
    x = player.x
    y = player.y
    collisions = {'bottom': False,
                  'top': False,
                  'left': False,
                  'right': False}
    if not dead:
        if (player.x > scroll[0]) and (player.x < scroll[0] + display.get_width()) and (player.y > scroll[1]) and (player.y < scroll[1] + display.get_height()):
            collisions = player.move(player_movement, collision_tiles, [])
            
        elif moved == False:
            player.set_pos(spawnpoint[0] + 4, spawnpoint[1] - 17)
    if player.x < limits[0] - (8 * 20):
        player.set_pos(limits[0] - (8 * 20), player.y)
    elif player.x + player.size_x > limits[1] + (8 * 20):
        player.set_pos(limits[1] + (8 * 20) - player.size_x, player.y)
    last_movement = [int(player.x - x), int(player.y - y)]
    if (player_movement[0] != 0) and (player.action == 'idle'):
        player.set_action('run')
    if collisions['bottom']:
        player_grav = 0
        jumps = 2
        air_timer = 0
        if player_movement[0] == 0:
            player.set_action('idle')
        else:
            player.set_action('run')
    else:
        air_timer += 2
        if air_timer > 4:
            if player_grav > 0:
                player.set_action('fall')
            else:
                player.set_action('jump')

   

    if not dead:

        player.display(display, [int(scroll[0]), int(scroll[1])])

    scroll_target = [player.get_center()[0], player.get_center()[1]]

    # Gun ------------------------------------------------#

    if mx > player.x - scroll[0]:
        flip = False
    else:
        flip = True
    rot = -math.degrees(math.atan2(my - (int(player.get_center()
                        [1]) - scroll[1]), mx - (int(player.get_center()[0]) - scroll[0])))

    shoot_timer = max(shoot_timer - 1 * dtf(dt) * game_speed, 0)

    # Click ----------------------------------------------------------------#
    if click and not dead:
        if shoot_timer == 0:
            moved = True
            shoot_s.play()
            shoot_timer = 50
            player_velocity[0] -= math.cos(math.radians(-rot)) * 6
            player_velocity[1] -= math.sin(math.radians(-rot)) * 6
            bullets.append(['player', [player.get_center()[0], player.get_center()[
                           1] + 3], math.radians(-rot + random.randint(0, 12) - 6), 20])
            for i in range(3):
                rot_offset = random.randint(0, 50) - 25
                flashes.append([[player.get_center()[0] + math.cos(math.radians(-rot + rot_offset)) * 4, player.get_center()[1] + math.sin(
                    math.radians(-rot + rot_offset)) * 4], random.randint(10, 30), math.radians(-rot + rot_offset), 8, random.randint(0, 8)])

    # Bullets ----------------------------------------------------------------#
    for i, bullet in sorted(list(enumerate(bullets)), reverse=True):
        bullet[1][0] += math.cos(bullet[2]) * bullet[3] * dtf(dt) * game_speed
        bullet[1][1] += math.sin(bullet[2]) * bullet[3] * dtf(dt) * game_speed
        popped = False
        if bullet[0] == 'turret':
            shot_img = pygame.transform.rotate(
                turret_shot, -math.degrees(bullet[2]))

            e.blit_center(display, shot_img,
                          (bullet[1][0] - scroll[0], bullet[1][1] - scroll[1]))

            glow((bullet[1][0] - 20, bullet[1][1] - 20),
                 display, scroll, glow_size[1], (30, 30, 30))
            glow((bullet[1][0] - 20, bullet[1][1] - 20),
                 display, scroll, glow_size[1] - 1, (30, 30, 30))

            dis = player.get_distance(bullet[1])
            if dis < 24:
                camera_sources.append([(dis + 50) / 150, player.get_center()])
            if player.obj.rect.collidepoint(bullet[1]):
                if not dead and not win:
                    death_s.play()
                    for i2 in range(60):
                        rot = math.radians(random.randint(0, 359))
                        speed = random.randint(3, 6)
                        particles.append(e.particle(player.x + random.randint(0, player.size_x), player.y + random.randint(0, player.size_y), 'p', [math.cos(rot) * speed, math.sin(
                            rot) * speed], 0.03, random.randint(10, 35) / 10, random.choice([(255, 255, 255), (49, 89, 134), (49, 89, 134), (49, 89, 134), (141, 137, 163)])))

                    dead = True

        if bullet[0] == 'player':  # type, pos, angle, speed
            dis = int(bullet[3] * dtf(dt) * game_speed) + 1

            for i2 in range(dis):
                pos = [int((bullet[1][0] - math.cos(bullet[2]) * (dis - i2)) / 20),
                       int((bullet[1][1] - math.sin(bullet[2]) * (dis - i2)) / 20) % map_height]
                if xy2str(pos) in tile_map:
                    if tile_map[xy2str(pos)][0] < 14:
                        for i3 in range(12):
                            rot = random.randint(0, 359)
                            speed = random.randint(3, 6)
                            size = random.randint(3, 5)
                            pos2 = [bullet[1][0] - math.cos(bullet[2]) * (
                                dis - i2), bullet[1][1] - math.sin(bullet[2]) * (dis - i2)]
                            bullet_v = [
                                math.cos(bullet[2]) * bullet[3] / 6, math.sin(bullet[2]) * bullet[3] / 6]
                            explosion_particles.append(['core', pos2.copy(), [math.cos(math.radians(
                                rot)) * speed - bullet_v[0], math.sin(math.radians(rot)) * speed + bullet_v[1]], size, [0, size * 10]])
                            flashes.append([[bullet[1][0] + math.cos(math.radians(rot)) * 4, bullet[1][1] + math.sin(
                                math.radians(rot)) * 4], random.randint(20, 40), math.radians(rot), 30, random.randint(0, 8)])
                        bullets.pop(i)
                        popped = True
                        explosion_s.play()
                        break
            for entity in entities:
                if entity[0].type in ['core', 'turret']:
                    dis = entity[0].get_distance(bullet[1])
                    if dis < 64:
                        camera_sources.append([(dis + 50) / 1000, bullet[1]])
                    if popped:
                        if dis < 24:
                            entity[1] = True

            if not popped:

                pygame.draw.line(display, (255, 255, 255), (bullet[1][0] - scroll[0], bullet[1][1] - scroll[1]), (
                    bullet[1][0] + math.cos(bullet[2]) * 6 - scroll[0], bullet[1][1] + math.sin(bullet[2]) * 6 - scroll[1]), 2)
                glow_size[1] -= 0.01
                if glow_size[1] <= 3:
                    glow_size[1] = 9
                glow((bullet[1][0] - 20, bullet[1][1] - 20),
                     display, scroll, glow_size[1], (30, 30, 30))
        if not popped:
            if (abs(bullet[1][0] - player.get_center()[0]) > 300) or (abs(bullet[1][1] - player.get_center()[1]) > 300):
                bullets.pop(i)

     # Explosion Particles ------------------------------------ #
    # type, pos, velocity, size, [timer, duration]
    for i, explosion_particle in sorted(list(enumerate(explosion_particles)), reverse=True):
        if explosion_particle[0] == '3rd':
            size = (explosion_particle[4][1] - explosion_particle[4]
                    [0]) / explosion_particle[4][1] * explosion_particle[3]
            if explosion_particle[4][0] > 2:
                pygame.draw.circle(display, (141, 137, 163), (
                    explosion_particle[1][0] - scroll[0], explosion_particle[1][1] - scroll[1]), size)
        if explosion_particle[0] == 'core':
            explosion_particle[1][0] += explosion_particle[2][0] * \
                dtf(dt) * game_speed
            pos = [int(explosion_particle[1][0] / 20),
                   int(explosion_particle[1][1] / 20) % map_height]
            # if the position is close to the tile, the velocity slow down, changing the velocity x and the pos.x
            if (xy2str(pos) in tile_map) and (tile_map[xy2str(pos)][0] < 14):
                explosion_particle[2][0] = -explosion_particle[2][0] * 0.7
                explosion_particle[1][0] += explosion_particle[2][0] * \
                    dtf(dt) * game_speed * 3
            explosion_particle[1][1] += explosion_particle[2][1] * \
                dtf(dt) * game_speed
            pos = [int(explosion_particle[1][0] / 20),
                   int(explosion_particle[1][1] / 20) % map_height]
            # if the position is close to the tile, the velocity slow down, changing the velocity x and the pos.y
            if (xy2str(pos) in tile_map) and (tile_map[xy2str(pos)][0] < 14):
                explosion_particle[2][1] = -explosion_particle[2][1] * 0.7
                explosion_particle[1][1] += explosion_particle[2][1] * \
                    dtf(dt) * game_speed * 3
            explosion_particle[2][1] += 0.3 * dtf(dt) * game_speed
            explosion_particle[2][1] = min(explosion_particle[2][1], 5)
            size = (explosion_particle[4][1] - explosion_particle[4][0]) / 10
            pygame.draw.circle(display, (255, 255, 255), (
                explosion_particle[1][0] - scroll[0], explosion_particle[1][1] - scroll[1]), size)
            if random.randint(1, 2) == 1:
                explosion_particles.append(
                    ['3rd', explosion_particle[1].copy(), [0, 0], size + 1,  [0, 20]])
            if explosion_particle[4][0] < 12:
                if random.randint(1, 3) == 1:
                    explosion_particles.append(['2nd', explosion_particle[1].copy(), [(random.randint(
                        0, 20) / 10 - 1), 0], random.randint(8, 20), [0, (30 + random.randint(0, 10) - explosion_particle[4][0] * 2.5 + 2)]])
        if explosion_particle[0] == '2nd':
            explosion_particle[2][1] -= 0.2 * dtf(dt) * game_speed
            explosion_particle[2][1] = max(
                explosion_particle[2][1], -2 * (size / 8))
            explosion_particle[1][1] += explosion_particle[2][1]
            explosion_particle[1][0] += explosion_particle[2][0]
            if explosion_particle[4][0] < 4:
                size = explosion_particle[3] * (explosion_particle[4][0] / 4)
            else:
                size = explosion_particle[3] * (
                    (explosion_particle[4][1] - explosion_particle[4][0]) / explosion_particle[4][1])
            if explosion_particle[4][0] > 20:
                explosion_particle[4][0] -= dtf(dt) * game_speed * 0.5
            color_offset = (
                explosion_particle[4][0] / explosion_particle[4][1]) * 30 * (1 + explosion_particle[3] / 8)
            pygame.draw.circle(display, (255 - color_offset * 1.1, 255 - color_offset * 1.2, 255 - color_offset),
                               (explosion_particle[1][0] - scroll[0], explosion_particle[1][1] - scroll[1]), size)
        explosion_particle[4][0] += dtf(dt) * game_speed
        if explosion_particle[4][0] >= explosion_particle[4][1]:
            explosion_particles.pop(i)

    # Other Particles ---------------------------------------- #

    for i, particle in sorted(list(enumerate(particles)), reverse=True):
        if particle.physics:
            particle.motion[1] += 0.3 * dtf(dt) * game_speed
            particle.motion[1] = min(particle.motion[1], 5)
            particle.x += particle.motion[0] * dtf(dt) * game_speed
            pos = [int(particle.x / 20), int(particle.y / 20) % map_height]
            if (xy2str(pos) in tile_map) and (tile_map[xy2str(pos)][0] < 14):
                particle.motion[0] *= -1 * 0.65
                particle.motion[1] *= 0.95
                particle.x += particle.motion[0] * dtf(dt) * game_speed * 3
            particle.y += particle.motion[1] * dtf(dt) * game_speed
            pos = [int(particle.x / 20), int(particle.y / 20) % map_height]
            if (xy2str(pos) in tile_map) and (tile_map[xy2str(pos)][0] < 14):
                particle.motion[1] *= -1 * 0.65
                particle.motion[0] *= 0.95
                particle.y += particle.motion[1] * dtf(dt) * game_speed * 3
        particle.draw(display, scroll)
        if not particle.update(dtf(dt) * game_speed):
            particles.pop(i)

    # Flashes ------------------------------------------------ #
    # pos, length, angle, speed, timer
    for i, flash in sorted(list(enumerate(flashes)), reverse=True):
        flash[0][0] += math.cos(flash[2]) * flash[3] * dtf(dt) * game_speed
        flash[0][1] += math.sin(flash[2]) * flash[3] * dtf(dt) * game_speed
        length = flash[1] * ((12 - flash[4]) / 12)
        points = [
            [flash[0][0] + math.cos(flash[2]) * length,
             flash[0][1] + math.sin(flash[2]) * length],
            [flash[0][0] + math.cos(flash[2] + math.pi / 2) * length * 0.15,
             flash[0][1] + math.sin(flash[2] + math.pi / 2) * length * 0.15],
            [flash[0][0] - math.cos(flash[2]) * length * 0.3,
             flash[0][1] - math.sin(flash[2]) * length * 0.3],
            [flash[0][0] + math.cos(flash[2] - math.pi / 2) * length * 0.15,
             flash[0][1] + math.sin(flash[2] - math.pi / 2) * length * 0.15],
        ]
        for point in points:
            point[0] -= scroll[0]
            point[1] -= scroll[1]
        pygame.draw.polygon(display, (255, 255, 255), points)
        flash[4] += 1
        if flash[4] >= 12:
            flashes.pop(i)

    # Cursor ------------------------------------------------- #
    e.blit_center(display, cursor_img, (mx, my))

    # Bars --------------------------------------------------- #
    bar_surf = pygame.Surface((display.get_width(), bar_height))
    bar_surf.fill((8, 5, 8))
    display.blit(bar_surf, (0, 0))
    display.blit(bar_surf, (0, display.get_height() - int(bar_height)))

   # UI --------------------------------------------------- #

    if level == 0:
        if not moved:
            controls_timer = (controls_timer + 1) % 50
            if controls_timer <= 42:
                display.blit(
                    controls_1, (player.x - scroll[0] - 17, player.y - scroll[1] - 22))
            else:
                display.blit(
                    controls_2, (player.x - scroll[0] - 17, player.y - scroll[1] - 22))
        text.show_text('shoot', 150 - int(get_text_width('shoot',
                       1) / 2), 35, 1, 9999, font, display)
        display.blit(core_img, (145, 45))
    if level == 1:
        text.show_text('shoot    avoid', 150 - int(get_text_width(
            'shoot    avoid', 1) / 2), 45, 1, 9999, font, display)
        display.blit(turret_img, (122, 57))
        display.blit(turret_shot, (163, 57))

    display.blit(core_img, (8, 20))
    text.show_text(str(total_cores - cores_left) + '/' +
                   str(total_cores), 30, 25, 1, 9999, font, display)
    text.show_text(f'level: {level}', 10, 10, 1, 9999, font, display)
    if dead:
        text.show_text('click to restart', 150 - int(get_text_width(
            'click to restart', 1) / 2), 97, 1, 9999, font, display)
        if click:
            dead = False
            tile_map, entities, map_height, spawnpoint, total_cores, limits = load_level(
                level)
            player = e.entity(
                spawnpoint[0]+4, spawnpoint[1] - 17, 18, 27, 'player')
            player.set_offset([-3, -2])
            bullets = []
            explosion_particles = []
            particles = []
            flashes = []
            scroll_target = [player.get_center()[0], player.get_center()[1]]
            scroll = scroll_target.copy()
            true_scroll = scroll.copy()
            win = 0
            moved = False
            left = False
            right = False
            player_velocity = [0, 0]
    text.show_text(str(current_fps) + 'fps', display.get_width() - 40,
                   display.get_height() - 20, 1, 9999, font, display, 1)
    # Buttons ------------------------------------------------ #
    click = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_d:
                right = True
            if event.key == K_a:
                left = True
            if event.key == K_w:
                if jumps > 0:
                    moved = True
                    jumps -= 1
                    player_grav = -5
                    player.set_action('jump')
                    particles.append(e.particle(
                        player.x, player.y + player.size_y, 'b', [-1, 3], 0.5, 2, (255, 255, 255), False))
                    particles.append(e.particle(player.x + player.size_x, player.y +
                                     player.size_y, 'b', [1, 3], 0.5, 2, (255, 255, 255), False))
                    jump_s.play()
            if event.key == K_SPACE:
                if jumps > 0:
                    moved = True
                    jumps -= 1
                    player_grav = -5
                    player.set_action('jump')
                    jump_s.play()

        if event.type == KEYUP:
            if event.key == K_d:
                right = False
            if event.key == K_a:
                left = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

    
    



    # Background Effect -------------------------------------- #

    screen.blit(pygame.transform.scale(
        display, (window_size[0], window_size[1])), (0, 0))

    pygame.display.update()
    current_fps = int(fps.get_framerate())
    mainClock.tick(60)
