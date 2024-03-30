# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 18:30:01 2024

@author: Mapmaking Team PyCamp Spain 2024
"""
import os, sys
from PIL import Image
from os import listdir
from os.path import isfile, join

class Tile:
    def __init__(
        self,
        image_list,
        frontier_list,
        special = '',
        rotable = True,
        symmetric = False,
    ):
        self.image_list = image_list
        self.frontier_list = frontier_list
        self.rotable = rotable
        self.symmetric = symmetric
        self.special = special

    def is_compatible_with(self, other_tile, other_position = 'up'):
        if other_position == 'up':
            my_frontier = self.frontier_list[0]
            their_frontier = other_tile.frontier_list[2]
        elif other_position == 'down':
            my_frontier = self.frontier_list[2]
            their_frontier = other_tile.frontier_list[0]
        elif other_position == 'right':
            my_frontier = self.frontier_list[1]
            their_frontier = other_tile.frontier_list[3]
        elif other_position == 'left':
            my_frontier = self.frontier_list[3]
            their_frontier = other_tile.frontier_list[1]
        else:
            raise ValueError(f'invalid value for other position: {other_position}')
        return my_frontier == their_frontier[::-1]
    
 
def frontiers_from_name(fname):
    fname = fname.partition('.')[0]
    frontiers = []
    for ii in range(3):
        _f, _, fname = fname.partition('-')
        frontiers.append(_f)
    if '-' in fname:
        _f, _, special = fname.partition('-')
        frontiers.append(_f)
    else:
        frontiers.append(fname)
        special = ''
    return frontiers, special


def rotate_frontier_list(old_frontier_list):
    new_frontier_list = [_front for _front in old_frontier_list[1:]]
    new_frontier_list.append(old_frontier_list[0])
    return new_frontier_list
def is_simmetric(frontier_list):
    base_string = '-'.join(frontier_list)
    inverse_list = [_f[::-1] for _f in frontier_list[::-1]]
    #print(base_string)
    for ii in range(4):
        inverse_string = '-'.join(inverse_list)
        #print(inverse_string)
        if inverse_string == base_string:
            return True
        inverse_list = rotate_frontier_list(inverse_list)
    return False


def tile_from_file(fname, pathname):
    frontiers, special = frontiers_from_name(fname)
    fpath = join(pathname, fname)
    im = Image.open(fpath)
    if special == '':
        rotable = True
    else:
        rotable = False
        
    newtile = Tile(
        image_list = [im,],
        frontier_list = frontiers,
        special = special,
        rotable = rotable,
        symmetric = False,
    )
    return newtile


def rotate_tile(oldtile):
    old_im_list = oldtile.image_list
    old_frontier_list = oldtile.frontier_list
    new_im_list = [_im.rotate(-90) for _im in old_im_list]
    new_frontier_list = [old_frontier_list[-1]] + [_front for _front in old_frontier_list[:-1]]
    newtile = Tile(
        new_im_list,
        new_frontier_list,
        special = oldtile.special,
        rotable = oldtile.rotable,
        symmetric = oldtile.symmetric,
    )
    return newtile

def flip_tile(oldtile):
    old_im_list = oldtile.image_list
    old_frontier_list = oldtile.frontier_list
    new_im_list = [_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for _im in old_im_list]
    new_frontier_list = [_front[::-1] for _front in old_frontier_list]
    new_frontier_list[1] = old_frontier_list[3][::-1]
    new_frontier_list[3] = old_frontier_list[1][::-1]
    newtile = Tile(
        new_im_list,
        new_frontier_list,
        special = oldtile.special,
        rotable = oldtile.rotable,
        symmetric = oldtile.symmetric,
    )
    return newtile


def create_tile_list(pathname):
    file_list = [f for f in listdir(pathname) if isfile(join(pathname, f))]
    tile_list = []
    for file in file_list:
        new_tile = tile_from_file(file, pathname)
        tile_list.append(new_tile)
        if new_tile.rotable == True:
            for ii in range(3):
                new_tile = rotate_tile(new_tile)
                tile_list.append(new_tile)
        if not is_simmetric(new_tile.frontier_list):
            new_tile = flip_tile(new_tile) 
            tile_list.append(new_tile)
            if new_tile.rotable == True:
                for ii in range(3):
                    new_tile = rotate_tile(new_tile)
                    tile_list.append(new_tile)
    return tile_list


def generate_final_image(image_names: list[list], width: int, height: int):
    final_image = Image.new('RGB', (width * 64, height * 64))
    for x, image_name_row in enumerate(image_names):
        for y, image_name in enumerate(image_name_row):
            image = Image.open(f'tiles/{image_name}')
            final_image.paste(image, (y * 64, x * 64))

    final_image.save('final_image.png', 'JPEG')

if __name__ == '__main__':
    image_names = [
        [
            'a-a-a-a.jpg',
            'a-a-a-a-ballena.jpg',
            'a-a-a-a-barco.jpg',
        ],
        [
            'a-t-a-t-canal.jpg',
            'a-t-a-t-istmo.JPG',
            't-a-a-a.jpg',
        ],
        [
            't-t-a-a.jpg',
            't-t-t-a.jpg',
            't-t-t-t.jpg',
        ],
    ]

    generate_final_image(image_names, 3, 3)