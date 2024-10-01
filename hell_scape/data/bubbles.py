import pygame
import random
from pygame.locals import *

# bubbles flying in the background
bg_bubbles = []
bg_bubble_particles = []


def bubbles(WINDOW_SIZE, display):
    if random.random() < 0.90:
        if random.random() < 0.20:
            bg_bubbles.append([[random.random() * WINDOW_SIZE[0], WINDOW_SIZE[1]],
                               random.random() * 3.5 + 0.25,  random.random() * 6 + 1, random.random() - 0.25])
        else:
            bg_bubbles.append([[random.random() * WINDOW_SIZE[1], 0],
                               random.random() * -3.5 - 0.25,  random.random() * 6 + 1, random.random() - 0.25])

    for i, bubble in sorted(enumerate(bg_bubbles), reverse=True):
        bg_bubble_particles.append(
            [((bubble[0][0] * bubble[3]) % 480, (bubble[0][1])), bubble[2]])
        bubble[0][1] -= bubble[1]
        if (bubble[0][1] < 0) or (bubble[0][1] > 480):
            bg_bubbles.pop(i)

    for i, p in sorted(enumerate(bg_bubble_particles), reverse=True):
        pygame.draw.circle(display, (0, 0, 0), p[0], int(p[1]))
        p[1] -= 0.3
        if p[1] <= 0:
            bg_bubble_particles.pop(i)


def glow_circle(pos, color, size):

    surf = pygame.Surface((60, 60))

    pygame.draw.circle(surf, color, (20, 20), size)
    surf.set_colorkey((0, 0, 0))
    return surf


def glow(pos, display, scroll, size, color):
    display.blit(glow_circle(pos, (color), size),
                 (pos[0]-scroll[0], pos[1]-scroll[1]), special_flags=BLEND_RGBA_ADD)
