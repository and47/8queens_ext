from functools import wraps
from typing import List, Callable
from board import Board


def solve(board: Board, start_one_quadrant: bool = True, deadend_cache: bool = True, hashedkeys: bool = True,
          hash_solutions: bool = True, autovar: bool = True, use_np_board: bool = False) -> None:
    """
    Computes recursively all solutions, and, for performance, by default will return their hashes. See params.

    :param board: board with coordinates, pieces move rules, and available pieces
    :param start_one_quadrant: on initial (not recursive) search, skip 3/4 quadrants
    :param deadend_cache: cache situations that lead to 0 ("no solutions") not to recompute same recursive sub-puzzles
    :param hashedkeys: use hashes for deadends cache, optimizing its used memory
    :param hash_solutions: hashes solutions (making them unreadable later to user), ok when only need number of solutions,
     further optimizes memory
    :param autovar: upon finding a solution, add its rotation and reflections to the output. automatic variants.
     further optimization. also, ensures all solutions (variations) are found when using other optimizations or a bug?
    :param use_np_board: use numpy's board operations (currently only rotation and reflections). DISABLED, TO-DO!
        also uses Numpy for solutions (incomplete, only converting to numpy didn't yield performance, and proper
        solution with whole code was abandoned due to time constraints)

    To-do: accept and consistently use user's hash function.

    :return: set of distinct solutions (unique and reflections/rotations)
    """
    m, n = board.dims
    transform_ops = (board.rotate,  # ugly work-around using bound methods due to introduced coupling
                     board.flip_horizontally, board.flip_vertically)

    #chess['empty'] = 1  # no piece (nothing in the square), infinite (1 not going to be decremented);
    # instead, already captured by an outer for loop in recourse_squares, but can be used in alt implementation?

    top_level = start_one_quadrant
    EMPTY = frozenset({None})  # const.  below two are control flags:

    OPTIMIZE = autovar if 'pawn' not in board.pieces and (m+n) > 4 else False  # without rotation or caching, unoptimized. To-do: (m+n) > 4 check for edge cases not needed?
    if use_np_board:  # this does not speed up run on with my code, and is disabled, please ignore related code left 'as is'
        board.switch_to_numpy()

    # decorator ignores first argument, which carries current solution, applied conditionally below based on flag
    # @cache_nosolutions_inputs(use_hash=hashedkeys, transform_ops = transform_ops if OPTIMIZE, use_numpy=use_np_board, NO_RESULT=EMPTY)
    def recourse_squares(current_solution: List, remained_coords: frozenset, filled_coords: frozenset, **pieces) -> frozenset:
        nonlocal top_level
        # print(f'left: {remained_coords}')  # proper logging can be added later
        # print(f'filled: {filled_coords}')
        # print(f'filled: {current_solution}')
        n_pieces = sum(pieces.values())
        if n_pieces == 0:
            # print(current_solution)
            sol = frozenset(current_solution)
            if OPTIMIZE:  # once a solution is complete, get its variations:
                sols = board.all_rots_reflects(sol)  # also make them immutable and hashable
                if hash_solutions:
                    sols = {hash(asol) for asol in sols}  # track all uniques complete ones, and in memory-conscious way
                    # print(sols)
                return frozenset(sols)
            else:  # even without caching, can't use mutables in a set tracking distinct
                return frozenset([hash(sol)]) if hash_solutions else frozenset([sol])

        for coord in remained_coords:
            if not top_level or (coord[0] > m/2 and coord[1] > n/2):  # no need to do initial search in 3 of the 4 quadrants
                new_filled_coords = frozenset((*filled_coords, coord))
                for piece in pieces:
                    if pieces[piece] == 0 or \
                            not filled_coords.isdisjoint(threatened_squares := board.threatened(coord, piece)):
                        continue  # take another piece if none left or this one threatens existing ones on the board
                    new_remained_coords = remained_coords - new_filled_coords - threatened_squares  # best if were maintained by the `board`
                    if len(new_remained_coords) < n_pieces - 1:
                        continue
                    new_pieces = pieces.copy()
                    new_pieces[piece] -= 1
                    current_solution.append(coord + (piece,))
                    # print(f'picked piece {piece} for {coord}')
                    top_level = False  # in recursion: do search in all quadrants
                    board.add_solutions(  # prunes not yet visited but threatened squares:
                        recourse_squares(current_solution, new_remained_coords, new_filled_coords, **new_pieces)
                    )
                    current_solution.pop()  # backtrack
        # print('no solution')
        return EMPTY

    if deadend_cache:
        recourse_squares = cache_nosolutions_inputs(recourse_squares, use_hash=hashedkeys, transform_ops=transform_ops)

    # recourse_squares(current_solution=[], ... # [] is ignored in caching of inputs
    recourse_squares([], remained_coords=frozenset(board.coordinates), filled_coords=frozenset(), **board.pieces)
    # better to use a set for board.coordinates e.g. for diff ops, but sorted = intuitive; left const in recursion

    # print(f'Cache hits: {recourse_squares.cache_hits}')
    return None


