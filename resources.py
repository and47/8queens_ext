from itertools import product


# can also define a class for a coord (x, y) and "placement": (coord, piece)
def chess_threats(piece_coord: tuple, piece: str, all_coords: tuple) -> set:
    # can validate e.g. piece names according to these "classic" rules (moves)
    if piece not in VALID_PIECES:
        raise ValueError("invalid piece")
    under_threat = set()
    if piece in ('king', 'knight'):  # try to use match/case statements instead of ifs
        under_threat.update(
            _possible_moves(piece, piece_coord, all_coords)
        )
    if piece in ('bishop', 'queen'):
        under_threat.update(
            _bishop_moves(piece_coord, all_coords)
        )
    if piece in ('rook', 'queen'):
        under_threat.update(
            _rook_moves(piece_coord, all_coords)
        )
    return under_threat


# Internal functions for classic Chess piece moves and threatened squares + auxiliary data #
# Knight:
# { (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)}
knight_movement = [-1, 1, -2, 2]
knight_moves = product(knight_movement, repeat=2)
knight_moves = {i for i in knight_moves if abs(i[0]) != abs(i[1])}
# King:
# {(0, 1), (-1, -1), (-1, 1), (1, 1), (1, -1), (-1, 0), (1, 0), (0, -1)}
king_movement = [-1, 1, 0]
king_moves = set(product(king_movement, repeat=2)) - {(0, 0)}

LIMITED_MOVES = {'knight': knight_moves, 'king': king_moves}

VALID_PIECES = ('knight', 'king', 'bishop', 'queen', 'rook')

def _possible_moves(piece: str, piece_coord: tuple, all_coords: tuple) -> set:
    new_coords = {(piece_coord[0] + move[0], piece_coord[1] + move[1]) for move in LIMITED_MOVES[piece]}
    return new_coords.intersection(all_coords)  # limits by chessboard N x M


# assumes sorted all_coords as above, tested
def _bishop_moves(coord: tuple, all_coords: tuple) -> set:
    size = min(all_coords[-1])  # diagonal size is the minimum of (N, M) on N x M chessboard
    new_coords = {(x + coord[0], y + coord[1]) for i in range(-size, size + 1) if i != 0  # 0-move skipping not really needed
                  for x, y in [(i, i), (-i, -i), (i, -i), (-i, i)]}
    return new_coords.intersection(all_coords)  # limits by chessboard N x M


def _rook_moves(coord: tuple, all_coords: tuple) -> set:
    new_coords = {i for i in all_coords if i[0] == coord[0]}  # same x...
    new_coords.update({i for i in all_coords if i[1] == coord[1]})  # ...or y coordinate
    return new_coords - {coord}  # skip "not moving", not needed


