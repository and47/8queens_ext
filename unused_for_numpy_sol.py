# not used

import numpy as np
from typing import List

# def rotate_90(coordinates, m, n) -> np.ndarray:
#     return (coordinates * np.array((-1, 1)) + np.array((m+1, 0)))[:,[1, 0]]

# dashboard coordinates (x, y) start from bottom-left indexed (1,1). see board.py
def rotate_180(coordinates, m, n) -> np.ndarray:
    return coordinates * np.array((-1, -1)) + np.array((m+1, n+1))


# def rotate_270(coordinates, m, n) -> np.ndarray:
#     return (coordinates * np.array((1, -1)) + np.array((0, n+1)))[:,[1, 0]]


def reflect_vertically(coordinates, _, n) -> np.ndarray:
    return coordinates * np.array((1, -1)) + np.array((0, n+1))

def reflect_horizontally(coordinates, m, _) -> np.ndarray:
    return coordinates * np.array((-1, 1)) + np.array((m+1, 0))


# sort as alternative to using sets for caching:
def sort_np_coords(coords: np.ndarray) -> np.ndarray:
    return coords[np.lexsort((coords[:, 1], coords[:, 0]))]


def hash_np(coords: np.ndarray) -> bytes:
    return sort_np_coords(coords).tobytes()


def set_coord_tupls_to_np(set_coords: set) -> np.ndarray:
    coords_arr = np.fromiter(set_coords, dtype=np.dtype((int, 2)))  # or np.array(list(key[0]), dtype='int')
    return sort_np_coords(coords_arr)


# remaining coordinates, filled coordinates, and counts of chess pieces are used as cache keys:
def get_np_keys(np_key: tuple, remcoords: np.ndarray, filcoords: np.ndarray, m: int, n: int, pcs: List,
                hash_f=hash_np) -> tuple:
    return (
      np_key,
     # (hash_np(rotate_90(remcoords, m, n)), hash_np(rotate_90(filcoords, m, n)), *pcs),
     (hash_f(rotate_180(remcoords, m, n)), hash_f(rotate_180(filcoords, m, n)), *pcs),
     # (hash_f(rotate_270(remcoords, m, n)), hash_f(rotate_270(filcoords, m, n)), *pcs),
     (hash_f(reflect_vertically(remcoords, m, n)), hash_f(reflect_vertically(filcoords, m, n)), *pcs),
     (hash_f(reflect_horizontally(remcoords, m, n)), hash_f(reflect_horizontally(filcoords, m, n)), *pcs))
