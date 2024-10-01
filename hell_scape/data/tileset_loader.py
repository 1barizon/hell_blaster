import pygame


def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


def load_tileset(path):
    tileset_img = pygame.image.load(path + 'tile_set_0.png')
    tileset_img.set_colorkey((0, 0, 0))
    width = tileset_img.get_width()

    tile_size = [20, 20]
    tile_count = int((width + 1) / (tile_size[0] + 1))

    images = [clip(tileset_img, i * (tile_size[0] + 1), 0,
                   tile_size[0], tile_size[1])
              for i in range(tile_count)]
    return images
