import random
from PIL import Image, ImageOps
import os
import glob

import numpy as np

from datetime import datetime

def print_map(map_: list):
    for idx_columna, columna in enumerate(map_):
        for fila in columna:
            print(" ", fila["a"], fila["b"], " ", end='   ')
        print()
        for fila in columna:
            print(fila["h"], "x", "x", fila["c"], end='   ')
        print()
        for fila in columna:
            print(fila["g"], "x", "x", fila["d"], end='   ')
        print()
        for fila in columna:
            print(" ", fila["f"], fila["e"], " ", end='   ')
        print()
        print()


def tile(overrides: dict[str, str] = {}):
    agua_weight = 4
    tierra_weight = 5
    t = {
        "a": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "b": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "c": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "d": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "e": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "f": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "g": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
        "h": random.choice(["a"] * agua_weight + ["t"] * tierra_weight),
    } | overrides
    path = os.path.exists("tiles/"+tile2filename(t))
    if not path:
        return tile(overrides)
    return t



def empty_tile():
    return {
        "a": "?",
        "b": "?",
        "c": "?",
        "d": "?",
        "e": "?",
        "f": "?",
        "g": "?",
        "h": "?",
    }

def tile2filename(tile):
    top = tile["a"] + tile["b"]
    if len(set(top)) == 1:
        top = top[0]
    right = tile["c"] + tile["d"]
    if len(set(right)) == 1:
        right = right[0]
    bottom = tile["e"] + tile["f"]
    if len(set(bottom)) == 1:
        bottom = bottom[0]
    left = tile["g"] + tile["h"]
    if len(set(left)) == 1:
        left = left[0]
    return '-'.join([top, right, bottom, left]) + ".jpg"


def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def pick_equal_picture(filename):
    r = random.choice(glob.glob(f"tiles/{filename.split('.')[0]}-*") + [filename])
    return r.split("/")[-1]


def generate_final_map(map_):
    img_map = []
    for row in map_:
        img_map_row = []
        for tile in row:
            # img_map_row.append(tile2filename(tile))
            img_map_row.append(pick_equal_picture(tile2filename(tile)))
        img_map.append(img_map_row)
    row_images = []
    for row in img_map:
        row_final = Image.open(os.path.join('tiles/', row[0]))
        for idx, tile in enumerate(row[1:]):
            tile_img = Image.open(os.path.join('tiles/', tile))
            row_final = get_concat_h(row_final, tile_img)
        row_images.append(row_final)
    final = row_images[0]
    for row in row_images[1:]:
        final = get_concat_v(final, row)
    map_name = f"frutimap__{len(map_)}x{len(map_[0])}__{datetime.now().isoformat()}.jpg"
    final.save(map_name)

    print(f"file:///{os.getcwd()}/{map_name}")

def water_tile():
    return {k: "a" for k in "abcdefgh"}

def fruti(l: int):
    map_ = []
    for i in range(l):
        row = []
        for j in range(l):
            row.append(empty_tile())
        map_.append(row)
    water = np.zeros((l, l))
    water[int(l/2), :] = 1
    # water[:, int(l/2)] = 1
    for idx_row, row in enumerate(map_):
        for idx_col, tile in enumerate(row):
            # if water[idx_col, idx_row] == 1:
            #     map_[idx_row][idx_col] = water_tile()
            #     update_tile(map_, idx_row, idx_col-1)
            #     # update_tile(map_, idx_row-1, idx_col)
            # else:
            #     update_tile(map_, idx_row, idx_col)
            update_tile(map_, idx_row, idx_col)
    print_map(map_)
    generate_final_map(map_)


def update_tile(map_, idx_row, idx_col):
    overrides = {}
    # LEFT
    if idx_col - 1 >= 0:
        left = map_[idx_row][idx_col - 1]
        if "?" not in left.values():
            overrides.update({
                "h": left["c"],
                "g": left["d"],
            })
    # RIGHT
    if idx_col+1 < len(map_[idx_row])-1:
        right = map_[idx_row][idx_col+1]
        if "?" not in right.values():
            overrides.update({
                "c": right["h"],
                "d": right["g"],
        })
    # UP
    if idx_row - 1 >= 0:
        up = map_[idx_row-1][idx_col]
        if "?" not in up.values():
            overrides.update({
                "a": up["f"],
                "b": up["e"],
            })
    # DOWN
    if idx_row+1 < len(map_)-1:
        down = map_[idx_row+1][idx_col]
        if "?" not in down.values():
            overrides.update({
                "f": down["a"],
                "e": down["b"],
            })

    map_[idx_row][idx_col] = tile(overrides)
    return map_



def rotate(path:str, filename: str, times: int = 1, ):
    """rotate the images 90 degrees per time"""
    filename = filename.replace(path, "")
    sides = filename.split(".")[0].split('-')[:4]
    for i in range(times):
        sides.insert(0, sides.pop())
    im = Image.open(os.path.join(path, filename))
    im_rotated = im.rotate(-90*times,)
    im_rotated.save(
        os.path.join(
            path, "-".join(sides)+".jpg"
        )
    )

def flip(path:str, filename: str, ):
    filename = filename.replace(path, "")
    sides = filename.split(".")[0].split('-')[:4]
    new = [""] * 4
    new[0], new[2] = sides[2][::-1], sides[0][::-1]
    new[1] = sides[1][::-1]
    new[3] = sides[3][::-1]
    im = Image.open(os.path.join(path, filename))
    im_flip = ImageOps.flip(im)
    im_flip.save(
        os.path.join(
            path, "-".join(new)+".jpg"
        )
    )

def mirror(path:str, filename: str, ):
    filename = filename.replace(path, "")
    sides = filename.split(".")[0].split('-')[:4]
    print(sides)
    new = [
        sides[0][::-1],
        sides[3][::-1],
        sides[2][::-1],
        sides[1][::-1]
    ]
    # new = [""] * 4
    # new[1], new[3] = sides[1][::-1], sides[3][::-1]
    # new[0] = sides[0][::-1]
    # new[2] = sides[2][::-1]
    im = Image.open(os.path.join(path, filename))
    im_flip = ImageOps.mirror(im)
    im_flip.save(
        os.path.join(
            path, "-".join(new)+".jpg"
        )
    )


def generate_rotated_img():
    for jpg_version in ["jpg", "JPG"]:
        for f in glob.glob(f"tiles/*.{jpg_version}"):
            # rotate("tiles/", f)
            # rotate("tiles/", f, times=2)
            # rotate("tiles/", f, times=3)
            # mirror("tiles/", f)
            # flip("tiles/", f)
            pass


if __name__ == "__main__":
    # generate_rotated_img()
    l = 15
    i = 0
    while True:
        i += 1
        try:
            fruti(l)
            break
        except Exception:
            print(f"starting over... {i}", end="\r")
            continue
