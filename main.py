from solver import Puzzle
from time import time


if __name__ == "__main__":
    test1 = Puzzle(w=3, h=3, kings=2, rooks=1)
    test1.run_solver(hashing=False)  # to see actual solutions not only their int hashes
    # test1.solutions  # print solutions, to-do: add pretty chessboard displayed text output
    test2 = Puzzle(4, 4, rooks=2, knights=4)
    test2.run_solver()
    test3 = Puzzle(7, 7, queens=7)
    test3.run_solver()
    assert test1.count_layouts() == 4
    assert test2.count_layouts() == 8
    assert test3.count_layouts() == 40

    # task = Puzzle(6, 9, kings=2, queens=1, bishops=1, rooks=1, knights=1)  # takes up to 30 mins.
    task = Puzzle(6, 8, kings=1, queens=1, bishops=1, rooks=1, knights=1)  # 1 min.
    start_t = time()
    task.run_solver()
    ans = task.count_layouts()
    end_t = time()
    print(f'{ans} solutions. Took {end_t - start_t} sec.')
