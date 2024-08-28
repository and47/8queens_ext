from itertools import product
from functools import partial, cache
from dataclasses import dataclass, field
from enum import Enum, EnumMeta  # Python 3.11+ EnumType not EnumMeta


@dataclass(frozen=True, slots=True)
class ChessBoard:
    # VALID_PIECES: ClassVar[tuple] = ('queen', 'rook', 'bishop', 'king', 'knight')  # add validation to-do?
    w: int
    h: int
    coords: set = field(init=False)
    pieces: 'PieceMoves' = field(init=False)
    threat_cache: dict = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, 'coords', ChessBoard.generate_coords(self.w, self.h))
        object.__setattr__(self, 'pieces', possible_moves_factory(self))

    def threatens(self, piece_coord: tuple, piece_name: str) -> set:
        if (k := (*piece_coord, piece_name)) in self.threat_cache:  # manual cache due to @cache bad with method (self)
            res = self.threat_cache[k]
        else:
            placed_piece = getattr(self.pieces, piece_name)
            res = placed_piece(piece_coord=piece_coord)
            res.add(piece_coord)  # for performance, consider placement square itself as threatened/busy
            self.threat_cache[k] = res
        return res

    @staticmethod  # for cache performance
    @cache
    def rotate_180(coordinates: tuple, w: int, h: int) -> tuple:
        x, y, *meta = coordinates
        return w - x - 1, h - y - 1

    @staticmethod
    @cache
    def reflect_vertically(coordinates: tuple, h: int) -> tuple:
        x, y, *meta = coordinates
        return x, h - y - 1

    @staticmethod
    @cache
    def reflect_horizontally(coordinates: tuple, w: int) -> tuple:
        x, y, *meta = coordinates
        return w - x - 1, y

    def rotations_reflections(self, coords: tuple[tuple]) -> set[tuple[tuple]]:
        rotated = tuple(ChessBoard.rotate_180(xy, self.w, self.h) for xy in coords)
        flipped_v = tuple(ChessBoard.reflect_vertically(xy, self.h) for xy in coords)
        flipped_h = tuple(ChessBoard.reflect_horizontally(xy, self.w) for xy in coords)
        return {rotated, flipped_v, flipped_h}

    @staticmethod
    def generate_coords(w: int, h: int) -> set:
        xs = range(w)
        ys = range(h)
        coords = list(product(xs, ys))
        # coords.sort(key=lambda xy: (xy[1], xy[0]))  # can use to "prioritize" e.g. corners or center
        return set(coords)  # sorted ("human-readable") and hashable

    # Static internal auxiliary data and functions for classic Chess piece moves and finding threatened squares
    king_movement = [-1, 1, 0]  # from (0, 0): to {(0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1), (-1, 0), (1, 0), (0, -1)}
    king_moves = set(product(king_movement, repeat=2)) - {(0, 0)}
    knight_movement = [-1, 1, -2, 2]  # (0, 0): { 2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)}
    knight_moves = product(knight_movement, repeat=2)
    knight_moves = {i for i in knight_moves if abs(i[0]) != abs(i[1])}

    LIMITED_MOVES = {'knight': knight_moves, 'king': king_moves}

    def _possible_lim_moves(self, piece_name: str, piece_coord: tuple) -> set:
        new_coords = {(piece_coord[0] + move[0], piece_coord[1] + move[1])
                      for move in ChessBoard.LIMITED_MOVES[piece_name]}
        return new_coords.intersection(self.coords)  # limits by chessboard N x M

    def _bishop_moves(self, piece_coord: tuple) -> set:
        # diagonal size is the minimum of (N, M) on N x M chessboard:
        size = min(max(self.coords, key=lambda xy: xy[0])[0], max(self.coords, key=lambda xy: xy[1])[1])
        new_coords = {(x + piece_coord[0], y + piece_coord[1]) for i in range(-size, size + 1) if i != 0
                      for x, y in [(i, i), (-i, -i), (i, -i), (-i, i)]}
        return new_coords.intersection(self.coords)  # limits by chessboard N x M

    def _rook_moves(self, piece_coord: tuple) -> set:
        new_coords = {i for i in self.coords if i[0] == piece_coord[0]}  # same x...
        new_coords.update({i for i in self.coords if i[1] == piece_coord[1]})  # ...or y coordinate
        return new_coords - {piece_coord}  # skip "not moving", not needed



def possible_moves_factory(board: ChessBoard) -> EnumMeta:
    class PieceMoves(Enum):
        __slots__ = ()  # Declare __slots__ to avoid __dict__ creation
        king   = partial(board._possible_lim_moves, piece_name='king')
        knight = partial(board._possible_lim_moves, piece_name='knight')
        rook   = board._rook_moves
        bishop = board._bishop_moves

        @classmethod
        def queen(cls, *, piece_coord) -> set[tuple]:
            return cls.rook(piece_coord=piece_coord) | cls.bishop(piece_coord=piece_coord)

        def __call__(self, **kwargs):
            return self.value(**kwargs)  # pre-caution: only allow keyword arguments not to mix in 'partial'

    return PieceMoves