# hoped that myhash would reduce collision risk, but it does not. also, slows
def myhash(fset1: frozenset, fset2: frozenset, *ints) -> int:
    a = hash(fset1) * hash(fset2) + max(*ints)
    return a * ((sum(*ints) << 13 ^ (len(fset2) + 3)) % (321892343278 * len(*ints)))


# custom cache decorator, only memoizes when no solutions found. also, it ignores 1st arg, which carries "current solution"
def cache_nosolutions_inputs(func: Callable, use_hash: bool = True, transform_ops: tuple = tuple(),
                             use_numpy: bool = False, NO_RESULT = frozenset({None})) -> Callable:
    """
    Unfortunately, this quick implementation is coupled (to chessboard rotation/reflection) in the interest of time,
    not meant that way. To-do: make more generic. :param use_numpy: is not used
    """
    mycache = set()  # to simply store (hashed) relevant function args that lead to "0 solutions", not to recompute
    # order = [*inspect.signature(func).parameters.keys()]  # expected order of arg names
    # first_arg_name = [*inspect.signature(func).parameters.keys()][0]  # unused, 'nice-to-have'/usability

    @wraps(func)  # to keep metadata for user's or IDE introspection
    def wrapper(*args, **kwargs):
        args_without_first = args[1:] if args else ()  # removing the first argument from args (should be done only if first_arg_name not present in kwargs)
        # kwargs = {k: kwargs.get(key, None) for k in order if k in kwargs} # need to order kwargs in case users provided own order, not used
        # kwargs_without_first = {k: v for k, v in kwargs.items() if k != first_arg_name}  # I'm not using first arg as keyword-arg, no ext users

        # create a hashed cache key based on the remaining args (and kwargs, to-do), i.e. determining inputs
        inps = (*args_without_first, *kwargs.values())  # use kwargs_without_first here in Prod

        # return empty if inputs cached previously (original or rotation/reflections)
        # if use_numpy:  # previous implementation, wasn't performant, commented out during refactoring
        #     from unused_for_numpy_sol import set_coord_tupls_to_np, get_np_keys
        #     remcoords = set_coord_tupls_to_np(inps[0])
        #     filcoords = set_coord_tupls_to_np(inps[1])
        #     pcs = inps[2:]
        #     np_key = (remcoords.tobytes(), filcoords.tobytes(), *pcs)
        #     if np_key in mycache:
        #         cache_hits += 1
        #         return NO_RESULT
        # else:
        inpsk = inps  # inputs as key
        if use_hash:
            inpsk = myhash(inps[0], inps[1], inps[2:])  # hashed inputs
        if inpsk in mycache:
            wrapper.cache_hits += 1
            return NO_RESULT

        # call the expensive function for new inputs (remaining coords and pieces, filled coords)
        result = func(*args, **kwargs)

        # cache the inputs (and rotation/reflections) if the output is 0 solutions
        if result == NO_RESULT:
            # if use_numpy:  # previous implementation, wasn't performant, commented out during refactoring
            #     inps_vnts = get_np_keys(np_key, remcoords, filcoords, m, n, pcs)
            # else:
            inps_vnts = [inpsk]  # hashed/original 1 key and now optimizations (rotation/reflections variants):
            remcoords, filcoords, *pcs = inps
            vnts = [(f(remcoords), f(filcoords), *pcs) for f in transform_ops]
            if use_hash:  # to reduce size of cache, use int (hash) instead of objs from original inputs
                vnts = [myhash(remcoords, filcoords, pcs) for remcoords, filcoords, *pcs in vnts]
            inps_vnts.extend(vnts)  # rotation/reflections of args 2 and 3 (remaining & filled coordinates), rest of the input (pieces, at least one more)
            mycache.update(inps_vnts)  # all inputs variants (or only original) cached (possibly in hashed form)

        return result
    wrapper.cache_hits = 0  # counter to track use of cache for debugging or later proper logging.
    return wrapper
