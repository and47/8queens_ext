from itertools import product
from functools import cache
from typing import Set, Tuple, Optional, Callable

from resources import chess_threats  # will be cached here


class Board:
    """
    Very simplistic setup.  Does not track filled squares or pieces in them.  To-do: should cache threats (see resources.py)
    """
    def __init__(self, m: int, n: int, use_numpy: bool = False, threat_rules: Callable = chess_threats, **pieces):
        self._m, self._n = m, n
        self.solutions = set()
        self._rules = threat_rules
        self._coordinates = Board.generate_coords(m, n)
        self._ops = {'rotate': rotate_180,  # default implementations
                     'flip_vertically': reflect_vertically, 'flip_horizontally': reflect_horizontally}
        if use_numpy:
            self.switch_to_numpy()
        self.pieces = {k.rstrip('s'): v for k, v in pieces.items()}  # simplified

    # def alloc_pieces(self, kings: int = 0, queens: int = 0, knights: int = 0, bishops: int = 0, rooks: int = 0):
        # can add validation of pieces, e.g. check names or limit queens to 2/4 for a chess game

    def add_solutions(self, new_solutions: set):
        # here can do validation, e.g. check that user/solver-added solutions actually contain valid coords and pieces
        self.solutions.update(new_solutions)  # instead only check for empty ones upon return below

    def get_solutions(self) -> set:
        """
        Valid (pieces not threatening each other) layouts - pieces and their coordinates
        :return: all layouts (tuples of coordinates X, Y and name of chess piece or just hashes for optimized
            caching performance)
        """
        self.solutions.discard(None)  # remove empty ("no solutions") as not a valid solution
        # self.solutions.discard(frozenset({None}))  # remove empty ("no solutions") as not a valid solution
        return self.solutions

    def count_layouts(self) -> int:
        return len(self.get_solutions())

    @staticmethod
    def generate_coords(m, n) -> tuple:
        xs = range(1, m + 1)  # can add more dimensions, use numpy
        ys = range(1, n + 1)
        coords = sorted(product(xs, ys), key=lambda x: (x[1], x[0]))
        return tuple(coords)  # "human-readable" sorted tuple (memoization requires this obj to be hashable)

    @property
    def coordinates(self) -> tuple:
        return self._coordinates

    @property
    def dims(self) -> tuple:
        return self._m, self._n

    # this can be pre-computed. instead, similarly, I use memoization. Size of this cache is rather small
    @cache
    def threatened(self, piece_coords: tuple, piece_name: str) -> set:
        # should also e.g. validate coords belong onboard
        squares_under_threat = self._rules(piece_coords, piece_name, self.coordinates)
        return squares_under_threat

    def switch_to_numpy(self):
        from unused_for_numpy_sol import rotate_180, reflect_horizontally, reflect_vertically
        self._ops = {'rotate': rotate_180,
                     'flip_vertically': reflect_vertically, 'flip_horizontally': reflect_horizontally}

    def rotate(self, coords):
        # can validate coords belong onboard
        f = self._ops['rotate']
        return f(coords, *self.dims)

    def flip_vertically(self, coords):
        # can validate coords belong onboard
        f = self._ops['flip_vertically']
        return f(coords, *self.dims)

    def flip_horizontally(self, coords):
        # can validate coords belong onboard
        f = self._ops['flip_horizontally']
        return f(coords, *self.dims)

    # for current solution and allowed rotation and reflections,
    # accepts positions (coordinate X, Y and optionally piece name,
    def all_rots_reflects(self, positions: Set[Tuple[int, int, Optional[str]]]) -> frozenset:
        """
        Get e.g. current solution and allowed rotation and reflections.  Or, for a situation (some filled and remaining
         coordinates) leading to 0 solutions in a specific "game/puzzle" setup, get transformations that'd lead to same
         outcome.
        :param positions:
        :return:
        """
        return frozenset((positions,
                          # rotate_90(positions),
                          self.rotate(positions),
                          # rotate_270(positions),
                          self.flip_vertically(positions),
                          self.flip_horizontally(positions)))





# to optimize - perform dashboards rotations/reflections, used when saving a solution to cache or
# checking if inputs lead to "no solution" and using cache not to call recursive function
# (see unused_for_numpy_sol.py for numpy version):
# dashboard coordinates (x, y) start from bottom-left indexed (1,1)
# def rotate_90(coordinates, m, _) -> frozenset:
#     return frozenset((y, m + 1 - x, *rest) for x, y, *rest in coordinates)

def rotate_180(coordinates, m, n) -> frozenset:
    return frozenset((m + 1 - x, n + 1 - y, *rest) for x, y, *rest in coordinates)

# def rotate_270(coordinates, _, n) -> frozenset:
#     return frozenset((n + 1 - y, x, *rest) for x, y, *rest in coordinates)

def reflect_vertically(coordinates, _, n) -> frozenset:
    return frozenset((x, n - y + 1, *rest) for x, y, *rest in coordinates)

def reflect_horizontally(coordinates, m, _) -> frozenset:
    return frozenset((m + 1 - x, y, *rest) for x, y, *rest in coordinates)
