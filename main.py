from board import Board
from solver import solve


if __name__ == "__main__":
    test1 = Board(3, 3, kings=2, rooks=1)
    solve(test1)
    test2 = Board(4, 4, rooks=2, knights=4)
    solve(test2)
    test3 = Board(7, 7, queens=7)
    solve(test3)
    assert test1.count_layouts() == 4
    assert test2.count_layouts() == 8
    assert test3.count_layouts() == 40

    from time import time

    # task = Board(6, 9, kings=2, queens=1, bishops=1, rooks=1, knights=1)
    task = Board(6, 8, kings=1, queens=1, bishops=1, rooks=1, knights=1)
    start_t = time()
    solve(task)  # 20136752 solutions. Took 30 mins, 3-4Gb RAM on a laptop
    ans = task.count_layouts()
    end_t = time()
    print(f'{ans} solutions. Took {end_t - start_t} sec.')
