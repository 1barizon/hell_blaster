import csv
import pygame
import json
ROWS = 30
MAX_COLS = 40


game_map = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    game_map.append(r)


tile_map = []


def dict_map(path, level):
    with open(path,  newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                if tile == '-1':
                    pass
                else:
                    tile_map.append((str(y)+';'+str(x), [int(tile), [y, x]]))

    with open(f'data/levels/level_{level}.txt', 'w') as f:
        f.write(str(dict(tile_map)).replace("'", '"'))


dict_map('data/level_0.csv', 0)

