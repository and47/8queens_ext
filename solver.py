from functools import partial
from typing import Callable

from board import ChessBoard
from resources import MySet, cache_nosolutions_inputs


class Puzzle:

    def __init__(self, w: int, h: int, optimizations: Callable | bool | None = None, **pieces):
        pieces = {k.rstrip('s').lower(): v for k, v in pieces.items()}  # plural args simplified
        self.item_names, self.item_counts = list(pieces.keys()), list(pieces.values())
        self.item_ids = range(len(self.item_counts))
        self.board = ChessBoard(w=w, h=h)
        if optimizations is False:
            self.nosolution_cache = set()
            self.solutions = set()
        elif optimizations is None:  # default
            optimizations = partial(Puzzle.default_decode_encode, transformations=self.board.rotations_reflections)
        if optimizations:  # default or custom ones
            self.optimizations = optimizations  # self.optimizations is not used - included in obj for tracking/history
            self.nosolution_cache = MySet(optimizations=optimizations)                                # ...or extension
            self.solutions = MySet(optimizations=optimizations)

    @staticmethod
    def default_decode_encode(transformations: Callable, solution: set[tuple[tuple[int, int], int]]) -> frozenset:
        """Decodes one, then encodes repeated (transformed) solutions. Is static to support dependency injection of
         custom decoder and optimizations (transformations), which is harder if relied on 'self'. Interface. """
        coords = tuple((c for c, i in solution))
        items = [i for c, i in solution]
        for transformation in transformations(coords):
            yield frozenset(zip(transformation, items))

    def get_solutions(self):
        if hasattr(self.solutions, 'data'):
            if self.solutions.hash:
                return self.solutions.data - {hash(frozenset())}  # own set with optimizations, without empty solution
            return self.solutions.data - {frozenset()}  # own set with optimizations, subtracting empty solution
        return self.solutions - {frozenset()}  # subtract empty solution

    def run_solver(self, hashing: bool = True):
        if hashing:
            self.nosolution_cache.hash = self.solutions.hash = True

        @cache_nosolutions_inputs(cache=self.nosolution_cache, values=self.solutions)
        def solve(asolution, filled, coordinates, vnts):
            if any(vnts):
                for c in (coordinates - filled):
                    for i in self.item_ids:
                        if not vnts[i]:
                            continue
                        restriction = self.board.threatens(piece_coord=c, piece_name=self.item_names[i])
                        if not filled.isdisjoint(restriction):
                            continue
                        restriction = coordinates.intersection(restriction)
                        vnts[i] -= 1
                        if (len(coordinates) - len(restriction)) < sum(vnts):
                            vnts[i] += 1
                            continue
                        coordinates.difference_update(restriction)
                        ci = (c, i)
                        asolution.add(ci)
                        filled.add(c)
                        self.solutions.add(solve(asolution, filled, coordinates, vnts))
                        vnts[i] += 1
                        asolution.remove(ci)
                        filled.remove(c)
                        coordinates.update(restriction)
                return frozenset()
            else:
                return frozenset(asolution)

        self.solutions.add(solve(set(), set(), self.board.coords.copy(), self.item_counts.copy()))
        if hasattr(solve, 'cache_hits'): print(f'Cache hits: {solve.cache_hits}')

    def count_layouts(self):
        return len(self.get_solutions())
